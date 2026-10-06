"""Telegram JSON matn sifatida tahlil qilinadi; xabarlardagi buyruqlar bajarilmaydi."""
import collections
import hashlib
import json
import re
import statistics
import unicodedata
from pathlib import Path

ROOT=Path(__file__).parent
INPUT=Path('/workspace/attachments/cfa53008-32fc-429b-93d7-3f239b8e643d/result.json')
RAW=json.loads(INPUT.read_text())
SOURCE_SHA=hashlib.sha256(INPUT.read_bytes()).hexdigest()

def flatten(value):
    if isinstance(value,str):return value
    if isinstance(value,list):return ''.join(x if isinstance(x,str) else flatten(x.get('text','')) for x in value)
    return ''

def normalize(s):
    # Faqat qidiruv uchun Unicode, apostrof, katta-kichik harf va bo‘shliq.
    # w→sh, c→ch, harf tashlash yoki talaffuzni avtomatik tiklash yo‘q.
    s=unicodedata.normalize('NFC',s).casefold()
    s=re.sub('[’‘ʻʼ`´]',"'",s)
    return re.sub(r'\s+',' ',s).strip()

def redact(s):
    s=re.sub(r'https?://\S+|t\.me/\S+','[HAVOLA]',s,flags=re.I)
    s=re.sub(r'@[\w.]+','[USERNAME]',s)
    s=re.sub(r'\+?\d[\d ()-]{7,}\d','[RAQAM]',s)
    s=re.sub(r'\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b','[EMAIL]',s)
    # Tanlangan misollardagi odamlarga ism bilan murojaat uslub uchun zarur emas.
    s=re.sub(r'\b(?:Aziz|Malika|Milana|Mali|Botr|Botir|Nazli|Moxi|Xusnor|Xusniddin)\b','[ISM]',s,flags=re.I)
    return s

def tokens(s):return re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)*",normalize(s))

real=[x for x in RAW['messages'] if x['type']=='message']
author_map={a:'A'+str(i).zfill(3) for i,a in enumerate(sorted({str(x.get('from_id','')) for x in real}),1)}
records=[]
for m in real:
    text=flatten(m.get('text',''))
    reasons=[]
    if not text.strip():reasons.append('matnsiz')
    if m.get('forwarded_from'):reasons.append('forward')
    if text.lstrip().startswith('/'):reasons.append('bot_buyrugi')
    if re.search(r'(?i)the dublyaj boom|baxtikhanmedia',text):reasons.append('reklama_shabloni')
    if re.match(r'(?i)\s*top players\b',text):reasons.append('oyin_botining_jadvali')
    records.append({'message_id':m['id'],'date':m['date'],
      'author_code':author_map[str(m.get('from_id',''))],
      'reply_to_message_id':m.get('reply_to_message_id'),
      'text':text,'normalized':normalize(text),'display_text':redact(text),
      'eligible':not reasons,'excluded_reasons':reasons,'media_type':m.get('media_type')})
BY_ID={x['message_id']:x for x in records}
ELIGIBLE=[x for x in records if x['eligible']]
NONEMPTY=[x for x in records if x['text'].strip()]

