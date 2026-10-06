"""Tadqiqotdan uslub profili va ajratib belgilangan nutq namunalarini tayyorlash."""
import json
import runpy
from pathlib import Path

P = Path(__file__).parent
research = runpy.run_path(str(P / 'build_research.py'))
ref, save = research['ref'], research['save']
lexicon = research['lexicon']

def cards(*forms):
    return [c['id'] for c in lexicon if c['form'] in forms]

profile = {
    'id': 'xorazm_janubiy_oguz_research_v1',
    'language': 'uz',
    'purpose': 'Kelajakdagi Telegram bot uchun manbali uslub tayanchi; bot kodi emas.',
    'default_region_candidate': 'Urganch–Xiva o‘g‘uz asosli',
    'default_region_is_editorial_choice': True,
    'all_xorazm_represented_by_default': False,
    'region_profiles_file': 'HUDUDIY_PROFILLAR.json',
    'lexicon_file': 'LUGAT.json',
    'grammar_file': 'GRAMMATIKA.json',
    'prompt_file': 'BOT_USLUB_PROMPTI.txt',
    'examples_file': 'NUTQ_NAMUNALARI.json',
    'tone': ['tabiiy va samimiy', 'suhbatdoshga mos hurmat', 'mazmunni aniq yetkazish'],
    'addressing': {
        'default': 'siz',
        'informal': 'Foydalanuvchi norasmiy uslubni tanlasa sen.',
        'kinship_terms': 'Aka/apa/ana/og‘o/biyi har kimga bezak murojaat qilib qo‘shilmaydi.',
        'evidence': [ref('X1', 10, 'dada, ota'), ref('X1', 36, 'ona ( Xorazmning'), ref('X1', 58, 'xo‘jayin')],
    },
    'initial_low_risk_vocabulary_candidates': cards(
        'assalom', 'arzimidi', 'aydin', 'dim', 'bitta / pitta',
        'buyun', 'arqoyin', 'biryonnon / biryannan', 'et', 'barak I / bo‘rak'),
    'vocabulary_policy': 'Nomzodlar gap ma’nosiga mos ishlatiladi; ularning hammasi har javobda qo‘llanmaydi.',
    'morphology_policy': 'Zamon, shaxs, son, inkor va yo‘nalish saqlanadi. To‘liq paradigma berilmagan fe’l taxmin bilan tuslanmaydi.',
    'generation_readiness': {
        'source_backed_rules_prepared': True,
        'native_speaker_validated': False,
        'modern_chat_frequency_measured': False,
        'audio_pronunciation_verified': False,
        'trained_model_weights': False,
        'telegram_bot_implemented_this_task': False,
    },
    'regional_separation': [
        'Urganch–Xiva profiliga shimoliy qipchoq j-lashishni umumiy qoida qilib qo‘shma.',
        'Gurlan/Amudaryo j-lovchi, y-lovchi va boshqa tarixiy tiplari alohida.',
        'Hazorasp–Yangiariq va aralash guruhlar uchun to‘liq mustaqil generatsiya profili hali tasdiqlanmagan.',
        'Tuman nomi o‘sha tumandagi barcha qishloqlar shevasi bir xil degani emas.',
    ],
    'orthography': {
        'output': 'O‘qilishi qulay oddiy lotin yozuvi; bir suhbatda izchil variant.',
        'scientific_transcription': 'Alohida dalil sifatida saqlanadi; chatga tasodifiy belgilar ko‘chirilmaydi.',
        'ocr': 'OCR boshliqning to‘g‘ri yozuvi yoki zamonaviy chat imlosi sifatida olinmaydi.',
    },
    'sense_selection_required': ['aka', 'apa/opo', 'ana', 'biyi', 'barak', 'bitta/pitta', 'bol', 'kadi', 'dars', 'eshik', 'axsham', 'alam'],
    'unsupported_generation_fallback': 'Ma’noni saqlab, oddiy o‘zbekcha gap va dalilli lokal birliklardan foydalan.',
    'website_imported_entries': 0,
}
save('USLUB_PROFILI.json', profile)

examples = []
def example(kind, surface, standard, sid, page, anchor, note, user_input=None):
    item = {'id': 'XN-' + str(len(examples) + 1).zfill(2), 'kind': kind,
            'readable_surface': surface, 'meaning_standard_uz': standard,
            'evidence': [ref(sid, page, anchor)], 'notes': note,
            'verbatim_scientific_transcription': False,
            'native_speaker_validated': False}
    if user_input is not None:
        item['user_input'] = user_input
    examples.append(item)

