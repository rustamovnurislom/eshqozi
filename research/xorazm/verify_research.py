"""Dalil va tadqiqot fayllari izchilligini tekshiradi; native nutqni baholamaydi."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).parent
def read(name):
    return json.loads((P/name).read_text())
def norm(s):
    return re.sub(r'\s+', ' ', s).replace('‘', "'").replace('’', "'").casefold()

checks = []
def require(ok, label, detail=None):
    checks.append({'check':label, 'passed':bool(ok), 'detail':detail})
    if not ok:
        raise AssertionError(label)

sources = read('MANBALAR.json')['sources']
source_map = {x['id']: x for x in sources}
require(len(source_map)==7, 'Seven distinct PDF sources')
for source in sources:
    actual = hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()
    require(actual==source['sha256'], 'Original PDF hash '+source['id'])

rows = [json.loads(x) for x in (P/'SAHIFALAR.jsonl').read_text().splitlines()]
pages = {(x['source_id'],x['pdf_page']):x['text'] for x in rows}
require(len(rows)==len(pages)==204, '182 current and 22 selected earlier pages retained')
require(sum(x['pages'] for x in sources if x['id'].startswith('X'))==182, 'Current PDF page count 182')

files = ['LUGAT.json','FONETIKA.json','GRAMMATIKA.json','IBORALAR.json',
         'MAQOLLAR.json','HUDUDIY_PROFILLAR.json','TEKSHIRILADIGAN_DAVOLAR.json',
         'USLUB_PROFILI.json','NUTQ_NAMUNALARI.json','HUDUDLAR_QIYOSI.json',
         'MAZMUN_SINOVLARI.json']
reference_count = 0
text_reference_count = 0
image_reference_count = 0
unique_reference_pages = set()
def walk(value):
    global reference_count, text_reference_count, image_reference_count
    if isinstance(value,list):
        for x in value: walk(x)
    elif isinstance(value,dict):
        if 'source_id' in value and 'pdf_page' in value:
            key = value['source_id'],value['pdf_page']
            assert key in pages, ('Page not retained',key)
            unique_reference_pages.add(key)
            reference_count += 1
            if 'source_sha256' in value:
                assert value['source_sha256']==source_map[key[0]]['sha256']
            if 'anchor' in value:
                assert norm(value['anchor']) in norm(pages[key]), key
                assert norm(value['quote']) in norm(pages[key]), (key,'quote')
                text_reference_count += 1
            if 'image_path' in value:
                assert Path(value['image_path']).is_file(), value['image_path']
                image_reference_count += 1
        for x in value.values(): walk(x)

for name in files:
    walk(read(name))
require(reference_count>300, 'All evidence references resolve to retained pages', reference_count)
require(text_reference_count>250, 'All extracted anchors and quotes match source pages', text_reference_count)
require(image_reference_count==22, 'Twenty-two image-table lexical references', image_reference_count)

lexicon = read('LUGAT.json')
require(len(lexicon)==209 and len({x['id'] for x in lexicon})==209, '209 distinct sense card IDs')
require(all(x['meaning_uz'] and x['evidence'] and x['usage_note'] for x in lexicon), 'Every sense card has meaning, evidence and context note')
require(all(not x['native_speaker_validated'] and not x['spoken_frequency_verified'] for x in lexicon), 'Native/frequency validation is not falsely asserted')
require(len([x for x in lexicon if x['evidence'][0]['source_id']=='X1'])==184, '184 curated dictionary sense cards')
require({x['meaning_uz'] for x in lexicon if x['form']=='kadi'}=={'qovoq','sevgan qizi yoki yigiti'}, 'Kadi homonym senses kept distinct')
require(not any(x['form']=='minga' for x in lexicon), 'Ambiguous minga mapping excluded from lexicon')
csv_rows = list(csv.DictReader((P/'LUGAT_JADVAL.csv').open()))
require([(x['id'],x['form'],x['meaning']) for x in csv_rows]==[(x['id'],x['form'],x['meaning_uz']) for x in lexicon], 'CSV and JSON lexical cards agree')

district = read('TUMANLAR_JADVALI.json')
require(len(district)==17 and [x['source_row_number'] for x in district]==list(range(1,18)), 'All 17 source table rows retained in order')
require(all(len(x['district_forms'])==4 and Path(x['table_image']).is_file() for x in district), 'Every district row has four columns and source image')
pronouns = read('OLMOSH_JADVALI_ASL.json')
require(len(pronouns)==10 and pronouns[0]['left_as_printed']==pronouns[1]['left_as_printed']=='bunga' and pronouns[1]['ambiguous_source_row'], 'Duplicate bunga row preserved and marked ambiguous')
samples = read('NUTQ_NAMUNALARI.json')
require(Counter(x['kind'] for x in samples)=={'printed_example_editorial_reading':8,'constructed_bot_candidate':8}, 'Printed and constructed examples separated 8/8')
require(all(not x['verbatim_scientific_transcription'] for x in samples), 'Simplified readings never asserted to be verbatim transcription')
require(read('MANBALAR.json')['website']['entries_imported']==0 and not read('OQISH_QAMROVI.json')['website_read'], 'Blocked site contributes zero imported evidence')
require(not read('USLUB_PROFILI.json')['generation_readiness']['trained_model_weights'], 'Prepared profile is not presented as trained model weights')

stats = read('HISOBOT_STATISTIKASI.json')
for field,name in [('phonetic_observations','FONETIKA.json'),('grammatical_observations','GRAMMATIKA.json'),
                   ('idiom_cards','IBORALAR.json'),('proverb_cards','MAQOLLAR.json'),
                   ('regional_profiles','HUDUDIY_PROFILLAR.json'),('open_claims_or_source_issues','TEKSHIRILADIGAN_DAVOLAR.json')]:
    require(stats[field]==len(read(name)), 'Statistics agree: '+field)
coverage = read('OQISH_QAMROVI.json')
visuals = {x['source_id']:x.get('visual_pages',[]) for x in coverage['new_pdfs']}
visuals.update(coverage['earlier_books_visual_pages'])
require(sum(map(len,visuals.values()))==32, '32 visually checked source pages declared')
for sid, nums in visuals.items():
    for n in nums: assert (P/f'images/{sid}_{n:03}.png').is_file()
report = (P/'OQISH_XULOSALARI.md').read_text()
targets = re.findall(r'\]\(([^)]+)\)',report)
require(all((P/x).is_file() or x=='TEKSHIRUV_NATIJASI.json' for x in targets), 'All report artifact links resolve')
result = {'status':'passed','scope':'Fayllar, dalil tayanchlari, o‘qish qamrovi va jadval izchilligi. Native nutq sifati yoki ishlayotgan bot sinovi emas.',
          'checks':checks,'reference_count':reference_count,'text_reference_count':text_reference_count,
          'image_reference_count':image_reference_count,'distinct_referenced_pages':len(unique_reference_pages),
          'lexical_sense_cards':len(lexicon),'visual_pages':32,
          'native_speaker_validation':False,'audio_validation':False}
(P/'TEKSHIRUV_NATIJASI.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
