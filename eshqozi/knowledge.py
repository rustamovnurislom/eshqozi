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
STOP = {"nima","nimaqa","degani","qanday","qaysi","bu","shu","menga","sen","siz","men","bilan","uchun","ham","va","bor","bir","sheva","shevasida","hududida","viloyatida","tumanida","qishlogida","iltimos","deb","ayt","ber","tushuntir","uslubida","uslubda","kocha","zamonaviy","slang","dalili","bolmasa","uydirma","gaplash","yoz"}


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
        self.details = {c['id']:c.get('meta',{}) for c in bundle['cards']}
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

    def context_profile(self, dialect: str, query: str):
        """Hudud tafsilotini faqat foydalanuvchi aniq joyni so‘raganda uzatadi."""
        base = self.profile(dialect)
        selected = dict(base)
        regional = self.profile(base['region']) if base['region'] in self.profiles else base
        if dialect != regional['id'] and regional.get('voice'):
            selected['regional_voice'] = regional['voice']
        variants = regional.get('regional_variants',[])
        words = set(normalize(query).split())
        selected['local_variant'] = [v for v in variants
             if any(word in words for word in normalize(v['name']).split() if len(word)>3)][:2]
        selected.pop('regional_variants',None)
        return selected

    def retrieve(self, dialect: str, query: str, limit: int = 8):
        if dialect == 'adabiy':
            return []
        base = self.profile(dialect)['region']
        dialects = [dialect] if dialect == base else [dialect,base]
        placeholders = ",".join("?" for _ in dialects)
        local_variants = self.context_profile(dialect,query)['local_variant']
        place_words = {word for variant in local_variants for word in normalize(variant['name']).split()
                       if len(word)>3}
        raw_tokens = normalize(query).split()
        profile_words = set(normalize(self.profile(dialect)['label']).split())
        tokens = [t for t in raw_tokens if t not in STOP and t not in place_words
                  and t not in profile_words and len(t)>1][:12]
        preferred_kind = ('phonetics' if any(t in {'fonetika','fonetik','talaffuz','tovush'} for t in raw_tokens)
                          else 'example' if any(t in {'misol','namuna','namunasi'} for t in raw_tokens)
                          else 'lexicon')
        found = []
        selected_profile = self.profile(dialect)
        seed_profile = self.profile(selected_profile['region']) if selected_profile.get('trial') else selected_profile
        seed_forms = {normalize(form) for form in seed_profile.get('voice',{}).get('low_risk_forms',[])}
        with self.store.connection() as con:
            if tokens:
                match = " OR ".join('"'+t+'"' for t in tokens)
                found = con.execute(f"""SELECT c.* FROM cards_fts JOIN cards c ON c.rowid=cards_fts.rowid
                    WHERE cards_fts MATCH ? AND c.dialect IN ({placeholders})
                    ORDER BY CASE WHEN c.dialect=? THEN 0 ELSE 1 END,
                      CASE WHEN c.kind=? THEN 0 WHEN c.kind='lexicon' THEN 1
                        WHEN c.kind='grammar' THEN 2 ELSE 3 END, bm25(cards_fts)
                    LIMIT ?""", (match,*dialects,dialect,preferred_kind,max(64,limit*8))).fetchall()
                normalized_query = ' ' + normalize(query) + ' '
                def exact_form(row):
                    forms = [normalize(re.sub(r'\s+I{1,3}$','',part.strip())) for part in row['form'].split('/')]
                    return any(form and ' '+form+' ' in normalized_query for form in forms)
                found = sorted(found,key=lambda row:(not exact_form(row),row['kind']!=preferred_kind,row['dialect']!=dialect))[:limit]
                found = [row for row in found if row['kind'] not in {'example','phonetics'}
                         or row['kind']==preferred_kind or exact_form(row)]
                if selected_profile.get('trial') and normalize(query).startswith(('nma gap','salom')):
                    found = [row for row in found if exact_form(row)]
            grammar = con.execute(f"SELECT * FROM cards WHERE dialect IN ({placeholders}) AND kind='grammar' ORDER BY id LIMIT 4",dialects).fetchall()
            if selected_profile.get('trial') and seed_forms:
                candidates = con.execute("SELECT * FROM cards WHERE dialect=? AND kind='lexicon' ORDER BY id",(seed_profile['id'],)).fetchall()
                fallback = [r for r in candidates if normalize(r['form']) in seed_forms][:5]
            elif dialect.endswith('_kocha'):
                fallback = con.execute("""SELECT * FROM cards WHERE dialect=? AND kind='lexicon'
                    ORDER BY CASE WHEN form IN ('qalesla','qales','bratan','otdushi','arzimidi','emdolli')
                      OR meaning IN ('juda; g‘oyat','yaxshi; ajoyib','salomlashish shakli','ozgina')
                      THEN 0 ELSE 1 END,id LIMIT 5""",(dialect,)).fetchall()
            elif seed_forms:
                candidates = con.execute("SELECT * FROM cards WHERE dialect=? AND kind='lexicon' ORDER BY id",(dialect,)).fetchall()
                fallback = [r for r in candidates if normalize(r['form']) in seed_forms][:5]
            else:
                fallback = []
            examples = con.execute(f"SELECT * FROM cards WHERE dialect IN ({placeholders}) AND kind='example' ORDER BY id LIMIT 2",dialects).fetchall() if preferred_kind=='example' and not found else []
        rows = []
        seen = set()
        for row in list(found)+list(grammar)+list(fallback)+list(examples):
            if row['id'] not in seen:
                seen.add(row['id'])
                data = dict(row)
                data['evidence'] = json.loads(data['evidence'])
                data.pop('search_text')
                data['meta'] = self.details.get(data['id'],{})
                rows.append(data)
        return rows[:limit+4]