# Bosma misollar oddiy lotinga yaqinlashtirildi. Asl matn rasm va reference quote'da.
example('printed_example_editorial_reading', 'Assalom ata, yaxshimisiz? — Alakim balam.',
        'Salom ota, yaxshimisiz? — Vaalaykum assalom, bolam.', 'X1', 65, 'salomiga javob',
        'Ilmiy transkripsiyaning o‘qiladigan talqini. Ata/balam shu dialogdagi oilaviy-ijtimoiy munosabatga tegishli.')
example('printed_example_editorial_reading', 'Ishlaring aydinmi? Apang, akang aydin yuribmi?',
        'Ishlaring yaxshimi? Onang, otang yaxshi yuribdimi?', 'X1', 70, 'ay din',
        'Ota va ona nomlarini standart aka/opaga almashtirib yuborish katta semantik xato.')
example('printed_example_editorial_reading', 'Ahvallaring ejoyipmi axir?',
        'Ahvollaring yaxshimi?', 'X1', 149, 'ecayip',
        'Boshliq qavsida ejoyip, ilmiy shaklda ejayipga yaqin yozuv. Kundalik yagona imlo sifatida tasdiqlanmagan.')
example('printed_example_editorial_reading', 'Arzimidi.',
        'Arzimaydi.', 'X1', 24, 'Arzimidi', 'Bosma dialogda rahmatga javob.')
example('printed_example_editorial_reading', 'Emdolli, barip galingla.',
        'Yaxshi, borib kelinglar.', 'X1', 152, 'Emdalli',
        'Modal rozilik va ko‘plik/hurmat shakli; hamma javobda majburiy emas.')
example('printed_example_editorial_reading', 'Yenam pitta qo‘shib bering, kamlik atdi burinch.',
        'Yana ozgina qo‘shib bering, guruch kamlik qildi.', 'X1', 97, 'pitta',
        'Pitta miqdor; bir dona degani emas. Transkripsiya soddalashtirilgan.')
example('printed_example_editorial_reading', 'Bazardan et aldingmi?',
        'Bozordan go‘sht oldingmi?', 'X1', 155, 'Bazardan et', 'Et — shu gapda go‘sht.')
example('printed_example_editorial_reading', 'Eshika chiqip pitta aylanip galik.',
        'Tashqariga chiqib ozgina aylanib keldik.', 'X1', 159, 'E^ika',
        'Eshik — tashqari/hovli. Galik o‘tgan harakat; uni galali taklifiga aylantirmang.')

# Quyidagilar manbadagi tayanchlarga asoslangan MUALLIFLIK NOMZODLARI.
example('constructed_bot_candidate', 'Assalom! Ishlaringiz aydinmi?',
        'Salom! Ishlaringiz yaxshimi?', 'X1', 70, 'ay din',
        'Hurmat uchun -iz qo‘shilgan mualliflik adaptatsiyasi; bosma manbada butun shu jumla yo‘q.', 'Salom')
examples[-1]['evidence'].append(ref('X1', 25, 'Salom berish'))
example('constructed_bot_candidate', 'Arzimidi! Yana savol bo‘lsa, oyting.',
        'Arzimaydi! Yana savol bo‘lsa, ayting.', 'X1', 24, 'Arzimidi',
        'Oyting — oytmoq boshlig‘idan muharrirlik tuslanishi; butun javob mahalliy suhbatda tekshirilmagan.', 'Rahmat')
examples[-1]['evidence'].append(ref('X1', 57, 'Ddrd'))
example('constructed_bot_candidate', 'Emdolli. Biryonnon tushuntiraman: avval birinchi qadamni ko‘ramiz.',
        'Yaxshi. Batafsil tushuntiraman: avval birinchi qadamni ko‘ramiz.', 'X1', 96, 'batafsil',
        'Adabiy sintaksis va dalilli lokal so‘zlar bilan ehtiyotkor nomzod.', 'Buni tushuntirib ber')
examples[-1]['evidence'].append(ref('X1', 152, 'madal so‘z'))
example('constructed_bot_candidate', 'Emdolli, pitta qisqartiraman.',
        'Yaxshi, ozgina qisqartiraman.', 'X1', 97, 'ozgina',
        'Miqdor ma’nosining yangi vaziyatdagi qo‘llanishi; native tekshiruvdan o‘tmagan.', 'Juda uzun yozding')
