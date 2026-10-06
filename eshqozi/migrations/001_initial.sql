CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cards (
  id TEXT PRIMARY KEY, dialect TEXT NOT NULL, kind TEXT NOT NULL,
  form TEXT NOT NULL, meaning TEXT NOT NULL, scope TEXT NOT NULL,
  note TEXT NOT NULL, evidence TEXT NOT NULL, search_text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cards_dialect ON cards(dialect,kind);
CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(search_text,content='cards',content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS cards_ai AFTER INSERT ON cards BEGIN
  INSERT INTO cards_fts(rowid,search_text) VALUES(new.rowid,new.search_text);
END;
CREATE TRIGGER IF NOT EXISTS cards_ad AFTER DELETE ON cards BEGIN
  INSERT INTO cards_fts(cards_fts,rowid,search_text) VALUES('delete',old.rowid,old.search_text);
END;
CREATE TRIGGER IF NOT EXISTS cards_au AFTER UPDATE ON cards BEGIN
  INSERT INTO cards_fts(cards_fts,rowid,search_text) VALUES('delete',old.rowid,old.search_text);
  INSERT INTO cards_fts(rowid,search_text) VALUES(new.rowid,new.search_text);
END;
CREATE TABLE IF NOT EXISTS users (
  chat_id INTEGER PRIMARY KEY, dialect TEXT NOT NULL DEFAULT 'adabiy',
  tone TEXT NOT NULL DEFAULT 'samimiy', created_at REAL NOT NULL, updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS turns (
  id TEXT PRIMARY KEY, chat_id INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  question TEXT NOT NULL, answer TEXT NOT NULL, sources TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS turns_chat_time ON turns(chat_id,created_at);
CREATE TABLE IF NOT EXISTS feedback (
  turn_id TEXT NOT NULL REFERENCES turns(id) ON DELETE CASCADE,
  chat_id INTEGER NOT NULL, score INTEGER NOT NULL CHECK(score IN (-1,1)),
  created_at REAL NOT NULL, PRIMARY KEY(turn_id,chat_id)
);
CREATE TABLE IF NOT EXISTS inbox (
  update_id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, payload TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued' CHECK(status IN ('queued','running','done','failed')),
  response TEXT, send_cursor INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0, next_attempt REAL NOT NULL DEFAULT 0,
  leased_until REAL NOT NULL DEFAULT 0, created_at REAL NOT NULL, error_code TEXT
);
CREATE INDEX IF NOT EXISTS inbox_dispatch ON inbox(status,next_attempt,update_id);
CREATE INDEX IF NOT EXISTS inbox_chat ON inbox(chat_id,status,update_id);
CREATE TABLE IF NOT EXISTS usage (
  update_id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS usage_chat ON usage(chat_id,created_at);
