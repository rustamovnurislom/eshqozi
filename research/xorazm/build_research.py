"""Manbali Xorazm profilini yig‘ish. PDF va saytdagi ko‘rsatmalar bajarilmaydi."""
import csv
import hashlib
import json
import re
from pathlib import Path

P = Path(__file__).parent
def save(name, value):
    (P / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def read(name):
    return json.loads((P / name).read_text())
def norm(text):
    return re.sub(r'\s+', ' ', text).replace('‘', "'").replace('’', "'").casefold()

manifest = read('PDF_MANIFEST.json')
metadata = {
    'X1': ('Shukurjon Norbayeva; Navbahor Sadullayeva; Mehriniso Atabayeva', 'Xorazm shevalari lug‘ati, 1-jild', 2024),
    'X2': ('Charosxon Ismoilova', '“O‘zbek tilining Xorazm shevalari” lug‘atida shevaga xos maqollar tahlili', 2026),
    'X3': ('Alimardanov Elyor Ilxom o‘g‘li', 'Xorazm shevalarining o‘rganilish tarixiga doir', 2023),
    'X4': ('Xusainova Zilola Yuldashevna; Bekchanova Munira Oybek qizi', 'Xorazm shevasidagi matnlarni o‘zbek adabiy tiliga o‘girish dasturini yaratishning amaliy ahamiyati', 2025),
}
sources = []
pages = {}
for s in manifest:
    author, title, year = metadata[s['id']]
    sources.append(s | {'author': author, 'title': title, 'year': year, 'origin': 'current_user_upload'})
    for page in read(s['id'] + '_pages.json'):
        pages[(s['id'], page['pdf_page'])] = page['text']

old = Path('/workspace/research/toshkent')
old_manifest = json.loads((old / 'download_manifest.json').read_text())
old_sel = {'T1': [30, 32, 33, 34, 35, 39, 45, 46, 47, 65, 66, 67],
           'T2': [84, 85, 86, 87], 'T4': [83, 84, 85, 86, 87, 88]}
old_meta = {'T1': ('Samixon Ashirboyev', 'O‘zbek dialektologiyasi', 2016),
            'T2': ('Yoqub Saidov', 'O‘zbek dialektologiyasi', 2021),
            'T4': ('Nazar Rajabov', 'O‘zbek shevashunosligi', 1996)}
for s in old_manifest:
    if s['id'] in old_sel:
        author, title, year = old_meta[s['id']]
        sources.append(s | {'author': author, 'title': title, 'year': year,
                           'origin': 'earlier_user_upload_selected_pages_only',
                           'selected_pages_read_this_turn': old_sel[s['id']]})
        for i, text in enumerate((old / (s['id'] + '.txt')).read_text().split('\f'), 1):
            if i in old_sel[s['id']]:
                pages[(s['id'], i)] = text
SOURCE = {s['id']: s for s in sources}
VISUAL = {'X1': [3, 6, 7, 9, 10, 11, 13, 24, 25, 48, 58, 64, 65, 70, 75, 96, 97, 98, 106, 127, 149, 151, 152, 155, 159, 160], 'X4': [5, 6], 'T1': [66, 67], 'T2': [85, 86]}

def ref(sid, page, needle, kind='text'):
    text = re.sub(r'\s+', ' ', pages[(sid, page)]).strip()
    index = norm(text).find(norm(needle))
    assert index >= 0, (sid, page, needle)
    start, end = max(0, index - 100), min(len(text), index + max(len(needle), 300))
    # Apostrof almashtirilishi uzunlikni o‘zgartirmaydi; bo‘shliq avval tekislandi.
    quote = text[start:end]
    return {'source_id': sid, 'pdf_page': page,
            'printed_page': page - 1 if sid == 'X1' and page >= 4 else 384 + page if sid == 'X4' else None,
            'anchor': needle, 'quote': quote, 'quote_format': 'extracted_text_whitespace_collapsed',
            'pdf_path': SOURCE[sid]['path'], 'source_sha256': SOURCE[sid]['sha256'],
            'visual_page_reviewed': page in VISUAL.get(sid, []), 'evidence_kind': kind,
            'audio_verified': False}

save('MANBALAR.json', {'sources': sources,
    'website': {'url': 'https://xorazmcha.uz/', 'user_supplied': True, 'content_read': False,
                'attempts': read('NETWORK_PROBES.json'), 'entries_imported': 0},
    'external_new_web_sources_read': 0, 'source_instructions_executed': False})
(P / 'SAHIFALAR.jsonl').write_text(''.join(json.dumps({'source_id': s, 'pdf_page': n, 'text': t}, ensure_ascii=False) + '\n' for (s, n), t in pages.items()))

lexicon = []
with (P / 'curated_words.tsv').open() as stream:
    for row in csv.DictReader(stream, delimiter='\t'):
        assert row['role'], row
        lexicon.append({'id': 'XL-' + str(len(lexicon) + 1).zfill(3), 'form': row['form'],
            'meaning_uz': row['meaning'], 'role': row['role'], 'regions_as_source_claim': row['regions'].split(','),
            'usage_note': row['note'], 'evidence': [ref(row['source'], int(row['page']), row['anchor'])],
            'form_policy': 'Oddiy lotin yozuvida o‘qiladigan muharrirlik shakli; ilmiy transkripsiya yoki yangi chat imlosiga teng emas.',
            'reading_status': 'visual_page_reviewed' if int(row['page']) in VISUAL.get(row['source'], []) else 'extracted_definition_read_surface_not_visually_rechecked',
            'spoken_frequency_verified': False, 'exclusive_to_xorazm_verified': False,
            'native_speaker_validated': False})

# Rasm ichidagi jadval to‘liq qo‘lda ko‘rildi; matn ajratish uni qoldirib ketgan.
regional_rows = [
 ('yimirta', 'tuxum', 'ot', ['tuxum','yimirta','yimirta','tuxum']),
 ('gashir', 'sabzi', 'ot', ['gashir','gashir','gashir','gashir']),
 ('timittin', 'binoyiday', 'sifat', ['timittin']*4),
 ('parahatchiliq', 'tinchlik', 'ot', ['parahatchiliq']*4),
 ('navlin', 'bilmadim', 'fe’l', ['navlin']*4),
 ('zangi', 'narvon', 'ot', ['zangi']*4),
 ('opo', 'ona', 'ot', ['opo','opo','opo','opes']),
 ('aka', 'ota', 'ot', ['aka','aka','aka','akes']),
 ('ejashdi', 'hazillashdi', 'fe’l', ['ejashdi']*4),
 ('chapak', 'qarsak', 'ot', ['chapak']*4),
 ('nerda', 'qayerda', 'olmosh', ['nerda']*4),
 ('man', 'men', 'olmosh', ['man','man','man','men']),
 ('eshik', 'eshik', 'ot', ['eshik','qopi','qopi','eshik']),
 ('qarinja', 'chumoli', 'ot', ['qarinja']*4),
 ('pitta', 'ozgina', 'ravish', ['pitta']*4),
 ('borosonmi', 'borasanmi', 'fe’l', ['borosonmi','borsommi','borosomo','borosomo']),
 ("go‘sht", "go‘sht", 'ot', ["go‘sht",'et',"go‘sht","go‘sht"]),
]
regional = []
for i, (surface, standard, pos, forms) in enumerate(regional_rows, 1):
    regional.append({'id': 'XJ-' + str(i).zfill(2), 'source_id': 'X4', 'pdf_page': 5, 'printed_page': 389,
        'source_row_number': i, 'source_headword': surface, 'standard_form_as_printed': standard,
        'source_pos_label': pos, 'district_forms': dict(zip(['Urganch','Xiva','Qo‘shko‘pir','Gurlan'], forms)),
        'table_image': str(P / 'images/X4_005.png'), 'manually_transcribed_from_image': True,
        'all_residents_use_this_form_verified': False,
        'notes': 'Bu maqoladagi 17 qatorli namuna; muallif aytgan 600 so‘zlik dataset fayli berilmagan.'})
save('TUMANLAR_JADVALI.json', regional)
new_table_words = [('yimirta','tuxum'),('gashir','sabzi'),('timittin','binoyiday'),('parahatchiliq','tinchlik'),
 ('navlin','bilmadim'),('zangi','narvon'),('ejashdi','hazillashdi'),('chapak','qarsak'),('nerda','qayerda'),
 ('man','men'),('qopi','eshik'),('qarinja','chumoli'),('borosonmi / borsommi / borosomo','borasanmi')]
for form, meaning in new_table_words:
    target = next(x for x in regional if x['standard_form_as_printed'] == meaning)
    lexicon.append({'id': 'XL-' + str(len(lexicon) + 1).zfill(3), 'form': form, 'meaning_uz': meaning,
        'role': 'savol' if meaning in ['qayerda','borasanmi'] else 'lug‘aviy yoki gap shakli',
        'regions_as_source_claim': list(target['district_forms']),
        'usage_note': 'Tuman variantlari ' + target['id'] + 'da. So‘z turkumi yorlig‘i muallifniki; navlin va borosonmi shaxs-zamonli gap shakllari.',
        'evidence': [{'source_id': 'X4', 'pdf_page': 5, 'printed_page': 389, 'evidence_kind': 'image_table',
            'source_sha256': SOURCE['X4']['sha256'], 'image_path': str(P / 'images/X4_005.png'),
            'table_row_id': target['id'], 'visual_page_reviewed': True}],
        'form_policy': 'Rasm-jadvaldan oddiy lotin yozuvida qo‘lda ko‘chirilgan.',
        'reading_status': 'visual_table_reviewed', 'spoken_frequency_verified': False,
        'exclusive_to_xorazm_verified': False, 'native_speaker_validated': False})

pronouns = [('bunga','binga'),('bunga','minga'),('unga','yunga'),('undan','vundan'),
 ('ana shu','onoshu'),('mana shu','inashu'),('ana','ono'),('mana','ina'),('menga','monga'),('senga','songa')]
save('OLMOSH_JADVALI_ASL.json', [{'row': i, 'source_id': 'X4','pdf_page': 6,'printed_page': 390,
    'left_as_printed': left, 'right_as_printed': right,
    'ambiguous_source_row': i == 2, 'note': 'Bunga ikki marta yozilgan; ikkinchi qatorning taxminiy tuzatishi fakt sifatida kiritilmaydi.' if i == 2 else '',
    'image_path': str(P / 'images/X4_006.png')} for i,(left,right) in enumerate(pronouns,1)])
for left, right in pronouns:
    if right == 'minga': continue
    lexicon.append({'id':'XL-'+str(len(lexicon)+1).zfill(3),'form':right,'meaning_uz':left,'role':'olmosh / ko‘rsatish birligi',
        'regions_as_source_claim':['X4 maqolasida tumani ko‘rsatilmagan'],'usage_note':'Maqoladagi rasm-jadval; boshqa manga/sanga variantlari grammatika kartasida.',
        'evidence':[{'source_id':'X4','pdf_page':6,'printed_page':390,'evidence_kind':'image_pronoun_table',
            'source_sha256':SOURCE['X4']['sha256'],'image_path':str(P/'images/X4_006.png'),
            'table_left':left,'table_right':right,'visual_page_reviewed':True}],
        'form_policy':'Rasm-jadvaldan ko‘chirilgan; hududga qarab variant bor.',
        'reading_status':'visual_table_reviewed','spoken_frequency_verified':False,
        'exclusive_to_xorazm_verified':False,'native_speaker_validated':False})
# Ikkinchi manbada qayd etilgan omonim va darslik leksikasi.
for form, meaning, sid, page, anchor, note in [
    ('kadi','qovoq','X4',6,'“qovoq”','Sabzavot ma’nosi; sevgan kishi ma’nosi bilan kontekstda ajratiladi.'),
    ('kadi','sevgan qizi yoki yigiti','X4',6,'“sevgan','Faqat X4 maqolasidagi izoh; zamonaviy ommaviy qo‘llanish tekshirilmagan.'),
    ('ulli','katta','T2',87,'ulli (katta)','Darslikning o‘g‘uz leksikasi; hamma tuman uchun yagona variant emas.'),
]:
    lexicon.append({'id':'XL-'+str(len(lexicon)+1).zfill(3),'form':form,'meaning_uz':meaning,
        'role':'lug‘aviy ma’no','regions_as_source_claim':['Manbada aniq tuman ko‘rsatilmagan'],
        'usage_note':note,'evidence':[ref(sid,page,anchor)],
        'form_policy':'Manbadagi oddiy lotin shakli.', 'reading_status':'extracted_definition_read',
        'spoken_frequency_verified':False,'exclusive_to_xorazm_verified':False,'native_speaker_validated':False})

save('LUGAT.json',lexicon)
with (P / 'LUGAT_JADVAL.csv').open('w',newline='') as stream:
    fields=['id','form','meaning','role','regions','source_pages','note']
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for c in lexicon:
        writer.writerow({'id':c['id'],'form':c['form'],'meaning':c['meaning_uz'],'role':c['role'],
            'regions':'; '.join(c['regions_as_source_claim']),
            'source_pages':'; '.join(f"{e['source_id']} PDF {e['pdf_page']}" for e in c['evidence']),
            'note':c['usage_note']})

def observations(name, prefix, rows):
    out=[]
    for title, claim, scope, uses, cites in rows:
        out.append({'id':prefix+str(len(out)+1).zfill(2),'title':title,'claim_uz':claim,
            'scope':scope,'bot_application':uses,'evidence':[ref(*c) for c in cites],
            'universal_replace_rule':False,'audio_verified':False})
    save(name,out)
    return out

phonetics=observations('FONETIKA.json','XF-',[
 ('Juft unlilar','Old va orqa qator unli juftliklari, palatal ohangdoshlik qayd etilgan.','O‘g‘uz guruhi, hamma Xorazm bir xil emas.','Bitta a harfi bilan ilmiy tovushlarni tenglashtirma.', [('T2',85,'a-ä'),('X1',6,'Old qator')]),
 ('Cho‘ziqlik ma’noni farqlaydi','at hayvon va a:d ism, o‘t o‘simlik va o‘:t olov juftlari berilgan.','Darslikdagi o‘g‘uz tavsifi.','Oddiy yozuvda cho‘ziqlik ko‘rinmasa, kontekstni o‘qi.', [('T2',85,'a:d'),('X1',8,"cho'ziqligini")]),
 ('So‘z boshidagi k → g','kel/keldi, ko‘z, kun so‘zlarining jarangli variantlari qayd etilgan.','Janubiy o‘g‘uzga oid misollar.','Gal/get/go‘z shakllari faqat mos so‘z va ma’noda.', [('T1',65,'гътть'),('T2',85,'ko’z-go’z')]),
 ('So‘z boshidagi t → d','til-dil, tilak-dilak, tuz-duz misollari bor.','O‘g‘uz guruhining ayrim so‘zlari.','Turk, paxta, tesha, kamon, kema uchun maqoladagi istisnolarni saqla.', [('T2',85,'til-dil'),('T2',85,'tesha')]),
 ('Ichki jaranglashish','Yetti-yeddi va ko‘kimtir-go‘gimtir misollari keltiriladi.','Ayrim so‘zlar.','Hamma t va k ni almashtirma.', [('T2',85,'yetti-yeddi')]),
 ('e/a variantlari','Kel-gal, dedi-dadi va berdi-bardi; gel ko‘hna e bilan ham berilgan.','Manba va hududga bog‘liq.','Gal va gel orasini botda bitta yozuvga majburlama.', [('T1',65,'dedi'),('T1',66,'ko‘hna e')]),
 ('ch ning jarangli varianti','Achchiq-aji va ipning uchi-ipin uji misollari berilgan.','Ayrim o‘g‘uz birliklari.','Ilmiy c harfi j affrikatasini bildirishi mumkin; c har safar ch emas.', [('T2',85,'achchiq'),('X1',7,'qorishiq')]),
 ('q tushishi','Sariq-sari, sichqon-sichon kabi misollar bor.','Ayrim so‘z va tovush muhiti.','Barcha q harfini o‘chirib tashlama.', [('T2',85,'sichqon')]),
 ('a/y muhitida i','Ishlay-ishliy, qo‘ymay-qo‘ymiy shakllari qayd etiladi.','Muayyan fonetik muhit.','Inkor qo‘shimchasi yo‘qolmasin.', [('T2',85,'ishlay')]),
 ('Bo‘l/ol','Bo‘l fe’lining b tushgan varianti qayd etilgan.','Ba’zi o‘g‘uz shevalari.','Bo‘ldi, o‘ldi va olmoqni aralashtirish xavfi; universal b→nol yo‘q.', [('T1',66,'b undoshi'),('T2',85,'o’l')]),
 ('j-lashish hududga bog‘liq','Gurlanning ayrim Amudaryoga yaqin joylari va shimoldan Xivaga kamayish qaydi bor.','X4 mualliflarining hududiy kuzatuvi.','Urganch-Xiva profiliga shimoliy j-lashishni majburan qo‘shma.', [('X4',5,'Amudaryo'),('X3',6,'й-lashgan')]),
 ('Diftong kuzatuvi','Davlat-do‘ulat va quvladi-qo‘uladi misollari keltiriladi.','T2 darsligidagi o‘g‘uz tavsifi.','Faqat ko‘rsatilgan birliklar; har bir o yoki u birikmasini o‘zgartirma.', [('T2',85,'quvladi')]),
 ('Transkripsiya oddiy imlo emas','Lug‘at cho‘ziqlik, old/orqa unlilar, parallel shakl va qavs belgilarini izohlaydi.','X1 ilmiy yozuvi.','Asl transkripsiya, OCR va oddiy o‘qiladigan shaklni ajrat.', [('X1',8,'parallel'),('X1',6,'TRANSKRIPSIYA')]),
])

grammar=observations('GRAMMATIKA.json','XG-',[
 ('Qaratqich va tushum','Urganch-Xivada qaratqich va tushum -ni bilan ifodalanishi; boshqa -ing/-in variantlari bor.','Janubiy o‘g‘uz va darslik varianti.','Egalik va obyekt ma’nosini aralashtirma.', [('T1',66,'qaratqich va tushum'),('T2',86,'Qaratqich')]),
 ('Jo‘nalish -a','Otimga-otima, ishga-isha singari -a variantlari mavjud.','O‘g‘uz guruhi.','Harakat kimga/qayerga ekanini saqla.', [('T1',66,'otimga'),('T2',86,'ancha faol')]),
 ('Jo‘nalish -na','Qo‘liga-alina, bolasiga-balasina; murodiga-murodina misollari.','Egalik bilan keladigan o‘g‘uz shakllari.','So‘zga ko‘r-ko‘rona na qo‘shma.', [('T1',34,'alina'),('T2',86,'murodina')]),
 ('Chiqish -nan','m, n, ng bilan tugagan so‘zlarda o‘zingnan, bo‘yingnan singari variantlar.','Xorazmda tovush muhiti.','Barcha dan ni nan ga almashtirish qoidasi emas.', [('T1',35,'m, n')]),
 ('O‘rin-payt va chiqish','-da/-ta va -dan/-tan tovush muhitiga qarab; ishtan/qishta misollari.','Darslik o‘g‘uz guruhi.','Jo‘nalish, o‘rin va chiqish semantikasini saqla.', [('T2',86,'qishta'),('T2',86,'ishtan')]),
 ('Ko‘plik -la/-lar','Gullar-gulla va olinglar-alingla kabi -la, shuningdek -lar/-lär/-ler variantlari.','Manba va sheva variantlari.','Son va hurmat munosabatini yo‘qotma.', [('T1',66,'ko‘plik affiksi'),('T2',86,'dïlekler')]),
 ('Men/sen va jo‘nalish','Man/san, manga/sanga kabi o‘g‘uz variantlari; X4da monga/songa.','Darslik va X4, turli yozuvlar.','Bir oilani hamma tumanga bir xil shaklda majburlama.', [('T1',66,'olmoshlari'),('X4',6,'olmoshlarning')]),
 ('Qipchoq olmoshlari','Magan/sagan/ugan va -jatir/-vatir shakllari qipchoq tavsifida bor.','Qipchoq, janubiy profilga qo‘shilmaydi.','Hududiy profil tanlansa shu profilning shakllarini saqla.', [('T4',87,'Жуналиш'),('T4',87,'б а р а в а т ы р')]),
 ('Hozirgi davom -yatir','Gayatir va baryatir, shaxsda gayatirman/baryatirman misollari.','Xorazm o‘g‘uz darslik tavsifi.','Toshkent qvoman/kevotti bilan bitta qolipga solma.', [('T1',66,'davom'),('T1',47,'гэ йатьр'.replace(' ',''))]),
 ('Kelasi -jak/-jaq','Barjaqman/getjäksän, kelajak-barajak singari kelasi shakllar.','O‘g‘uz guruhi.','Shaxs, vaqt va niyatni saqla; hamma kelasi gap uchun yagona shakl emas.', [('T2',86,'barjaqman'),('T4',84,'б а р а ж а к')]),
 ('Birgalik istak -li','Galali/barali; kelali kabi birgalik taklifi.','O‘g‘uz guruhi.','Taklifni bir kishiga buyruq qilib yuborma.', [('T1',67,'boraylik'),('T4',88,'к е л э л и')]),
 ('-sana iltimos-buyruq','Barsana/bersana turidagi borsangchi/bersangchi shakli.','Darslikdagi o‘g‘uz mayli.','Oddiy yordamda buyruq ohangini yumshoq va mos tut.', [('T1',67,'borsangchi'),('T4',88,'берсангчи')]),
 ('Harakat nomi -maq/-mak','Gormak, gitmak, oynamaq kabi variantlar.','O‘g‘uz guruhi; adabiy ta’sirda aralashish qaydi ham bor.','Barcha fe’l oxirini so‘zga qaramasdan o‘zgartirma.', [('T1',45,'ojnamaq'),('T1',66,'harakat nomi')]),
 ('To‘liqsiz fe’l adi/akan','Edi/ekan lug‘atda alohida kiritilgan.','X1 tumanlari.','Xabar manbai, zamon va taxmin ma’nosini saqla.', [('X1',9,'toMiqsiz'),('X1',10,'To‘liqsiz')]),
 ('Murakkab o‘tgan zamon','Barivadim/barivadik va olpadim singari shakllar; X1da olib keldi fe’li shakllari berilgan.','Darslik Xorazm qaydi va Xonqa lug‘ati.','Infinitiv izohi bilan shaxsli gapni bir xil birlik deb qabul qilma.', [('T1',46,'Xorazm'),('X1',34,'olgan edim')]),
 ('-an sifatdosh va -ti edi','Gitän, ölän; o‘qianti/go‘ränti misollari.','T2 o‘g‘uz tavsifi.','Hamma hududda aynan shu qolip borligi da’vo qilinmaydi.', [('T2',86,'sifatdosh'),('T2',86,'go’räntï')]),
 ('Istak -asi + galdi','I:chasim galdi turida ichgim keldi; shaxs variantlari bor.','T1 o‘g‘uz guruhi.','Xohish va ro‘y bergan harakatni ajrat.', [('T1',67,'i. casi')]),
 ('Bil- yordamchi fe’li','Palavni dim yaxshi pishirib bilimmän misolida ravishdosh + bil- qobiliyat ma’nosiga nomzod sifatida ajratildi.','X1 dim misoli; gap konteksti.','Bil-ning yordamchi vazifasi kontekstda o‘qiladi; bilimmän shaklini OCR sabab bilman deb qisqartirib, inkorga o‘zgartirmang. To‘liq paradigma bu lug‘atda yo‘q.', [('X1',127,'bilimmein'),('X1',20,'uddalab')]),
 ('Inkorni saqlash','Ishliy/qo‘ymiy, arzimidi va dushunmadim kabi inkorli shakllar ma’noda muhim.','Manbalardagi alohida misollar.','Tushunmadimni tushundim qilib yuborma; manba boshlig‘i xatosini ajrat.', [('X1',144,'tushunmadim'),('X1',24,'Arzimidi'),('T2',85,'qo’ymiy')]),
 ('Dim kuchaytirgichi','Dim sifat ortirma darajasi va juda ma’nosini ifodalaydi.','X1 va T1 o‘g‘uz guruhi.','Vaziyatga mos kuchaytir, har javobga tiqma.', [('X1',127,'sifatning ortirma'),('T1',66,'intensiv')]),
 ('-don ta’kid','Bo‘ladidon misolida -da ta’kidga mos don shakli berilgan.','X4da tumani ko‘rsatilmagan.','T1/T2 darsliklarda shu misol tekshirilmagan; lokal nomzod, default majburiy emas.', [('X4',4,'bo‘ladidon')]),
 ('-qu ta’kid','Oytdm-qu misolida ku/qu ta’kid varianti beriladi.','X4da tumani ko‘rsatilmagan.','Qo‘shimchani har gapga majburan qo‘shma.', [('X4',4,'oytdm-qu')]),
 ('O‘sin ketma-ketlik','So‘ng/so‘ngra ma’nosida o‘sin misoli bor.','X4da tumani ko‘rsatilmagan.','Vaqt ketma-ketligini saqla; barcha keyin so‘zini almashtirma.', [('X4',4,'o‘sin')]),
 ('Olmosh jadvali xatosi','Bunga→binga va bunga→minga ikki qator; ikkinchisi aniqlashtirilmagan.','X4 rasm, PDF 6.','Minga uchun taxminiy standart juftni fakt qilib kiritma.', [('X4',6,'olmoshlarning')]),
])

idioms=observations('IBORALAR.json','XI-',[
 ('Og‘zini suvi oqdi','Juda charchadi; holdan toydi.','X4 sheva tavsifi.','Istak/ishtahti ma’nosidagi boshqa umumiy ibora bilan ajrat.', [('X4',6,'Og‘zini suvi oqdi')]),
 ('Oyoqinnan o‘t chiqdi','Juda charchash iborasi.','X4 sheva tavsifi.','Jismoniy voqea deb talqin qilma.', [('X4',6,'Oyoqinnan')]),
 ('Go‘zzini go‘ki so‘kildi','Ko‘z bilan ishlashdan qattiq charchash.','Qo‘shko‘pir; kompyuter yoki tikuv ishi.','Barcha umumiy charchoqga avtomatik ishlatma.', [('X4',6,'Go‘zzini go‘ki')]),
 ('Borg‘ono boldiz, galgana yengga','Kerakli-keraksiz joyda paydo bo‘ladigan odamga baho.','X4 sheva tavsifi.','Boldiz/yengga qarindoshlik so‘zlarini literal odamlar deb tushunma.', [('X4',6,'Borg‘ono boldiz')]),
 ('Dasmal siqmoq','Laganbardorlik qilish.','X1dagi bir necha tuman.','Xushomad vaziyati bilan.', [('X1',116,'laganbardorlik'),('X1',121,'laganbardorlik')]),
 ('Engsadan deyish','Asabga tegish.','Yangibozor/Gurlan.','Jismoniy ensaga tegish ma’nosi bilan ajrat.', [('X1',159,'asabga tegish')]),
])

proverbs=[]
proverb_rows=[
 (2,'Ejȉt otgännän soŋ hāyȉt xȉnäŋni ökçäŋä ur','Har ishni o‘z vaqtida qilish; hayit/keyin/tovon birliklari.', 'Tovon ko‘çä/ökçä tovush imlosi manbaga bog‘liq.'),
 (2,'Duväqsȉz qazan qāynāmās, änäsȉz balā oynāmās','Qopqoq va ona timsoli; duväq=qopqoq.', 'Bu yerda änä ona; X1 ana=buvi yozuvi bilan kontekst tekshiriladi.'),
 (2,'Deyȉrmenȉ gorä bärmäŋ āyālāb','Yaxshi narsani yomon maqsadga sarflab zoye qilmaslik.', 'Maqolda ikki qism bor; sitata parchasi manba tayanchi.'),
 (2,'Ikki qārğā uruştȉ','Janjal boshqaga qulay vaziyat yaratishi.', 'Yän qulay vaziyat ma’nosida; yanä tomon boshqa izoh.'),
 (2,'Dȉlȉŋ bȉlän qȉstänmā','Kam gapirib ko‘proq ish qilish.', 'Dil=til; qisqargan maqolning to‘liq shakli manba sahifasida.'),
 (2,'Qȉrq kişi bir yanä','Qaysar odam ko‘pchilikka qarshi turishi.', 'Qȉtr=o‘jar; lokal baho, adresatga majburiy emas.'),
 (2,'Adāmni lävzinnän','Lafz va va’daga sodiqlik bilan insonni baholash.', 'Maqoladagi erkaklar cheklovi universal qoida sifatida olinmaydi.'),
 (3,'Bajni aşinnän','Boyning oshidan beminnat mosh afzal.', 'Maş=mosh; ijtimoiy baho maqol vaziyatida.'),
 (3,'Ormä blȉyi','Bilimga ichki ishtiyoq va majburlash foydasi haqida.', 'Blȉy imlosi manbada; to‘liq shaklni tekshirmay o‘zgartirmang.'),
 (3,'Er – xotȉnnȉŋ','Er-xotin janjali haqidagi maqol; bosāğānā=ostona.', 'Oilaviy nizoni masxara qilish botning default ohangi emas.'),
 (3,'Bir gälin aldȉm','Bir va ikki kelin bilan oila munosabati tasviri.', 'Folklor umumiy fakt yoki barcha oilalar xususiyati emas.'),
 (3,'Bevudā xärj etmä','Yoshlikni behuda sarflamaslik.', 'Manba xarj ma’nosini izohlaydi; hayotiy advice uchun kontekst.'),
 (3,'Atār doŋä qärä','Oldinga/yaxshi tarafga intilish haqidagi talqin.', 'Doŋ=tong; don yuklama yoki g‘alla so‘zi bilan aralashtirma.'),
]
for n,anchor,meaning,note in proverb_rows:
    proverbs.append({'id':'XM-'+str(len(proverbs)+1).zfill(2),'anchor':anchor,'meaning_uz':meaning,
        'usage_note':note,'evidence':[ref('X2',n,anchor)],
        'original_1961_dictionary_checked':False,'secondary_article_only':True,
        'sentence_invented':False,'native_modern_usage_verified':False})
save('MAQOLLAR.json',proverbs)

profiles=[
 ('xorazm_janubiy_oguz','Urganch–Xiva o‘g‘uz asosli profil','Urganch–Xiva','X3 tarixiy tasnifida o‘g‘uz kichik guruh. Tumanning barcha qishloqlari bir xil degani emas.', [('X3',6,'Urganch-Xiva'),('T1',65,'qipchoq')]),
 ('xorazm_hazorasp_yangiariq','Hazorasp–Yangiariq','Hazorasp–Yangiariq','O‘g‘uz ichidagi alohida guruh; to‘liq fe’l paradigmasi bu materiallardan tuzilmagan.', [('X3',6,'Hazorasp-Yangiariq')]),
 ('xorazm_qipchoq_j','Shimoliy qipchoq j-lovchi','Gurlan va Amudaryo ayrim qishloqlari','X3 tasnifidagi bir tip; butun Gurlanga avtomatik yoyilmaydi.', [('X3',5,'дж-lashgan'),('X4',5,'Amudaryo')]),
 ('xorazm_qipchoq_y','Qipchoq y-lovchi','Amudaryo, Gurlan, Beruniy, To‘rtko‘l qishloqlari','X3 tarixiy tasnifi, hududiy zamonaviy geoma’lumot sifatida tekshirilmagan.', [('X3',6,'й-lashgan')]),
 ('xorazm_qipchoq_a','Qipchoq ə-lashgan','Gurlan, Urganch, Hazorasp, Shovot qishloqlari','X3 tasnifi; har tuman markazining profili degani emas.', [('X3',6,'ə-lashgan')]),
 ('xorazm_aralash_qipchoq_oguz','Qipchoq–o‘g‘uz aralash','Urganch, Qo‘shko‘pir, Yangibozor, Xonqa qishloqlari','Aniq qishloq yoki mahalliy misol bo‘lsa tanlash mumkin.', [('X3',6,'Aralash tipdagi qipchoq-o')]),
 ('xorazm_aralash_oguz_qipchoq','O‘g‘uz–qipchoq aralash','Urganch, Shovot, Qo‘shko‘pir, Hazorasp qishloqlari','Oldingi aralash profil bilan asosning farqi saqlanadi.', [('X3',6,'Aralash tipdagi o')]),
]
save('HUDUDIY_PROFILLAR.json',[{'id':sid,'name':name,'source_region':region,'notes':note,
    'evidence':[ref(*c) for c in cites],'ready_native_generation_verified':False,
    'default_candidate':sid=='xorazm_janubiy_oguz'} for sid,name,region,note,cites in profiles])

issues=[
 ('Birinchi jild qamrovi','X1 A unli bo‘limlari, B, D, E bilan tugaydi; G/Z va boshqalar shu faylda yo‘q.','To‘liq Xorazm lug‘ati deb sanalmaydi.', [('X1',160,'M U N D A R I J A')]),
 ('600 so‘z da’vosi','X4 mualliflari 600 birlik to‘planganini aytadi; ko‘rinadigan jadval 17 qator.','600 so‘z import qilindi yoki datasetni o‘qidim deb aytilmaydi.', [('X4',4,'600ta')]),
 ('Lug‘at lookupi va tarjima','X4 rasmda bitta barak so‘zidan chuchvara va ot chiqarilishi ko‘rsatilgan.','Bu butun gapning ma’nosi, zamoni yoki bot suhbat sifati isboti emas.', [('X4',5,'so‘zning adabiy')]),
 ('Bunga/minga qatori','Rasmda bunga ikki marta yozilgan.','Ikkinchi qator ochiq savol sifatida saqlandi.', [('X4',6,'olmoshlarning')]),
 ('Ejashdi ma’nosi','X4 jadvalida hazillashdi; X1 ejashmoq izohida o‘chakishmoq, zid ish.','Yaqin shaklning ma’nosini hamma gapda bir xil deb bermang.', [('X1',149,'o‘chakishmoq')]),
 ('Ona/buvi','X1 ana=buvi, apa=ona; X2 maqolida änä ona deb sharhlanadi.','Talaffuz yozuvi, avlod va kontekst farqi saqlanadi.', [('X1',16,'buvi'),('X1',36,'ona ( Xorazmning'),('X2',2,'Duväqsȉz')]),
 ('Et hududi','X1 et Xiva, Xonqa, Urganchda; X4 jadvalida et Xivada, boshqalar go‘sht.','Bir jadvaldagi shakl boshqa variantning yo‘qligini isbotlamaydi.', [('X1',155,'go‘sht')]),
 ('Eshik ma’nolari','X1 tashqi hovli; X4 eshik/qopi jadvali fizik eshik.','Eshikka chiqish bilan eshik buyumini ajrat.', [('X1',159,'tashqariga nisbatan')]),
 ('Dushunmak izohi','Boshliq infinitiv ko‘rinishda; izoh tushunmadim va misol dushunmadim.','Lug‘at izohidan shaxs/inkorni ko‘r-ko‘rona ko‘chirmang.', [('X1',144,'tushunmadim')]),
 ('Apkaldi izohi','Lug‘at olib kelmoq deb izohlagan shaxsli o‘tgan shakl.','Infinitiv bilan o‘tgan zamon farqlanadi.', [('X1',20,'olib kelmoq')]),
 ('OCR xatolari','Ba:s OCRda bars, a:lakim arlakim, c/j/sh/ch belgilarida buzilish bor.','Asl rasm va muharrirlik soddalashtirish alohida.', [('X1',75,'balls'),('X1',65,'salomiga javob')]),
 ('-yatir variantlari tavsifi','T1 -yatirni bir variantli deb bayon qiladi; T4 janubiy Xorazm uchun -yatir/-yetir shakllarini beradi.','Darsliklar tavsifidagi farq saqlanadi; bitta universallik qoidasi chiqarilmaydi.', [('T1',66,'bir variantli'),('T4',84,'-йатир')]),
 ('Bilimmän yozuvi','X1 PDF 127 rasmida bilimmän; oddiy bilman tarzida qisqartirish zamon/inkor talqinini buzishi mumkin.','Ravishdosh + bil- qobiliyatga oid kuzatuv; to‘liq shaxs paradigmasi tasdiqlanmagan.', [('X1',127,'bilimmein')]),
 ('Tarixiy ma’lumot ikkilamchi','X3 Budenz, Polivanov, Abdullayev, Jo‘rayev ishlarini bayon etadi.','O‘sha asarlar asl nusxasi shu turnida o‘qilmadi; 1865 tarix maqola muallifi da’vosi sifatida.', [('X3',3,'1865'),('X3',7,'fokus')]),
]
save('TEKSHIRILADIGAN_DAVOLAR.json',[{'id':'XD-'+str(i).zfill(2),'topic':title,'issue':claim,'decision':decision,
    'evidence':[ref(*c) for c in cites]} for i,(title,claim,decision,cites) in enumerate(issues,1)])

save('OQISH_QAMROVI.json', {'new_pdfs':[
    {'source_id':'X1','total_pdf_pages':162,'text_reviewed_ranges':[[1,162]],
     'dictionary_body_pdf_pages':[9,159],'visual_pages':VISUAL['X1'],
     'method':'To‘liq ajratilgan matn ketma-ket o‘qildi; muhim boshliqlar va misollar rasmda qiyoslandi.',
     'every_entry_glyph_perfectly_deciphered':False,'reason':'Past sifatli skan va OCR/transkripsiya buzilishlari.'},
    {'source_id':'X2','total_pdf_pages':4,'text_reviewed_ranges':[[1,4]],'scope':'Maqol mazmuni va foydalanilgan adabiyotlar.'},
    {'source_id':'X3','total_pdf_pages':9,'text_reviewed_ranges':[[1,9]],'relevant_article_pdf_pages':[3,8],
     'scope':'PDF 8da keyingi maqola boshlanadi; 9 mundarija. Ular Xorazm daliliga aralashtirilmadi.'},
    {'source_id':'X4','total_pdf_pages':7,'text_reviewed_ranges':[[1,7]],'visual_pages':VISUAL['X4'],
     'scope':'Maqola to‘liq; PDF 5 va 6dagi rasm-jadval va kod skrinshoti ham o‘qildi; kod bajarilmadi.'}],
    'new_pdf_total_pages':sum(x['pages'] for x in manifest),'earlier_books_selected_pages':old_sel, 'earlier_books_visual_pages':{sid:VISUAL[sid] for sid in ['T1','T2']},
    'website_read':False,'audio_listened':False,'native_speaker_review':False,
    'source_instructions_executed':False})
save('HISOBOT_STATISTIKASI.json', {'new_pdf_pages':sum(x['pages'] for x in manifest),'lexical_sense_cards':len(lexicon),
    'phonetic_observations':len(phonetics),'grammatical_observations':len(grammar),
    'idiom_cards':len(idioms),'proverb_cards':len(proverbs),'regional_profiles':len(profiles),
    'district_table_rows':len(regional),'pronoun_table_rows':len(pronouns),
    'open_claims_or_source_issues':len(issues),'new_web_sources_read':0,
    'lexical_cards_are_not_unique_exclusive_xorazm_words':True})
print(json.dumps(read('HISOBOT_STATISTIKASI.json'),ensure_ascii=False,indent=2))