examples[-1]['evidence'].append(ref('X1', 152, 'madal so‘z'))
example('constructed_bot_candidate', 'Arqoyin, biryonnon ko‘rib chiqamiz.',
        'Xotirjam bo‘ling, bir boshdan ko‘rib chiqamiz.', 'X1', 69, 'betashvish',
        'Suhbatga mos tinchlantirish nomzodi; butun jumla bosma iqtibos emas.', 'Hali tushunmadim')
examples[-1]['evidence'].append(ref('X1', 96, 'batafsil'))
example('constructed_bot_candidate', 'Buyun qaysi ishni avval qilamiz?',
        'Bugun qaysi ishni avval qilamiz?', 'X1', 106, 'bugun',
        'Zamon va shaxs o‘zgarishsiz; yengil lokal leksika.', 'Bugungi rejani tuzamiz')
example('constructed_bot_candidate', 'Dim yaxshi fikr. Keling, bosqichlarini belgilaymiz.',
        'Juda yaxshi fikr. Keling, bosqichlarini belgilaymiz.', 'X1', 127, 'sifatning ortirma',
        'Dim kuchaytirgichini o‘rinli bir marta qo‘llash nomzodi.', 'Botda viloyatni tanlash tugmasi bo‘lsin')
example('constructed_bot_candidate', 'Pitta kuting, savolingizni tekshiraman.',
        'Ozgina kuting, savolingizni tekshiraman.', 'X1', 97, 'ozgina',
        'Qisqa vaqtga miqdor so‘zini qo‘llash mualliflik nomzodi; tabiiyligi native tekshiruvga muhtoj.', 'Shu ma’lumotni tekshir')
save('NUTQ_NAMUNALARI.json', examples)

comparisons = [
    {'aspect':'Hozirgi davom zamon', 'xorazm_oguz':'Gayatirman/baryatirman turidagi shakllar.',
     'other_profiles':'Toshkent tavsifida barvomman/barvotti; Buxoro tavsifida baromman/baropti.',
     'limit':'Darslik misollari; bu har bir shahardagi barcha so‘zlovchilar paradigmasi emas.',
     'evidence':[ref('T1',47,'Toshkent'),ref('T1',47,'Buxoro'),ref('T1',47,'Xorazm')]},
    {'aspect':'Harakat nomi', 'xorazm_oguz':'-maq/-mak xarakterli: gitmak, oynamaq.',
     'other_profiles':'Qarluq guruhida -ish variantlari, qipchoqda -uv variantlari.',
     'limit':'Darslikning o‘zi adabiy ta’sir natijasida aralashishini qayd etadi; geografik universal qoida emas.',
     'evidence':[ref('T1',45,'Harakat nomi'),ref('T1',45,'aralash')]},
    {'aspect':'O‘g‘uz tarqalishi', 'xorazm_oguz':'Urganch–Xiva va boshqa guruhlar muhim markazlar.',
     'other_profiles':'Rajabov o‘g‘uz unsurlarini Jizzax yaqinidagi Bog‘don hamda boshqa hududlarda ham qayd etadi.',
     'limit':'Xorazm juda farq qiladi, lekin barcha xususiyatlari boshqa o‘zbek shevalarida mutlaqo yo‘q degani emas.',
     'evidence':[ref('T4',87,'Жиззах'),ref('X3',6,'Urganch-Xiva')]},
    {'aspect':'Shimol/janub', 'xorazm_oguz':'Janubiy profil bilan Gurlan/Amudaryo qipchoq tiplari farqlanadi.',
     'other_profiles':'Y-lovchi, j-lovchi, ə-lashgan va aralash tiplar Xorazm mintaqasining ichida ham bor.',
     'limit':'Surxondaryo, Qashqadaryo yoki Jizzaxning barcha aholisi bilan bitta sodda kontrast tuzish noto‘g‘ri.',
     'evidence':[ref('X3',5,'дж-lashgan'),ref('X3',6,'й-lashgan')]},
]
save('HUDUDLAR_QIYOSI.json',comparisons)

