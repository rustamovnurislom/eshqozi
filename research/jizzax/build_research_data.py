"""Jizzax bo‘yicha o‘qilgan dalillardan qayta yaratiladigan tadqiqot to‘plami."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
manifest = json.loads((ROOT / 'download_manifest.json').read_text())
old_path = Path('/workspace/attachments/a3a82354-817b-48d5-9018-fa152b5a9f3f/Ўзбек халқ шевалари луғати.pdf')
texts = {x['id']: (ROOT / (x['id'] + '.txt')).read_text().split('\f') for x in manifest}
texts['E1'] = Path('/workspace/research/qashqadaryo/Q4.txt').read_text().split('\f')

def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def ref(source, page, anchor):
    text = texts[source][page - 1]
    assert anchor in text, (source, page, anchor)
    lines = text.splitlines()
    line = next(i for i, s in enumerate(lines) if anchor in s)
    excerpt = '\n'.join(lines[max(0, line - 1):line + 5])
    return {'source': source, 'pdf_page': page,
            'printed_page': page + 886 if source == 'J4' else (None if source == 'J3' else page),
            'anchor_extracted': anchor, 'evidence_extracted': excerpt}

sources = {
    'J1': {'title': 'O‘zbek shevalari tadqiqotlari: amaliyot, metodologiya va yangicha yondashuv',
           'editor': 'Sh. Sirojiddinov', 'year': 2022, 'publisher': 'Donishmand ziyosi, Toshkent',
           'kind': '2022-yil 21-maydagi II respublika ilmiy-nazariy konferensiyasi materiallari',
           'duplicate_of': ['samarqand/M4'],
           'read_pages_this_round': list(range(148, 156)) + list(range(189, 193)) + [69, 70, 71, 72, 73, 74],
           'articles': [
               {'id': 'J1-A', 'title': 'Forish tumani milliy xalq o‘yinlari leksikasiga doir', 'authors': ['M. Abdiyev', 'R. Nabiyev'], 'pdf_pages': [148, 149, 150, 151], 'read': 'to‘liq', 'field_material_period': '2019–2021; maqola adabiyotlar ro‘yxatida ko‘rsatilgan'},
               {'id': 'J1-B', 'title': '«Devonu lug‘otit turk»da mavjud bo‘lib ayrim shevalarda qo‘llanilayotgan so‘zlar xususida', 'authors': ['Nurmurod Chiniqulov'], 'pdf_pages': [152, 153, 154, 155], 'read': 'to‘liq; Jizzax uchun faqat aniq Forish belgili birliklar olindi'},
               {'id': 'J1-C', 'title': 'Dialektal leksikada sinonimiya', 'authors': ['Feruza Toraxanovna Musayeva'], 'pdf_pages': [189, 190, 191, 192], 'read': 'to‘liq; Zominning tirjiq so‘zi olinadi'}],
           'reading_limit': 'Butun 216 sahifa so‘zma-so‘z o‘qilgan emas. Hududiy qidiruv va ko‘rsatilgan maqolalar asos bo‘ldi. Denov hamda Dardoq maqolalaridagi barcha misollar Jizzax materiali emas.'},
    'J2': {'title': 'O‘zbek dialektologiyasi fanidan o‘quv-uslubiy majmua', 'author': 'Sh. Xudoyqulova',
           'year': 2008, 'publisher': 'Guliston davlat universiteti', 'kind': 'umumiy dialektologiya kursi',
           'duplicate_of': ['qashqadaryo/Q2', 'samarqand/M2'],
           'read_pages_this_round': [31, 34, 38, 46, 62], 'context_page': [33],
           'reading_limit': 'Tasnif sahifalari o‘qildi; butun 88 sahifa qayta to‘liq o‘qilmadi. Testlardagi yulduzchalar mustaqil dalil emas. O‘quv topshiriqlari bajarish buyrug‘i sifatida olinmadi.'},
    'J3': {'title': 'O‘zbek dialektologiyasi (to‘ldirilgan va qayta nashri)', 'author': 'Yoqub Saidov',
           'year': 2022, 'publisher': 'Sadriddin Salim Buxoriy, Durdona, Buxoro', 'kind': 'umumiy o‘quv qo‘llanma',
           'read_pages_this_round': [1, 2, 5, 54, 63, 84],
           'reading_limit': 'PDF 96 sahifali, 2-sahifada bibliografik hajm 74 b. deb yozilgan. Bu farq bartaraf etilmagan; havolalar PDF tartib raqamida. Butun kitob o‘qilgan emas.'},
    'J4': {'title': 'Zomin tumani «j»lovchi shevasida uchraydigan ayrim iboralar tahlili',
           'author': 'Mahmudjon Abdurahmanov', 'year': 2021,
           'publisher': 'Scientific Progress, 2(8), 887–890', 'issn': '2181-1601',
           'kind': 'Zomin iboralari haqidagi maqola', 'read_pages_this_round': [1, 2, 3, 4],
           'reading_limit': 'To‘liq o‘qildi. Har ibora uchun aniq qishloq, suhbatdosh va audio yozuv berilmagan; faqat Zominga xosligi mustaqil isbotlanmagan.'}}
for source in manifest:
    source.update(sources[source['id']])
    source['text_path'] = str(ROOT / (source['id'] + '.txt'))
supplement = {'id': 'E1', 'title': 'O‘zbek xalq shevalari lug‘ati', 'editor': 'Sh. Sh. Shoabdurahmonov',
              'year': 1971, 'publisher': 'Fan, Toshkent', 'pages': 410, 'pdf_path': str(old_path),
              'text_path': '/workspace/research/qashqadaryo/Q4.txt',
              'sha256': hashlib.sha256(old_path.read_bytes()).hexdigest(),
              'kind': 'oldin foydalanuvchi yuborgan qo‘shimcha manba; yangi to‘rtta PDFdan biri emas',
              'checked_entries_pdf_pages': [13, 22, 34, 49, 53, 56, 69, 74, 91, 94, 195, 207, 220, 244, 258, 272],
              'visual_checked_pages_this_round': [53, 195, 272],
              'reading_limit': 'Tanlangan hududiy lug‘aviy maqolalar tekshirildi, 410 sahifa to‘liq qayta o‘qilmadi. Tarixiy ma’muriy hududlar bugungi chegaralar bilan aynan teng emas.'}
save('MANBALAR.json', {'uploaded_sources': manifest, 'supplementary_sources': [supplement],
                     'read_claim': 'Matnni ajratish va qidirish to‘liq o‘qish degani emas.',
                     'transcription_policy': 'Manba yozuvi dalil parchasida saqlanadi. Latincha ko‘rsatish shakllari soddalashtirilgan; ular IPA yoki tekshirilgan audio transkripsiya emas.'})
with (ROOT / 'SAHIFALAR.jsonl').open('w') as stream:
    for source in manifest:
        for n in range(1, source['pages'] + 1):
            stream.write(json.dumps({'source': source['id'], 'pdf_page': n,
                'printed_page': n + 886 if source['id'] == 'J4' else (None if source['id'] == 'J3' else n),
                'text_extracted': texts[source['id']][n - 1]}, ensure_ascii=False) + '\n')

lexicon = []
def word(form, meanings, region, source, page, anchor, note='', variants=None):
    lexicon.append({'id': f'JL{len(lexicon)+1:02}', 'display_form': form, 'variants': variants or [],
        'meanings': meanings, 'region': region, 'exclusive_to_region': None,
        'evidence_type': 'hudud nomi aniq berilgan yozma qayd',
        'modern_usage_verified': False, 'audio_verified': False,
        'normalization': 'Soddalashtirilgan latincha ko‘rsatish shakli; aniq manba yozuvi source_refs ichida.',
        'usage_note': note, 'source_refs': [ref(source, page, anchor)]})
word('qanquv', ['kesatiq; chandish mazmunidagi gap'], 'Zomin qishloq shevalari; maqola «j»lovchi nutqqa bag‘ishlangan', 'J4', 2, '“qanquv” deyiladi', 'Kesatiq ohangini oddiy betaraf hazil bilan tenglashtirmaslik kerak.')
word('inmoq', ['yuqoridan pastga tushmoq', 'ayrim kontekstlarda biror joyga borib kelmoq'], 'Forish; aniq qishloq berilmagan', 'J1', 154, 'kelmoq” biror joy', 'Manbadagi bozor misoli adabiy yozuvga yaqin; to‘liq fonetik nutq yozuvi emas.', ['inib kelmoq', 'inishdi', 'indi (endi)'])
word('tirjiq', ['ozg‘in; salbiy munosabat bilan aytiladi'], 'Zomin; lahja ichidagi kichik hudud berilmagan', 'J1', 191, 'Oz­g‘in – tirjiq' if 'Oz­g‘in – tirjiq' in texts['J1'][190] else 'tirjiq dialek', 'Ozg‘in so‘zining betaraf muqobili sifatida avtomatik ishlatilmaydi.')
for form, meanings, region, page, anchor, note in [
    ('agnamoq', ['anglamoq; tushunmoq'], 'Jizzax; Qashqadaryo bilan birga qayd etilgan', 13, 'агнамоц агнамо', 'Jizzax misoli ham bor; faqat Jizzaxga xos emas.'),
    ('ochyurak', ['och qoringa; ovqat yemagan holda'], 'Jizzax; Xazorasp bilan qiyoslangan', 22, 'ачйурэк ачюрак', 'Jizzax bosh shakli эчйурэк, gap misolida очйурэккэ. Ochko‘z degani emas; Xazoraspning ачюрак shakli Jizzaxniki qilib olinmadi.'),
    ('obdish', ['qaynagan suv'], 'Jizzax; Qashqadaryo va Qorabuloq bilan birga', 34, 'обдъш обдиш', 'Manbada objish//obdish variantlari ham berilgan. Hozir qaynayotgan suv degan ma’noga cheklanmaydi.'),
    ('boshliq', ['yugan'], 'Zomin', 49, 'бэшлыц бошлиц', 'Ot jihozi ma’nosida. Rahbar ma’nosidagi barcha boshliq so‘zlarini yugan deb talqin qilmaslik kerak.'),
    ('bixtiy', ['yashirin'], 'Jizzax', 53, 'бъхтъй бихтий', 'Manbaning standart kirillcha shakli бихтий; talaffuz audioda tekshirilmagan.'),
    ('bichcha', ['picha; ozgina'], 'Forish', 53, 'бъччэ бичча', 'Manbada qisqa gaplashish misoli bor; latincha ko‘rsatish fonetik belgilarni to‘liq saqlamaydi.'),
    ('butancha', ['oshqovoq; ruscha izohda muskat oshqovog‘i'], 'Zomin', 56, 'бетэнчэ бутанча', 'O‘simlik nomi; aniq biologik tur manbadan tashqari tekshirilmagan.'),
    ('gulishxoni', ['lag‘mon'], 'Forish', 69, 'гулъшхонъ гулишхони', 'Taom nomi.'),
    ('gilak', ['qiyma'], 'Forish', 74, 'гилaк' if 'гилaк' in texts['E1'][73] else 'гилак', 'Taom masallig‘i.'),
    ('dusaq', ['ikki yoshli qo‘y'], 'Forish', 91, 'дусац', 'Har qanday qo‘y ma’nosida emas; chorvachilik atamasi.'),
    ('elarmak', ['o‘qraymoq; xafa yoki jahlli qaramoq'], 'Forish', 94, 'елармэк элармак', 'Betaraf qarash emas; salbiy hissiy tusga ega.'),
    ('nemana', ['nima'], 'Forish', 195, 'немэиэ немана', 'OCR bosh shaklni xato ajratgan; sahifa tasvirida нэмэнэ, oddiy yozuvi немана.'),
    ('paymana', ['tarozi'], 'Zomin', 207, 'паймана (Зомин)', 'O‘lchov jihozi; sig‘im o‘lchovi ma’nosi bu qaydda yo‘q.'),
    ('pidina', ['yalpiz'], 'Forish; Qarshi va Laqay bilan birga', 220, 'пъдъна пидина', 'Bir necha hududga umumiy qayd; faqat Forishniki deb bo‘lmaydi.'),
    ('tavunmak', ['bo‘ysunmoq', 'sig‘inmoq'], 'Zomin', 244, 'тавунмак', 'Manbada ikki alohida ma’no va ularning misollari bor; kontekst bilan farqlanadi.'),
    ('tigalamak', ['quyoshda isinmoq'], 'Forish', 258, 'тыгаламак', 'Issiqlik manbai quyosh ekanligi ma’noning bir qismi.'),
    ('faqer', ['chelak'], 'Forish, Safarota qishlog‘i', 272, 'фа^ер', 'OCRdagi ^ tasvirdagi қ harfiga mos. Kattalashtirilgan sahifa parchasida tekshirildi.')]:
    word(form, meanings, region, 'E1', page, anchor, note)
save('LUGAT.json', lexicon)

idioms = []
def idiom(form, meaning, literal, pages, anchors, tone, note, variants=None, senses=None):
    idioms.append({'id': f'JI{len(idioms)+1:02}', 'display_form': form,
        'variants': variants or [], 'region': 'Zomin tumani «j»lovchi shevasi; aniq qishloq berilmagan',
        'genre': 'ibora', 'meaning': meaning, 'literal': literal, 'senses': senses or [],
        'tone': tone, 'usage_note': note, 'exclusive_to_region': None,
        'modern_usage_verified': False,
        'source_refs': [ref('J4', p, a) for p, a in zip(pages, anchors)]})
idiom('Arqag‘a qarab kuvshegen', 'Gapidan qaytaveradigan, so‘zida turmaydigan kishi haqida.', 'Orqaga qarab kavshagan.', [3], ['Arqag’a qarab kuvshegen'], 'tanqidiy', 'Chorva haqidagi metafora; odamga nisbatan malomat ohangi bor.')
idiom('At basadi, shaqa jenchedi', 'Asosiy ishni bajarmagan yordamchining ish to‘liq bitishidagi hissasini ta’kidlash.', 'Ot bosadi, shoxa yanchadi.', [3], ['“at basadi, shaqa jenchedi'], 'yordamchining hissasini e’tirof etish', 'Xirmonda otga yanchilmagan donni panshaxa bilan surib turish manzarasi asos bo‘lgan.')
idiom('Baltasi tashqa tiydi', 'Pand yeb, xafsalasi pir bo‘lishi va shashti qaytishi.', 'Boltasi toshga tegdi.', [3], ['“Baltasi tashqa'], 'afsus yoki tanqid; kontekstga bog‘liq', 'Kengroq o‘zbek nutqida ham uchrashi mumkin; faqat Zomin uchun ajratilgan ibora deb da’vo qilinmaydi.')
idiom('Jelka tomiri juvon', 'O‘jar, qaysar, bo‘yin egmaydigan kishi haqida.', 'Yelka tomiri yo‘g‘on.', [3, 4], ['“Jelka tomiri juvon', 'Karimding jelke tamiri'], 'tanqidiy', 'Sarlavhadagi jelka/tomiri/juvon bilan gapdagi jelke/tamiri/juvan farqi saqlanadi; tana tavsifi emas.', ['jelke tamiri juvan'])
idiom('Mo‘yin adam', 'O‘jar, qaysar, bo‘yin egmaydigan odam.', None, [3, 4], ['“mo’yin adam”', 'Shunday egilmaydigan'], 'tanqidiy', 'Ma’no qo‘shni izohdan anglashiladi. Mo‘yin so‘zini bo‘yin bilan aynan tenglashtirish yoki alohida lemma tarjimasi dalillanmagan.')
idiom('Sabang‘a tashtash', 'Ko‘pkari ma’nosi ham, maqsadga yetish ma’nosi ham mavjud.', 'Somonga tashlash.', [4], ['“sabang’a tashtash'], 'ko‘chma ma’noda maqtov', 'Kontekstsiz so‘zma-so‘z tarjima ko‘chma ma’noni yo‘qotadi.', ['sabang‘a teshtesh'], [
    {'id': 1, 'domain': 'uloq-ko‘pkari', 'meaning': 'Uloqni somon bilan belgilangan marraga tashlash.'},
    {'id': 2, 'domain': 'ko‘chma ma’no', 'meaning': 'Marraga yoki maqsadga yetish; ishni qoyilmaqom bajarish.'}])
idiom('Avruvda chanchuv jaman, gepte qanquv', 'Gapdagi kesatiqning og‘riqliligini kasallikdagi sanchiq bilan qiyoslash.', 'Kasallikda sanchiq yomon, gapda kesatiq. (Tahririy mazmuniy talqin.)', [2], ['“Avruvda chanchuv jaman, gepte'], 'kesatiq haqida obrazli mulohaza', 'Tahririy talqin manbaning so‘zma-so‘z tayyor tarjimasi emas.')
idioms[-1]['genre'] = 'maqolsimon obrazli ifoda; janr yorlig‘i tahririy'
save('IBORALAR.json', idioms)

games = []
def game(form, kind, description, page, anchor, stage=None):
    games.append({'id': f'JO{len(games)+1:02}', 'name': form, 'kind': kind,
        'region': 'Forish; maqolada aniq qishloq kesimida ajratilmagan',
        'description': description, 'besh_tosh_stage': stage,
        'context': 'xalq o‘yinlari; oddiy kundalik gapga avtomatik kiritilmaydi',
        'exclusive_to_region': None, 'modern_usage_verified': False,
        'source_refs': [ref('J1', page, anchor)]})
for form, kind, description, anchor in [
    ('Jambil', 'oddiy o‘yin', 'Tosh bilan o‘ynaladigan o‘yin sifatida sanalgan; batafsil qoida berilmagan.', '“Jambil”'),
    ('Besh tosh', 'oddiy o‘yin', 'Besh dona tosh, ikki yoki ko‘proq ishtirokchi; maqolada o‘nta shart tasvirlangan.', '“Besh'),
    ('Tosh ko‘tarar', 'oddiy o‘yin', 'Tosh bilan o‘ynaladigan guruh; batafsil qoida berilmagan.', 'Tosh ko‘tarar'),
    ('Chillik o‘yini', 'oddiy o‘yin', 'Yog‘och yoki suyak bilan bajariladigan guruhda sanalgan.', 'Chillik o‘yini'),
    ('Oq suyak', 'oddiy o‘yin', 'Yog‘och yoki suyak bilan bajariladigan guruhda sanalgan.', 'Oq suyak'),
    ('Oshiq o‘yin', 'oddiy o‘yin', 'Yog‘och yoki suyak bilan bajariladigan guruhda sanalgan.', 'Oshiq o‘yin'),
    ('Xo‘rozlar jangi', 'oddiy o‘yin', 'Hayvon nomlari bilan bog‘liq guruh; qoidasi bu maqolada berilmagan.', 'Xo‘rozlar jangi'),
    ('Podachi', 'oddiy o‘yin', 'Hayvon nomlari bilan bog‘liq guruh.', '“Podachi”'),
    ('Eshak mindi', 'oddiy o‘yin', 'Hayvon nomlari bilan bog‘liq guruh.', 'Eshak mindi'),
    ('Ilon dumi', 'oddiy o‘yin', 'Hayvon nomlari bilan bog‘liq guruh.', 'Ilon dumi'),
    ('Poda lov-lov', 'oddiy o‘yin', 'Hayvon nomlari bilan bog‘liq guruh.', 'lov-lov')]:
    game(form, kind, description, 150, anchor)
for form in ['Gashtak ko‘pkari', 'Darveshona', 'Yil boshi', 'Urug‘ qadash', 'Ko‘rpa qopladi', 'Cho‘nka shuvoq']:
    game(form, 'marosim o‘yini', 'Marosim o‘yinlari ro‘yxatida berilgan. Cho‘nka shuvoqning qo‘shiq matni ham keltirilgan; qolganlar uchun batafsil qoida berilmagan.', 151, form)
for form, stage, description in [
    ('bo‘ri', 6, 'Bosh va o‘rta barmoq yerga, ko‘rsatkich barmoq ustga qo‘yiladi; tanlangan «bo‘ri» tosh bir zarb bilan o‘tkaziladi.'),
    ('ayri', 7, 'Ko‘rsatkich va o‘rta barmoq ayri shaklda yerga qo‘yiladi; oltinchi shart kabi bajariladi.'),
    ('qafas', 8, 'Barmoqlar qafas shaklida qo‘yiladi; toshlar ularning oralaridan o‘tkaziladi.'),
    ('ko‘za', 9, 'Bosh va ko‘rsatkich barmoq doira hosil qiladi; toshlar «ko‘za» ichiga tushiriladi.'),
    ('o‘ngmi-chap', 10, 'Toshlar havoga otilib qo‘llarning ustki qismida ilib olinadi.')]:
    game(form, 'Besh tosh sharti atamasi', description, 150, '“' + form + '”', stage)
save('OYIN_ATAMALARI.json', games)

samples = []
for page, dialect, standard, translation_kind, note in [
    (3, 'Erkek adamam arqag’a qarab kuvshayma ?', 'Erkak odam ham gapida turmaydimi?', 'muallif talqini', 'Tanqidiy ritorik savol. Erkak haqidagi ayni misol botning barcha foydalanuvchiga murojaat andozasi emas.'),
    (3, 'Ongardinam baltasi tashqa  tiydi, endi barmas', 'O‘ng‘orning ham boltasi toshga tegdi, endi bormasa kerak.', 'muallif tarjimasi; apostroflar tahrirlandi', 'Barmas → bormasa kerak muallifning kontekstual talqini; barcha -mas shakli uchun avtomatik taxmin ma’nosi emas.'),
    (4, 'Karimding jelke tamiri juvan-da, uriship qapti', 'Karimning yelka tomiri yo‘g‘on-da, urishib qolibdi.', 'muallif tarjimasi; apostroflar tahrirlandi', 'Ibora qaysarlikni bildiradi; tanqidiy ohang.'),
    (4, 'Tilov ulaqti sabang’a tashtedi', 'Tilov uloqni somonga tashladi.', 'muallif tarjimasi', 'Uloq-ko‘pkari konteksti; somon bilan belgilangan marra.'),
    (4, 'Bugungu mayliste siz sabang’a\nteshtediniz', 'Bugungi majlisda siz hammani qoyil qoldirdingiz.', 'muallif tarjimasi', 'Ko‘chma ma’no; maqtov.')]:
    assert dialect in texts['J4'][page-1]
    samples.append({'id': f'JN{len(samples)+1:02}', 'dialect_extracted': dialect,
        'display': re.sub(r'\s+', ' ', dialect), 'standard_meaning': standard,
        'translation_kind': translation_kind, 'region': 'Zomin «j»lovchi',
        'note': note, 'source_refs': [ref('J4', page, dialect.splitlines()[0])]})
samples.append({'id': 'JN06', 'dialect_extracted': 'men bugun\nbozorga inib keldim',
    'display': 'men bugun bozorga inib keldim', 'standard_meaning': 'Men bugun bozorga borib keldim. (Kontekstga qarab «tushib keldim» ham mumkin.)',
    'translation_kind': 'tahririy mazmuniy talqin', 'region': 'Forish',
    'note': 'Manba adabiy yozuvda bergan misol; to‘liq fonetik transkripsiya emas.',
    'source_refs': [ref('J1', 154, 'bozorga inib keldim')]})
song = 'Cho‘nka shuvoq-shuvoqqa,\n   Otang ketdi tuvoqqa,\n   Tuvoq sindi, kul bo‘ldi.\n   Cho‘nka shuvoq pul bo‘ldi.'
assert song in texts['J1'][150]
samples.append({'id': 'JN07', 'dialect_extracted': song, 'region': 'Forish maqolasidagi marosim qo‘shig‘i',
    'genre': 'qo‘shiq parchasi', 'note': 'Kundalik suhbat yozuvi emas. Qofiya va qo‘shiq shakllaridan umumiy grammatika qoidasi chiqarilmaydi.',
    'source_refs': [ref('J1', 151, 'Cho‘nka shuvoq-shuvoqqa')]})
save('NUTQ_NAMUNALARI.json', samples)

grammar = []
for standard, observed, page, anchor, note in [
    ('yelka', 'jelka / jelke', 3, '“Jelka tomiri juvon', 'So‘z boshidagi y→j; jelke gap varianti 4-sahifada.'),
    ('yo‘g‘on', 'juvon / juvan', 3, '“Jelka tomiri juvon', 'So‘z boshidagi j hamda g‘ o‘rnidagi v ayni birikmada. Juvonning adabiy tildagi boshqa ma’nosi bilan chalkashtirmaslik kerak.'),
    ('yanchadi', 'jenchedi', 3, '“at basadi, shaqa jenchedi', 'Muallif birikma tarjimasidagi qiyos; boshqa barcha y va unlilar uchun qoida emas.'),
    ('gapda', 'gepte', 2, '“Avruvda chanchuv jaman, gepte', 'Maqolsimon ifodadagi butun shakl; mustaqil yalang‘och gep lemma bu yerda qayd etilmagan.'),
    ('yomon', 'jaman', 2, '“Avruvda chanchuv jaman, gepte', 'So‘z boshidagi y→j va unli farqi ayni misolda.'),
    ('Karimning', 'Karimding', 4, 'Karimding jelke tamiri', 'Qaratqich qo‘shimchasi shu ism va gapda -ding. Hamma so‘zdagi ng harflarini d ga almashtirish dalili emas.'),
    ('uloqni', 'ulaqti', 4, 'Tilov ulaqti', 'Tushum qo‘shimchasi ayni kontekstda -ti.'),
    ('urishib qolibdi', 'uriship qapti', 4, 'Karimding jelke tamiri', 'Ravishdosh va ko‘makchi fe’lning qisqargan ko‘rinishi shu gapda.'),
    ('bugungi', 'bugungu', 4, 'Bugungu mayliste', 'Unli mosligi shu misolda; butun hudud uchun to‘liq garmoniya paradigmasi aniqlanmagan.'),
    ('majlisda', 'mayliste', 4, 'Bugungu mayliste', 'Muallifning juft gapida o‘zak va qo‘shimcha farqi mavjud.'),
    ('orqaga', 'arqag‘a', 3, 'Arqag’a qarab kuvshegen', 'Manba arqag’a yozadi; tahririy ko‘rsatishda apostrof standartlashtirilgan.'),
    ('kavshagan', 'kuvshegen', 3, 'Arqag’a qarab kuvshegen', 'Leksik shakl qiyosi; alohida tovush o‘zgarishlarini hammaga yoyish uchun yetarli emas.'),
    ('somonga', 'sabang‘a', 4, '“sabang’a tashtash', 'Leksik va kelishik shakli birga farqlanadi; barcha somon yozuvlarini avtomatik almashtirish yo‘q.')]:
    grammar.append({'id': f'JG{len(grammar)+1:02}', 'standard_context_form': standard,
        'attested_form_display': observed, 'region': 'Zomin «j»lovchi; J4 misollari',
        'evidence_level': 'birikma/gapdagi qayd, umumiy qoida emas',
        'automatic_global_replacement': False, 'note': note, 'source_refs': [ref('J4', page, anchor)]})
for standard, observed, anchor in [('pastga tushishdi', 'inishdi', 'shevada (Forish) inishdi'), ('pastga tushdi', 'indi (endi)', 'shevada (Qipchoq, Forish) indi')]:
    grammar.append({'id': f'JG{len(grammar)+1:02}', 'standard_context_form': standard,
        'attested_form_display': observed, 'region': 'Forish; J1-B',
        'evidence_level': 'maqolada Forish nomi bilan berilgan shakl',
        'automatic_global_replacement': False, 'note': 'Endi vaqt bildiruvchi adabiy so‘zning har bir holati tushdi deb tarjima qilinmaydi.',
        'source_refs': [ref('J1', 154, anchor)]})
save('GRAMMATIKA.json', grammar)

profiles = [
    {'id': 'JP1', 'region': 'Jizzax shahri / shahar tipidagi sheva',
     'classification': 'Qarluq-chigil-uyg‘ur; Reshetov tasnifining Toshkent guruhi.',
     'source_refs': [ref('J2', 34, 'Toshkent guruhi:'), ref('J2', 38, '2.Toshkent guruhi')],
     'coverage_limit': 'Bu tasnif butun viloyatni bir xil sheva qilmaydi. Jizzax shahar suhbatining to‘liq korpusi berilmagan.'},
    {'id': 'JP2', 'region': 'Zomin «j»lovchi qishloq nutqi',
     'classification': 'Maqolada asosan qipchoq; kichik qism aholida qarluq ham qayd etilgan.',
     'source_refs': [ref('J4', 1, 'asosan qipchoq lahjasida')],
     'coverage_limit': 'Iboralar va 5 gap bor; aniq qishloq va suhbatdoshlar kesimida taqsimot yo‘q. Zominning barcha nutqi j-lovchi deb olinmaydi.'},
    {'id': 'JP3', 'region': 'Forish',
     'classification': 'Turfa shevalar mavjudligi aytilgan; bu to‘plam barcha Forish materialini bitta lahjaga biriktirmaydi.',
     'source_refs': [ref('J1', 149, 'turfa xil shevalari'), ref('J3', 63, 'Xorazm, Forish')],
     'coverage_limit': 'O‘yin terminlari dala ekspeditsiyasidan; inmoq maqolada aniq belgilangan; oddiy so‘zlar asosan 1971-yil lug‘atidan. Cho‘ziq unli misollari Xorazm/Forish/shimoliy guruh uchun umumiy berilgan, alohida Forish yozuvi emas.'},
    {'id': 'JP4', 'region': 'Baxmal / G‘allaorol',
     'classification': 'J2 test variantida sharqiy qipchoq geografiyasi ichida sanalgan; J3 baxmal shevasini qipchoq dialekti misoliga qo‘shadi.',
     'source_refs': [ref('J2', 62, 'qipchoq shevalari, Baxmal'), ref('J3', 5, 'baxmal, ming')],
     'coverage_limit': 'Lug‘at yoki hozirgi nutq namunasi bo‘lmaganligi sababli alohida tayyor so‘zlashuv profili tuzilmadi.'},
    {'id': 'JP5', 'region': 'Joy nomi aniqlashtiriladigan o‘g‘uz qaydlari',
     'classification': 'J2 Forishdagi «Bog‘ot»ni shimoliy o‘g‘uz guruhiga kiritadi; J3 Jizzax yaqinida «Bodan» qishlog‘ini aytadi.',
     'source_refs': [ref('J2', 31, 'Forish tumanidagi Bog’ot'), ref('J3', 84, 'Bodan qishloida')],
     'coverage_limit': 'Bog‘ot va Bodan aynan bir joy yoki Bog‘donning xatosi ekanligi tekshirilmagan. Nomlar dalilsiz birlashtirilmaydi.'}]
save('HUDUDIY_PROFILLAR.json', profiles)
save('TEKSHIRILADIGAN_DAVOLAR.json', [
    {'claim': 'J4dagi iboralar faqat Zominda uchraydi.', 'status': 'mustaqil tasdiqlanmagan', 'source_refs': [ref('J4', 1, 'faqat  zominliklar')], 'handling': 'Mahalliy qayd saqlanadi; exclusivity tasdiqlanmaydi.'},
    {'claim': 'J2dagi test yulduzchalari hammasi to‘g‘ri javobdir.', 'status': 'ishonchsiz', 'source_refs': [ref('J2', 62, 'A.* unlilarning cho')], 'handling': 'Labial garmoniya uchun unli cho‘ziqligi yulduzlangan; test variantidan ishonchli avtomatik qoida chiqarilmadi.'},
    {'claim': 'Zomin etimologiyasidagi y→z butun shevaning almashtirish qoidasidir.', 'status': 'etimologik taxmin; sinxron qoida sifatida olinmaydi', 'source_refs': [ref('J4', 1, '“yam”')], 'handling': 'Botda umumiy almashtirishga aylanmaydi.'},
    {'claim': 'Hududdagi odamlarning fe’li maqoladagi umumiy tavsifga bir xil mos.', 'status': 'lingvistik qoidaga asos bo‘lmaydi', 'source_refs': [ref('J4', 2, 'qo’pollik, qo’rslik')], 'handling': 'Iboraning tanqidiy ohangi saqlanadi; aholiga umumiy xarakter yoki botga qo‘pollik yuklanmaydi.'},
    {'claim': '1971-yilgi lug‘at birliklari bugungi yoshlar nutqida ham bir xil faol.', 'status': 'hozirgi qo‘llanish tekshirilmagan', 'handling': 'Har bir birlikda modern_usage_verified=false.'},
    {'claim': 'J1dagi «jizza» hudud nomi Jizzaxdir.', 'status': 'hududiy qidiruvning yolg‘on mosligi', 'handling': 'Taom/mahsulot nomi mahalliy Jizzax dalili qilib olinmadi.'}])
save('OLDINGI_HUDUDLAR_QIYOS.json', {
    'exact_reuploads': [{'current': 'J1', 'previous': 'samarqand/M4'}, {'current': 'J2', 'previous': 'qashqadaryo/Q2; samarqand/M2'}],
    'shared_lexicon': [{'form': 'obdish', 'regions_in_source': ['Qashqadaryo', 'Jizzax', 'Qorabuloq'], 'ref': ref('E1', 34, 'обдъш обдиш')}, {'form': 'pidina', 'regions_in_source': ['Qarshi', 'Laqay', 'Forish'], 'ref': ref('E1', 220, 'пъдъна пидина')}],
    'notation_limit': 'Har xil manbalardagi j belgisi avtomatik bir xil fonetik belgi deb olinmaydi. Ushbu Zomin maqolasida j-lashish yelka/jelka kabi juftlik bilan ko‘rsatilgan.',
    'historical_boundaries': 'E1 lug‘atidagi 1971-yilgi ma’muriy hudud nomlari hozirgi viloyat chegaralarini bildirmaydi.'})

counts = {'uploaded_pdf_pages_indexed': sum(x['pages'] for x in manifest), 'lexicon_entries': len(lexicon),
    'lexicon_from_current_pdfs': 3, 'lexicon_from_previous_dictionary': len(lexicon)-3,
    'idioms': 6, 'proverb_like_expressions': 1, 'game_names_and_terms': len(games),
    'contextual_form_comparisons': len(grammar), 'speech_examples_including_song_fragment': len(samples)}
save('HISOBOT_STATISTIKASI.json', counts)
assert counts['uploaded_pdf_pages_indexed'] == 404
assert len(lexicon) == 20 and len(idioms) == 7 and len(games) == 22 and len(grammar) == 15
print(json.dumps(counts, ensure_ascii=False))
