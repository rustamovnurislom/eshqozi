from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import time


class Store:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self, write: bool = False):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=15000")
        try:
            if write:
                con.execute("BEGIN IMMEDIATE")
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def migrate(self):
        with self.connection() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("PRAGMA synchronous=FULL")
            con.execute("CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at REAL NOT NULL)")
            version = con.execute("SELECT max(version) FROM schema_migrations").fetchone()[0] or 0
            if version > 1:
                raise RuntimeError("Ma’lumotlar bazasi versiyasi bu koddan yangi")
            if version < 1:
                sql = (Path(__file__).parent / "migrations/001_initial.sql").read_text()
                con.executescript("BEGIN IMMEDIATE;\n" + sql + f"\nINSERT INTO schema_migrations VALUES(1,{time.time()});\nCOMMIT;")

    def user(self, chat_id: int):
        now = time.time()
        with self.connection(write=True) as con:
            con.execute("INSERT OR IGNORE INTO users(chat_id,created_at,updated_at) VALUES(?,?,?)", (chat_id, now, now))
            return dict(con.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,)).fetchone())

    def preference(self, chat_id: int, *, dialect: str | None = None, tone: str | None = None):
        self.user(chat_id)
        with self.connection(write=True) as con:
            if dialect is not None:
                con.execute("UPDATE users SET dialect=?,updated_at=? WHERE chat_id=?", (dialect,time.time(),chat_id))
                con.execute("DELETE FROM turns WHERE chat_id=?", (chat_id,))
            if tone is not None:
                con.execute("UPDATE users SET tone=?,updated_at=? WHERE chat_id=?", (tone,time.time(),chat_id))

    def history(self, chat_id: int, limit: int, retention_hours: int):
        cutoff = time.time() - retention_hours * 3600
        with self.connection() as con:
            rows = con.execute("SELECT question,answer FROM turns WHERE chat_id=? AND created_at>=? ORDER BY created_at DESC,rowid DESC LIMIT ?", (chat_id,cutoff,limit)).fetchall()
        return [dict(row) for row in reversed(rows)]

    def last_sources(self, chat_id: int):
        with self.connection() as con:
            row = con.execute("SELECT sources FROM turns WHERE chat_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1", (chat_id,)).fetchone()
            return json.loads(row[0]) if row else []

    def clear(self, chat_id: int):
        with self.connection(write=True) as con:
            con.execute("DELETE FROM turns WHERE chat_id=?", (chat_id,))

    def forget(self, chat_id: int, current_update: int | None = None):
        with self.connection(write=True) as con:
            con.execute("DELETE FROM users WHERE chat_id=?", (chat_id,))
            con.execute("DELETE FROM usage WHERE chat_id=?", (chat_id,))
            if current_update is None:
                con.execute("DELETE FROM inbox WHERE chat_id=?", (chat_id,))
            else:
                con.execute("DELETE FROM inbox WHERE chat_id=? AND update_id<>?", (chat_id,current_update))

    def feedback(self, chat_id: int, turn_id: str, score: int) -> bool:
        with self.connection(write=True) as con:
            row = con.execute("SELECT 1 FROM turns WHERE id=? AND chat_id=?", (turn_id,chat_id)).fetchone()
            if row is None:
                return False
            con.execute("INSERT INTO feedback VALUES(?,?,?,?) ON CONFLICT(turn_id,chat_id) DO UPDATE SET score=excluded.score", (turn_id,chat_id,score,time.time()))
            return True

    def offset(self) -> int:
        with self.connection() as con:
            row = con.execute("SELECT value FROM metadata WHERE key='telegram_offset'").fetchone()
            return int(row[0]) if row else -1

    def enqueue_batch(self, updates: list[dict]) -> int:
        from .telegram import parse_update
        if not updates:
            return 0
        inserted = 0
        with self.connection(write=True) as con:
            row = con.execute("SELECT value FROM metadata WHERE key='telegram_offset'").fetchone()
            previous = int(row[0]) if row else -1
            latest = previous
            for update in updates:
                uid = update.get("update_id")
                if not isinstance(uid,int) or uid <= previous:
                    continue
                latest = max(latest,uid)
                event = parse_update(update)
                if event is None:
                    continue
                cursor = con.execute("INSERT OR IGNORE INTO inbox(update_id,chat_id,payload,created_at) VALUES(?,?,?,?)", (uid,event['chat_id'],json.dumps(event,ensure_ascii=False),time.time()))
                inserted += cursor.rowcount
            con.execute("INSERT INTO metadata(key,value) VALUES('telegram_offset',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(latest),))
        return inserted

    def claim(self, lease_seconds: int = 300):
        now = time.time()
        with self.connection(write=True) as con:
            con.execute("UPDATE inbox SET status='queued',leased_until=0 WHERE status='running' AND leased_until<?", (now,))
            row = con.execute("""SELECT i.* FROM inbox i WHERE i.status='queued' AND i.next_attempt<=?
                AND NOT EXISTS(SELECT 1 FROM inbox other WHERE other.chat_id=i.chat_id
                   AND other.status IN ('queued','running') AND other.update_id<i.update_id)
                ORDER BY i.update_id LIMIT 1""", (now,)).fetchone()
            if row is None:
                return None
            con.execute("UPDATE inbox SET status='running',attempts=attempts+1,leased_until=? WHERE update_id=?", (now+lease_seconds,row['update_id']))
            result = dict(row)
            result['attempts'] += 1
            result['event'] = json.loads(result['payload'])
            result['response'] = json.loads(result['response']) if result['response'] else None
            return result

    def heartbeat(self, update_id: int, seconds: int):
        with self.connection(write=True) as con:
            con.execute("UPDATE inbox SET leased_until=? WHERE update_id=? AND status='running'", (time.time()+seconds,update_id))

    def reserve(self, update_id: int, chat_id: int, minute_limit: int, day_limit: int, global_limit: int) -> bool:
        now = time.time()
        day = int(now // 86400)
        with self.connection(write=True) as con:
            existing = con.execute("SELECT 1 FROM usage WHERE update_id=?", (update_id,)).fetchone()
            minute = con.execute("SELECT count(*) FROM usage WHERE chat_id=? AND created_at>?", (chat_id,now-60)).fetchone()[0]
            daily = con.execute("SELECT count(*) FROM usage WHERE chat_id=? AND created_at>=?", (chat_id,day*86400)).fetchone()[0]
            key = f"budget:{day}"
            row = con.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
            aggregate = int(row[0]) if row else 0
            if (not existing and (minute >= minute_limit or daily >= day_limit)) or aggregate >= global_limit:
                return False
            if not existing:
                con.execute("INSERT INTO usage VALUES(?,?,?)", (update_id,chat_id,now))
            con.execute("INSERT INTO metadata VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key,str(aggregate+1)))
            return True

    def save_response(self, update_id: int, response: dict, turn: dict | None = None, history_limit: int = 6):
        with self.connection(write=True) as con:
            con.execute("UPDATE inbox SET response=?,attempts=1 WHERE update_id=?", (json.dumps(response,ensure_ascii=False),update_id))
            if turn:
                con.execute("INSERT OR IGNORE INTO turns VALUES(?,?,?,?,?,?)", (turn['id'],turn['chat_id'],turn['question'],turn['answer'],json.dumps(turn['sources'],ensure_ascii=False),time.time()))
                con.execute("DELETE FROM turns WHERE chat_id=? AND id NOT IN (SELECT id FROM turns WHERE chat_id=? ORDER BY created_at DESC,rowid DESC LIMIT ?)", (turn['chat_id'],turn['chat_id'],history_limit))

    def sent(self, update_id: int, cursor: int):
        with self.connection(write=True) as con:
            con.execute("UPDATE inbox SET send_cursor=? WHERE update_id=?", (cursor,update_id))

    def finish(self, update_id: int, *, forget: bool = False, failed: bool = False):
        with self.connection(write=True) as con:
            if forget:
                con.execute("DELETE FROM inbox WHERE update_id=?", (update_id,))
            else:
                con.execute("UPDATE inbox SET status=?,payload='{}',response=NULL,leased_until=0 WHERE update_id=?", ('failed' if failed else 'done',update_id))

    def retry(self, update_id: int, delay: float, code: str):
        with self.connection(write=True) as con:
            con.execute("UPDATE inbox SET status='queued',next_attempt=?,leased_until=0,error_code=? WHERE update_id=?", (time.time()+delay,code,update_id))

    def cleanup(self, retention_hours: int):
        cutoff = time.time() - retention_hours*3600
        with self.connection(write=True) as con:
            con.execute("DELETE FROM turns WHERE created_at<?", (cutoff,))
            con.execute("DELETE FROM inbox WHERE status IN ('done','failed') AND created_at<?", (cutoff,))
            con.execute("DELETE FROM usage WHERE created_at<?", (time.time()-86400,))
            con.execute("DELETE FROM metadata WHERE key LIKE 'budget:%' AND CAST(substr(key,8) AS INTEGER)<?", (int(time.time()//86400)-2,))

    def status(self):
        with self.connection() as con:
            return {"database": con.execute("SELECT 1").fetchone()[0] == 1,
                    "cards": con.execute("SELECT count(*) FROM cards").fetchone()[0],
                    "queued": con.execute("SELECT count(*) FROM inbox WHERE status IN ('queued','running')").fetchone()[0]}

    def backup(self, destination: str):
        if Path(destination).resolve() == Path(self.path).resolve():
            raise ValueError("Zaxira manzili asosiy baza bo‘lishi mumkin emas")
        Path(destination).parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as con, sqlite3.connect(destination) as target:
            con.backup(target)