# Mazmuniy kontrastlar: keyinchalik bot natijasini baholashga tayanch,
# hozir hech qanday bot natijasi sinovdan o‘tkazilganini anglatmaydi.
checks = [
    ('aka','Xorazmga xos oilaviy kontekstda ota; har aka katta aka emas.', [('X1',10,'dada, ota')]),
    ('opo / apa','Ona; apka — opa bilan ajrat.', [('X1',36,'ona ( Xorazmning'),('X1',19,'opa,')]),
    ('ana','X1da buvi, X2 maqolida änä ona deb sharhlangan; kontekst va manba kerak.', [('X1',16,'buvi'),('X2',2,'Duväqsȉz')]),
    ('pitta qo‘shib bering','Ozgina qo‘shish; bir dona degani emas.', [('X1',97,'ozgina')]),
    ('barak','Ovqat chuchvara yoki kelin ko‘rdi marosimi; atrofdagi gap tanlatadi.', [('X1',75,'chuchvara'),('X1',75,'kelin ko‘rdi')]),
    ('biyi','Behi mevasi yoki kelinoyi; obyekt va fe’lga qarab.', [('X1',98,'xushbo‘y mevali'),('X1',98,'akaning xotini')]),
    ('kadi','Qovoq yoki sevgan kishi; X4 ikki ma’noni beradi.', [('X4',6,'“qovoq”')]),
    ('axsham','X1da kecha; avtomatik kechqurun emas.', [('X1',70,'kecha')]),
    ('et','Taom kontekstida go‘sht; tuman jadvallari variantlari ham saqlanadi.', [('X1',155,'go‘sht')]),
    ('eshika chiqish','Tashqariga/hovliga chiqish; fizik eshik bilan cheklanmaydi.', [('X1',159,'tashqariga nisbatan')]),
    ('Og‘zini suvi oqdi','X4da qattiq charchash; avtomatik yegisi kelish deb tarjima qilinmaydi.', [('X4',6,'Og‘zini suvi oqdi')]),
    ('Go‘zzini go‘ki so‘kildi','Qo‘shko‘pirda ko‘z bilan ishlashdan charchash; shunchaki har qanday charchoq emas.', [('X4',6,'tikuv')]),
    ('galali / barali','Birgalikdagi taklif; galik o‘tgan gapidan ajrat.', [('T1',67,'boraylik'),('X1',159,'gcihk')]),
    ('barjaqman','Kelasi zamon, birinchi shaxs; o‘tgan bordimga aylantirilmaydi.', [('T2',86,'barjaqman')]),
    ('-a / -na','Jo‘nalish ma’nosini saqlaydi; chiqish -nan bilan teng emas.', [('T2',86,'murodina'),('T1',35,'m, n')]),
    ('bo‘l / o‘l','B tushishi kuzatilgan bo‘lsa ham, har o‘ldi jumlasini bo‘ldi deb olma.', [('T2',85,'o’l')]),
    ('dushunmak','Boshliq va inkor-o‘tgan misol farqli; tushunmadimni tushundimga aylantirma.', [('X1',144,'tushunmadim')]),
    ('bilimmän','X1dagi yozuvni bilman deb qisqartirib inkor chiqarma; yordamchi bil- va to‘liq paradigma alohida masala.', [('X1',127,'bilimmein')]),
    ('k / t jaranglashishi','Tanlangan so‘zlar; turk, paxta, tesha, kamon, kema istisno.', [('T2',85,'tesha')]),
    ('Gurlan','Butun tuman j-lovchi degan universal xulosa yo‘q.', [('X3',5,'дж-lashgan'),('X3',6,'й-lashgan')]),
    ('bunga → minga','X4 takroriy, noaniq qatori; taxminiy tuzatishni fakt qilib qaytarma.', [('X4',6,'olmoshlarning')]),
    ('ejashdi / ejashmoq','X4 hazillashdi, X1 o‘chakishmoq: ma’nolarni kontekstsiz birlashtirma.', [('X1',149,'o‘chakishmoq')]),
]
save('MAZMUN_SINOVLARI.json', {'purpose':'Kelajakdagi bot uchun manbali ma’no kontrastlari; bot hali sinovdan o‘tkazilmagan.',
     'cases':[{'id':'XS-'+str(i).zfill(2),'trigger':trigger,'required_meaning':meaning,
               'evidence':[ref(*c) for c in cites]} for i,(trigger,meaning,cites) in enumerate(checks,1)]})
print('Profile, 16 examples, 4 comparisons and 22 meaning contrasts written.')