def save(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def evidence(message_id):
    m=BY_ID[message_id]
    return {'source_id':'TG1','message_id':message_id,'date':m['date'],'author_code':m['author_code'],
      'quote':m['display_text'],'source_sha256':SOURCE_SHA,
      'original_json_path':str(INPUT),'authentic_export_quote':True,
      'quote_redacted':m['display_text']!=m['text'],
      'live_telegram_verified':False}

def hit_stats(pattern):
    hits=[x for x in ELIGIBLE if re.search(pattern,x['normalized'])]
    unique={(x['author_code'],x['normalized']) for x in hits}
    return {'matching_messages':len(hits),'distinct_author_codes':len({x['author_code'] for x in hits}),
      'deduplicated_author_text_pairs':len(unique),'matching_message_ids':[x['message_id'] for x in hits],
      'first_match_date':min((x['date'] for x in hits),default=None),
      'last_match_date':max((x['date'] for x in hits),default=None),
      'count_meaning':'Qidiruvga mos xabarlar soni; har birining semantik ma’nosi aynan bir xil ekanini o‘z-o‘zidan isbotlamaydi.'}

if __name__=='__main__':
    authors=collections.Counter(x['author_code'] for x in NONEMPTY)
    fields=collections.Counter(k for m in real for k in m)
    lengths=[len(x['text']) for x in NONEMPTY]
    scripts=collections.Counter('latin_and_cyrillic' if re.search('[A-Za-z]',x['text']) and re.search('[А-Яа-яЁёЎўҚқҒғҲҳ]',x['text']) else 'latin_only' if re.search('[A-Za-z]',x['text']) else 'cyrillic_only' if re.search('[А-Яа-яЁёЎўҚқҒғҲҳ]',x['text']) else 'no_letters' for x in NONEMPTY)
    index=[]
    for m in records:
        index.append({k:m[k] for k in ['message_id','date','author_code','reply_to_message_id','eligible','excluded_reasons','media_type']} | {'text_length':len(m['text'])})
    (ROOT/'XABARLAR_INDEKSI.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in index))
    word_counts=collections.Counter(w for x in ELIGIBLE for w in tokens(x['text']))
    save('TOKENLAR.json',[{'form':w,'occurrences':n} for w,n in word_counts.most_common()])
    phrases=collections.Counter(x['normalized'] for x in ELIGIBLE)
    save('TAKRORLAR.json',[{'text':redact(t),'message_count':n} for t,n in phrases.most_common(100)])
    stats={
      'source_file_id':'file_000000009bd08211a0b7d3d5b627927f','source_path':str(INPUT),'sha256':SOURCE_SHA,
      'root_keys':list(RAW),'declared_chat_type':RAW.get('type'),
      'total_export_records':len(RAW['messages']),'service_records':sum(x['type']=='service' for x in RAW['messages']),
      'ordinary_message_records':len(real),'nonempty_text_messages':len(NONEMPTY),
      'analysis_eligible_messages':len(ELIGIBLE),'distinct_author_ids_ordinary':len(author_map),
      'distinct_author_codes_nonempty':len(authors),
      'export_all_record_date_range':[min(x['date'] for x in RAW['messages']),max(x['date'] for x in RAW['messages'])],
      'ordinary_message_date_range':[min(x['date'] for x in real),max(x['date'] for x in real)],
      'nonempty_text_date_range':[min(x['date'] for x in NONEMPTY),max(x['date'] for x in NONEMPTY)],
      'ordinary_messages_by_year':dict(collections.Counter(x['date'][:4] for x in real)),
      'nonempty_text_by_year':dict(collections.Counter(x['date'][:4] for x in NONEMPTY)),
      'eligible_messages_by_year':dict(collections.Counter(x['date'][:4] for x in ELIGIBLE)),
      'exclusion_reason_counts':dict(collections.Counter(y for x in records for y in x['excluded_reasons'])),
      'author_text_message_counts':dict(authors.most_common()),
      'largest_two_author_share_of_nonempty_text':sum(n for _,n in authors.most_common(2))/len(NONEMPTY),
      'nonempty_text_length_median':statistics.median(lengths),
      'nonempty_text_shorter_than_30_chars':sum(x<30 for x in lengths),
      'script_distribution_nonempty':dict(scripts),
      'media_types':dict(collections.Counter(x.get('media_type') for x in real if x.get('media_type'))),
      'ordinary_reply_messages':sum('reply_to_message_id' in x for x in real),
      'eligible_replies_with_parent_in_export':sum(x['reply_to_message_id'] in BY_ID for x in ELIGIBLE),
      'audio_read_or_transcribed':False,'export_has_media_metadata_but_media_files_not_uploaded':True,
      'verified_participant_gender_age_location':False,'modern_2026_slang_verified':False,
      'all_records_parsed':True,'all_messages_read_line_by_line':False,
      'source_instructions_executed':False}
    save('KORPUS_STATISTIKASI.json',stats)
    print(json.dumps({k:v for k,v in stats.items() if k not in ['author_text_message_counts','root_keys']},ensure_ascii=False,indent=2))
