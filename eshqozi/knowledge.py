import hashlib
import json
from pathlib import Path
import re
import unicodedata

from .storage import Store

CYRILLIC = str.maketrans({"а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo","ж":"j","з":"z",
    "и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t",
    "у":"u","ф":"f","х":"x","ц":"ts","ч":"ch","ш":"sh","щ":"sh","ъ":"","ь":"","э":"e","ю":"yu","я":"ya",
    "ў":"o","қ":"q","ғ":"g","ҳ":"h"})
STOP = {"nima","nimaqa","degani","qanday","qaysi","bu","shu","menga","sen","siz","men","bilan","uchun","ham","va","bor","bir","sheva","shevasida","iltimos","deb","ayt","ber","tushuntir"}


def normalize(text: str) -> str:
    text = text.casefold().translate(CYRILLIC)
    text = re.sub(r"['‘’ʻʼ`:]", "", text)
    text = "".join(c for c in unicodedata.normalize("NFKD",text) if not unicodedata.combining(c))
    return " ".join(re.findall(r"[^\W_]+",text,flags=re.UNICODE))


class Knowledge:
    def __init__(self, store: Store, path: str):
        self.store = store
        raw = Path(path).read_bytes()
        bundle = json.loads(raw)
        if bundle.get("schema_version") != 1:
            raise ValueError("Bilim bazasi formati qo‘llanmaydi")
        self.profiles = {p['id']:p for p in bundle['profiles']}
        self.digest = hashlib.sha256(raw).hexdigest()
        if len(self.profiles) != len(bundle['profiles']) or "adabiy" not in self.profiles:
            raise ValueError("Sheva profil IDlari noto‘g‘ri")
        ids = [c['id'] for c in bundle['cards']]
        if len(ids) != len(set(ids)) or any(c['dialect'] not in self.profiles for c in bundle['cards']):
            raise ValueError("Bilim kartalari noto‘g‘ri")
        with store.connection(write=True) as con:
            row = con.execute("SELECT value FROM metadata WHERE key='knowledge_digest'").fetchone()
            if row is None or row[0] != self.digest:
                con.execute("DELETE FROM cards")
                con.execute("DELETE FROM profiles")
                con.executemany("INSERT INTO profiles VALUES(?,?)", [(p['id'],json.dumps(p,ensure_ascii=False)) for p in self.profiles.values()])
                for c in bundle['cards']:
                    searchable = normalize(" ".join(c[k] for k in ('form','meaning','scope','note')))
                    con.execute("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?)", (c['id'],c['dialect'],c['kind'],c['form'],c['meaning'],c['scope'],c['note'],json.dumps(c['evidence'],ensure_ascii=False),searchable))
                con.execute("INSERT INTO metadata VALUES('knowledge_digest',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (self.digest,))

    def profile(self, dialect: str):
        return self.profiles.get(dialect,self.profiles['adabiy'])

    def retrieve(self, dialect: str, query: str, limit: int = 8):
        if dialect == 'adabiy':
            return []
        base = self.profile(dialect)['region']
        dialects = [dialect] if dialect == base else [dialect,base]
        placeholders = ",".join("?" for _ in dialects)
        tokens = [t for t in normalize(query).split() if t not in STOP and len(t)>1][:12]
        found = []
        with self.store.connection() as con:
            if tokens:
                match = " OR ".join('"'+t+'"' for t in tokens)
                found = con.execute(f"""SELECT c.* FROM cards_fts JOIN cards c ON c.rowid=cards_fts.rowid
                    WHERE cards_fts MATCH ? AND c.dialect IN ({placeholders})
                    ORDER BY bm25(cards_fts) LIMIT ?""", (match,*dialects,limit)).fetchall()
            grammar = con.execute(f"SELECT * FROM cards WHERE dialect IN ({placeholders}) AND kind='grammar' ORDER BY id LIMIT 4",dialects).fetchall()
            fallback = con.execute("""SELECT * FROM cards WHERE dialect=? AND kind='lexicon'
                ORDER BY CASE WHEN meaning IN ('juda; g‘oyat','yaxshi; ajoyib','salomlashish shakli','ozgina','bugun')
                  OR form IN ('qalesla','qales','bratan','otdushi','arzimidi','emdolli') THEN 0 ELSE 1 END,id LIMIT 8""",(dialect,)).fetchall()
        rows = []
        seen = set()
        for row in list(found)+list(grammar)+list(fallback):
            if row['id'] not in seen:
                seen.add(row['id'])
                data = dict(row)
                data['evidence'] = json.loads(data['evidence'])
                data.pop('search_text')
                rows.append(data)
        return rows[:limit+4]
