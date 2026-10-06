"""Manbali Toshkent kartotekasi. PDF matni o'zgartirilmaydi; lotincha izohlar tahlilchiga tegishli."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
manifest = json.loads((ROOT / 'download_manifest.json').read_text())
pages = {s['id']: (ROOT / (s['id'] + '.txt')).read_text().split('\f')[:s['pages']] for s in manifest}
visual = {('T1', n) for n in [58,59,89,90,91]} | {('T2',68)} | {('T3',n) for n in [41,42]} | {('T4',n) for n in [1,149,206,208,224,269,272,276]}
printed_verified = {('T4',208):210,('T4',224):226,('T4',269):271,('T4',272):274,('T4',276):278}

def save(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

def ref(s, n, needle):
    raw = pages[s][n-1]
    # Whitespace-only normalization permits anchors spanning PDF line breaks.
    p, q = norm(raw), norm(needle)
    assert q in p, (s,n,needle)
    k = p.index(q)
    anchor = p[max(0,k-90):min(len(p),k+len(q)+180)]
    paper = n-1 if s == 'T1' and n >= 32 else n if s == 'T3' else printed_verified.get((s,n))
    return {'source_id':s,'pdf_page':n,'printed_page':paper,
            'anchor_normalized_whitespace':anchor,'search_needle':needle,
            'page_image_inspected':(s,n) in visual,
            'pdf_path':next(x['path'] for x in manifest if x['id']==s)}

collections = {n:[] for n in ['LUGAT','FONETIKA','GRAMMATIKA','NUTQ_NAMUNALARI','TEKSHIRILADIGAN_DAVOLAR','HUDUDIY_PROFILLAR','HUDUDLAR_QIYOSI']}

def add(cat, label, meaning, refs, area='Toshkent shahar', notes='', status='manbada_qayd_etilgan', latin=None, **extra):
    row={'id':cat[:3]+'-'+str(len(collections[cat])+1).zfill(3),
         'label':label,'meaning_or_analysis_uz':meaning,'area':area,'notes':notes,
         'evidence_status':status,'refs':[ref(*x) for x in refs],
         'exclusive_to_region':None,'audio_verified':False,
         'independent_modern_usage_verified':False,'model_training_performed':False,
         **extra}
    if latin is not None: row['approximate_latin_analyst_reading']=latin
    collections[cat].append(row)
    return row

# Qiyosiy jadval: aynan Toshkent ustuni. Asalari va tuxum ajratuvchi belgi emas.
for original, latin, meaning, scope in [
 ('muchicha','muchicha','musicha','variant'),('arg`imchoq',"arg‘imchoq",'tebranib uchiladigan arg‘imchoq','umumiy'),
 ('duxoba','duxoba','baxmal','variant'),('chumoli','chumoli','chumoli','umumiy'),
 ('asalari','asalari','asalari','umumiy'),('tuxum','tuxum','tuxum','umumiy'),
 ('yuray','yuray','yurak','fonetik_variant'),('choch','choch','soch','fonetik_variant')]:
    add('LUGAT',original,meaning,[('T2',68,original)],latin=latin,lexical_kind=scope,
        notes='Jadval hududlar qiyosi; boshqa shevalarda yo‘qligini isbotlamaydi.')

# T3 bevosita Toshkent deb belgilagan birliklar; etimologiya tasdiqlanmaydi.
for original, latin, meaning, note in [
 ('buvə','buva','bobo; katta ota','Andijondagi kətətə bilan qiyoslangan; buvi bilan almashtirilmasin.'),
 ('mən','man','men','ə belgisi oddiy a harfi bilan aynan teng emas.'),
 ('O’gъl',"o‘g‘il",'o‘g‘il','Fonetik yozuvdagi ъ oddiy lotin imlosida to‘liq ifodalanmaydi.'),
 ('o’chə',"o‘cha",'o‘choq','So‘z oxiridagi q saqlanmagan variant.'),
 ('o’pkə',"o‘pka",'o‘pka','Talaffuz varianti; alohida mahalliy predmet emas.'),
 ('o’rdəy',"o‘rday",'o‘rdak','So‘z oxiridagi k/y mosligi.'),
 ('chəch','chach','soch','T2 choch deb beradi; bu grafik/talaffuz farqi saqlanadi.'),
 ('sъgъr','sigir','sigir','Toshkent va Farg‘ona birgalikda berilgan.'),
 ('sъyъr','siyir','sigir','Toshkent va Farg‘ona birgalikda berilgan; hamma holatdagi g→y emas.'),
 ('kepeley','kepeley','kapalak','T3 kepeley, Farg‘ona kepelek deb qiyoslaydi.'),
 ('qudu','qudu','quduq','Leksik qayd; q undoshini har bir so‘zdan tushirish qoidasi emas.'),
 ('mъxnet','mixnat','mehnat','T1 mixnat shakli bilan qiyoslash mumkin.'),
 ('g’em',"g‘am",'g‘am','Unli belgisi fonetik transkripsiyada saqlanadi.'),
 ('zerъl','zeril','zarur','Faqat shu qaydga tayaniladi; zamonaviy faol qo‘llanish tekshirilmagan.'),
 ('əzъz','aziz','aziz','Toshkent va Farg‘ona uchun umumiy qayd.'),
 ('ъnag’əm',"inag‘am",'in’om','Noodatiy shakl: PDF tasvirida ham bor; botga avtomatik kiritilmasin.'),
 ('juvop','juvop','javob','Toshkent va Farg‘ona uchun umumiy qayd.'),
 ('qъmat','qimat','qimmat','Fonetik variant; faqat Toshkentga xos deb olinmaydi.'),
 ('nəxt','naxt','naqd','Jarangsizlanish va undoshlar birikmasi.'),
 ('dərəx','darax','daraxt','So‘z oxirida t yo‘q variant.'),
 ('bechərə','bechara','bechora','Umumiy so‘zning fonetik ko‘rinishi.')]:
    add('LUGAT',original,meaning,[('T3',41,original)],notes=note,latin=latin,
        status='tekshirish_kerak' if original=='ъnag’əm' else 'manbada_qayd_etilgan',lexical_kind='variant')
for original, latin, meaning, note in [
 ('shəhər - shəər-shə:r','shahar → sha:r','shahar','h tushishi va cho‘ziqlik; barcha h ga tatbiq etilmaydi.'),
 ('dos','dos','do‘st','Oxirgi undosh birikmasining qisqarishi.'),
 ('nərx','narx','narx','Ma’no o‘zgarmagan; talaffuz qaydi.'),
 ('əvəz','avaz','ovoz','Etimologiyasi shu sahifadagi arabcha degan umumlashtirishdan olinmadi.'),
 ('əyne','ayna','oyna','Lotinlashtirish taxminiy; ə fonetik belgisi yo‘qotilmasin.'),
 ('əgə','aga','ogoh','Qisqargan tarixiy qayd; faol nutqqa qo‘llashdan oldin tekshirish kerak.'),
 ('ərəm','aram','orom','Umumiy so‘zning talaffuz varianti.'),
 ('ərzъ','arzi','orzu','Unli belgilarining qiymati oddiy imloda aynan berilmagan.'),
 ('əptəv','aptav','oftob','f/p va oxirgi undosh farqi; etimologiya alohida tekshiriladi.'),
 ('chəqələ:','chaqala:','chaqaloq','T3 p55 Chəqəlog‘ boshqa shaklini ham beradi; ularni bir shaklga tuzatmadik.'),
 ('gərъmdorъ','garimdori','qalampir','T2 garmdori; T4 ham shu ma’noni beradi.')]:
    add('LUGAT',original,meaning,[('T3',42,original)],notes=note,latin=latin,lexical_kind='variant')

for label, latin, meaning, s, n, needle, note in [
 ('ой и','oyi','ona','T4',269,'ой и','Buvi/buvi=ona hududiy ma’nolari bilan aralashtirmaslik.'),
 ('са п ч а','sapcha','xomak','T4',269,'са п ч а','Manba xomak bilan tenglaydi; barcha xom meva degan kengaytirish yo‘q.'),
 ('қъйъқчэ','qiyiqcha','erkaklar beliga bog‘lanadigan, cheti gullangan belbog‘ materiali','T4',272,'ъ й ъ к ч э','Qo‘lyozilgan tasvir transkripsiyasi; PDF matn qatlami q harfini yo‘qotgan.'),
 ('Шэтъ','shoti','aravaning bir qismi','T4',276,'Ш э т ъ','Farg‘onadagi narvon ma’nosi bu yerga avtomatik ko‘chirilmaydi.'),
 ('chekch-chekich','chekich','nonni bezab teshadigan yog‘och va simli asbob','T3',57,'chekch-chekich','Nonper patdan yasalishi bilan dastlab farqlangan; keyinchalik ma’nolar yaqinlashgan.'),
 ('Pashsha','pashsha','pashsha (muxa)','T3',57,'Toshkent pashsha','Farg‘ona chivin (komar) deb qiyoslangan; barcha vodiyga birday tarqatilmasin.'),
 ('dovuchchə','dovuchcha','dovuchcha; hali pishmagan o‘rik','T3',55,'dovuchchə','Jadval Farg‘onada g‘ora deb beradi; meva turi boshqa lug‘at bilan ham tekshirilishi mumkin.'),
 ('qələmchə','qalamcha','qalamcha','T3',55,'qələmchə','Jadvalda kontekst yetarli emas: ma’no toraytirilmagan.'),
 ('Tuvog’','tuvog‘','qopqoq','T3',55,'Tuvog’','Jadvalning Toshkent ustuni; so‘nggi g‘/q qiymati tasvir tekshiruvi talab qiladi.')]:
    add('LUGAT',label,meaning,[(s,n,needle)],notes=note,latin=latin,
        status='tekshirish_kerak' if latin in ['dovuchcha','qalamcha','tuvog‘'] else 'manbada_qayd_etilgan',
        lexical_kind='leksik_yoki_semantik_variant')

# Bog‘dorchilik monologi: predmet emas, suhbatning kasbiy konteksti ham saqlanadi.
for original, latin, meaning, n, needle, note in [
 ('ъшкэм','ishkom','tok ko‘tariladigan ishkom',89,'ъшкэм','So‘z umumxalq tilida ham bor; monologdagi kasbiy qo‘llanish.'),
 ('пэйэ','poya','ishkomning tayanch poyasi',89,'Пэйэлэ','Kontekstga bog‘liq; odamning oyog‘i ma’nosi emas.'),
 ('бэгэз','bog‘oz','ishkomda poyalarga yonboshlatib bog‘lanadigan qism',89,'бэгэз','Aniq predmet tuzilishi etnografik tekshiruvga muhtoj.'),
 ('ъстэй','istay','tolning ingichka novdasi; bog‘lash uchun',90,'ъстэй дъйвуз','Monolog o‘zi ta’riflaydi.'),
 ('хэмтов (< хэмток)','xomtov','quyosh tushishi uchun tok barglarini yulish amali',90,'хэмтов (< хэмток)','Xomtov/xomtav yozuvi manba ichida almashadi; tibbiy tavsiya emas.'),
 ('хэвэзэ','havaza','ishkom ustida qush qo‘rishga va yotishga qilingan joy',90,'хэвэзэ','Bu monologdagi bog‘dorchilik ma’nosi.'),
 ('Тэртэрэй','tartaray','qush qochirish uchun chalinadigan narsa',90,'Тэртэрэй','Moslama qanday tuzilishi manbada batafsil ochilmagan.'),
 ('Пэкър','paqir','qo‘ng‘iroq sifatida ishlatilgan paqir',90,'Пэкърръ','Umumiy so‘z; shevaga mutlaq xos emas.'),
 ('шэкэрэцгуллъ','shakarangur','shakar angur nomi bilan izohlangan uzum',90,'шэкэрэцгуллъ','Muallif tojikcha shaklni qavsda keltiradi; botda har qanday uzumga qo‘llanmaydi.'),
 ('кондэ:','konda:','tok novdalarini yig‘ib, bog‘lab qo‘yish',90,'кондэ: дъйвуз','Ko‘mishdan oldingi amal; manbadagi o‘z ta’rifi.'),
 ('ЭЙМЭКЬ','aymaki','ko‘milmay, qishda ham qoldiriladigan tokka oid qayd',90,'ЭЙМЭКЬ','Nav nomimi yoki parvarish usulimi: monologning o‘zi yetarli emas.'),
 ('пэрхъш','parxish','tokni ko‘paytirishga oid amal',91,'пэрхъш','Aniq texnik usul tasdiqlanmagan; qatlamlash deb avtomatik kengaytirilmaydi.')]:
    add('LUGAT',original,meaning,[('T1',n,needle)],area='Toshkent; kitobdagi bog‘dorchilik monologi',notes=note,
        latin=latin,lexical_kind='kasbiy_kontekst',status='tekshirish_kerak' if latin in ['bog‘oz','aymaki','parxish'] else 'manbada_qayd_etilgan')

for label, explanation, refs in [
 ('e → i: mixnat, didi','Toshkent guruhi misollari; barcha e harfini i ga almashtirish qoidasi emas.', [('T1',58,'mixnat'),('T1',58,'didi')]),
 ('terak → teray','So‘z oxirida k/y mosligi.',[('T1',58,'teraj')]),
 ('ertak → ertay','So‘z oxirida k/y mosligi.',[('T1',58,'ertaj')]),
 ('bilak → bilay','So‘z oxirida k/y mosligi.',[('T1',58,'bilaj')]),
 ('chiroq → chiro:','So‘z oxiridagi q tushishi; ikki nuqta cho‘ziqlik belgisi.',[('T1',58,'чъро:')]),
 ('sariq → saru:','q tushishi bilan unli ham o‘zgaradi; oddiy q ni o‘chirish yetmaydi.',[('T1',58,'saru:')]),
 ('achchiq → achchu:','Manba ochchiq deb yozgan; transkripsiya va adabiy izoh ajratiladi.',[('T1',58,'ochchiq')]),
 ('qattiq → qattu:','q tushishi bilan yakuniy unli farqi.',[('T1',58,'qattu:')]),
 ('og‘zi → o:zi','g‘ tushishi va oldingi unlining cho‘ziqligi.',[('T1',58,'og‘zi')]),
 ('tog‘ → to:','So‘z oxiridagi g‘ tushishi; manba matnida latin transkripsiya buzilgan.',[('T1',58,'tog*')]),
 ('hunar → xunar','h/x mosligi, leksik misol bilan chegaralangan.',[('T1',58,'xunar')]),
 ('tuzni → tuzzi','Oldingi undosh n ni o‘ziga o‘xshatadi; grammatik tushum vazifasi qoladi.',[('T1',58,'туззъ')]),
 ('oshni → oshshi','sh+n ning shsh bo‘lib talaffuzi.',[('T1',58,'ошшъ')]),
 ('temirni → temirri','r+n ning rr bo‘lib talaffuzi.',[('T1',58,'temirri')]),
 ('tushda → chushta','t/ch mosligi va undoshlar birikmasi o‘zgarishi.',[('T1',58,'чуштэ')]),
 ('tushdi → chushti','Bir so‘zda ikki tovush hodisasi.',[('T1',58,'чуштъ')]),
 ('boryapman → borvomman','-vot+man birikmasida t/m assimilyatsiyasi; latin unli qiymati taxminiy.',[('T1',47,'борвоммэн')]),
 ('boryapsan → borvossan','-vot+san birikmasida t/s assimilyatsiyasi.',[('T1',47,'борвоссэн')]),
 ('boryapti → borvotti','-vot+ti birikmasidagi tt.',[('T1',47,'борвоттъ')]),
 ('boryapmiz → borvammiz(a)','Manbadagi birinchi shaxs ko‘plikning qaydi.',[('T1',47,'борвзммъз(э)')]),
 ('boryapsizlar → borvossila','Ikkinchi shaxs ko‘plik variantida assimilyatsiya va qisqarish.',[('T1',47,'борвоссълэ')]),
 ('foyda → payda','Toshkent/Farg‘ona guruhida f/p mosligi; hozirgi barcha so‘z va nutq qatlamiga umumlashtirilmaydi.',[('T3',39,'foyda>pəydə')]),
 ('hozir → xazir','T3 guruhga oid h/x misoli.',[('T3',39,'hozir>xəzir')]),
 ('toshbaqa → tashvaqa','T3 guruhga oid b/v misoli.',[('T3',39,'toshbaqa>təshvəqə')]),
 ('lab → lav','T3 guruhga oid b/v misoli.',[('T3',39,'ləb>ləv')]),
 ('buni → muni','Toshkent, Farg‘ona, Andijon uchun umumiy b/m qaydi.',[('T3',39,'bun’>mun’')]),
 ('burun → murun','Toshkent, Farg‘ona, Andijon uchun umumiy b/m qaydi.',[('T3',39,'burun>murun')]),
 ('bolalar → balala → balla','Toshkent misoli; -lar qisqarishi va so‘z ichidagi qisqarish.',[('T3',40,'bələlər>bələlə')]),
 ('bir bo‘g‘inli fe’lda l zaiflashishi','T3 el>o, bol>bo deb bosgan; el aslida ol ekanini bu tahlil taxmin qilib tuzatmaydi.',[('T3',40,'el>o')]),
 ('birga → billa','Toshkent va Farg‘ona uchun birgalikda qayd.',[('T4',137,'б ълл э')]),
 ('kitobni → kitappi','Toshkent va Farg‘ona uchun birgalikda qayd; bn/pp mosligi.',[('T4',137,'к ъ т э п п ъ')]),
 ('hech nima → hishtima / heshtma','Jizzax va Toshkentga birgalikda nisbat berilgan; OCR va mahalliy talaffuz tekshiriladi.',[('T4',138,'х ъ ш тъмэ')]),
 ('Unli uyg‘unligi va unlilar soni','Shahar tipida uyg‘unlik kuchsiz; T1 shimoliy qarluq shevalarini istisno qiladi. Oddiy imlo bilan to‘liq fonetik tizim tuzilmaydi.',[('T1',57,'shimoliy o‘zbek shevalarigina'),('T2',80,'oltita')]),
 ('choch / chəch','T2 va T3 yozuvlarini bitta qat’iy zamonaviy norma qilib birlashtirishga dalil yetmaydi.',[('T2',68,'choch'),('T3',41,'chəch')]),
 ('quduq → qudu; o‘rdak → o‘rday','Leksik misollar k va q bir xil tovush emasligini ko‘rsatadi.',[('T3',41,'qudu'),('T3',41,'o’rdəy')])]:
    add('FONETIKA',label,explanation,refs,area='Toshkent yoki manbada ko‘rsatilgan umumiy guruh',notes='So‘z/kontekst bo‘yicha qayd; avtomatik harf almashtirish uchun universal qoida emas.')

for label, explanation, refs, area in [
 ('-vot/-vat hozirgi davom','Toshkent shahar uchun kevotti va borvot- qatori qayd etilgan; zamon va shaxs alohida saqlanadi.',[('T1',58,'кевотть'),('T1',47,'борвоттъ')],'Toshkent shahar'),
 ('Hozirgi davomning shaxs qatori','borvomman / borvossan / borvotti / borvammiz(a) / borvossila / borishvotti. T1 jadvali; uchinchi ko‘plik -ish ishtirokida.',[('T1',47,'barisvattL')],'Toshkent shahar'),
 ('-ot davom shakli','T1 borotti, T4 borottim/kelottim qayd qiladi; shahar profiliga avtomatik ko‘chirilmaydi.',[('T1',58,'боротть'),('T4',208,'Паркеит, Нискент')],'Parkent, Piskent; Yangiyo‘lning manbadagi qishloq shevalari'),
 ('Parkentda -vat ham bor','T4 Parkent yor-yorida opkevottim shakli orqali ko‘rsatadi. Bitta namuna -ot ni inkor etmaydi.',[('T4',208,'Паркент'),('T4',208,'э п к е в э т т ъ м')],'Parkent; folklor'),
 ('Qaratqich va tushum -ni','Bir affiks ikkala vazifada keladi; sintaktik egalik/obyekt munosabatlari yo‘qolmaydi.',[('T1',58,'qaratqich, ham tushum')],'Toshkent guruhi'),
 ('suvvi teyi','Suvning tegi: genitiv munosabat; vv assimilyatsiyasi.',[('T1',58,'суввъ тэйъ')],'Toshkent guruhi'),
 ('atti min','Otni min: tushumdagi obyekt; tt assimilyatsiyasi.',[('T1',58,'atti min')],'Toshkent guruhi'),
 ('-la ko‘plik','T1 uylar/gullar, T4 bula deb beradi; oddiy ko‘plik vazifasi.',[('T1',31,'gullar'),('T4',166,'б у л э')],'Toshkent shahar va boshqa qayd etilgan shevalar'),
 ('-la hurmat birlik','ekamla, dadamla bitta insonni ham hurmat bilan bildiradi; sonni kontekstdan aniqlash kerak.',[('T4',167,'э кэмлэ'),('T4',167,'д э д э м л э')],'Toshkent shahar'),
 ('Egalikdan oldin r saqlanishi','T4 ularnı paxtaları misolida -lar qayta tiklanishini izohlaydi; tarixiy kuzatuv, zamonaviy mutlaq shart emas.',[('T4',167,'п э х т э л э р ъ')],'Toshkent va manbadagi qiyosiy guruh'),
 ('-gi jamlik: adamgila','Adasi va u bilan birga boshqalar. Faqat ko‘p ota degani emas.',[('T1',59,'adamgila')],'Toshkent'),
 ('-gi jamlik: oyimgila','Oyisi va u bilan birga boshqalar. Murojaat va referentni farqlash kerak.',[('T1',31,'эйъмгълэ')],'Toshkent dialekti'),
 ('-lig/-lug jamlik','T1 oylug‘i/ishlig‘i kabi birliklarda jamlikni qayd etadi; barcha otlarga unumli yasash uchun dalil yetarli emas.',[('T1',58,'-лъг/луг')],'Toshkent guruhi'),
 ('I ko‘plik: -vuz/-vuza','baravuz/baravuza; bu shakllar barcha fe’l zamoniga o‘zgarishsiz qo‘shilmaydi.',[('T1',59,'baravuz')],'Toshkent'),
 ('I ko‘plik o‘tgan: barduv','Bordik ma’nosidagi shakl, T1 va T4 qaydi.',[('T1',59,'barduv'),('T4',224,'бэр дув')],'Toshkent'),
 ('I ko‘plik o‘tgan: barduz','T1 borduz/kelduz; T4 barduz. Unli yozuv farqlari saqlanadi.',[('T1',40,'келдуз'),('T4',224,'б э р д у з')],'Toshkent'),
 ('I ko‘plik: oldimiz / aytsamiz','T1 oldimiz, aytsamiz misollarini alohida qayd etadi; adabiy -miz ni barcha shaklda majburlash emas.',[('T1',38,'олдъмъз'),('T1',38,'эйтсэмъз')],'Toshkent'),
 ('Shart I ko‘plik: borsovuz(a)','Shart mazmuni; -sa tarkibida ham unli o‘zgarishi qayd etilgan.',[('T1',40,'борсовуз(э)')],'Toshkent'),
 ('I ko‘plik: urdi:y','Toshkent/Qarshi uchun birgalikda qayd etilgan boshqa variant.',[('T1',40,'урди:й')],'Toshkent va Qarshi'),
 ('II ko‘plik egalik: kitopi:z','Kitobingiz ma’nosi. Shaxs-son va hurmat vazifasi grammatik kontekstdan aniqlanadi.',[('T1',33,'кьтопъ:з')],'Toshkent'),
 ('II ko‘plik fe’l: borvossiz','T1 -siz shaklini ham beradi; foydalanuvchini sheva bahonasida senlash kerak emas.',[('T1',39,'борвоссъз')],'Toshkent'),
 ('II ko‘plik: -s/-sila','Ishlaysiz/kelasila; boshqa shevalarga ham xos variant.',[('T1',39,'келэсълэ')],'Toshkent va Qarshi'),
 ('II o‘tgan: -yiz/-yla','Bajardiyiz, oldiyla, ishladiyla. Manbadagi konkret fe’l shakllari.',[('T1',41,'бэджэрдъйъз'),('T1',41,'олдъйлэ')],'Toshkent va Qarshi'),
 ('Buyruq/hurmat: keliyla','Kelinglar/olib boringlar uchun keliyla/oboriyla qaydi; adresat soni vaziyatga bog‘liq.',[('T1',42,'келъйлэ'),('T1',42,'оборъйлэ')],'Toshkent va Qarshi'),
 ('Istak I ko‘plik: -iylu','T1 ali ylu yozuvi matn qatlamida buzilgan; tasvir tekshiruvisiz tayyor fe’l tuzilmaydi.',[('T1',42,'(Toshkent)')],'Toshkent'),
 ('biza / bizla','Biz ma’nosidagi so‘zlashuv variantlari; yolg‘iz kishining kamtarlik/mag‘rurlik nutqi alohida kontekst.',[('T4',174,'б ъ з э'),('T4',174,'камтаринлик')],'Toshkent va bir necha shahar shevalari'),
 ('ula','Ular; -r qisqarishi. Katta guruhga umumiy belgi.',[('T4',173,'у л э')],'Toshkent, Samarqand, Qarshi, Jizzax va boshqa qaydlar'),
 ('senla / senlar','T4 oddiylik yoki nazar-pisand qilmaslikni ham qayd etadi. Botning standart adresati uchun hurmatli shakl saqlansin.',[('T4',174,'се н лэ')],'Toshkent, Turkiston, Chimkent'),
 ('hovliya / bedanaya / dalaya','T4 Toshkentda -ya jo‘nalish variantini qayd etadi; qo‘shimcha hududi har misolda alohida.',[('T4',152,'Тошкент')],'Toshkent'),
 ('Qurama jo‘nalish olmoshlari','magan/sagan/o‘g‘an turidagi qipchoq qaydlari; matn qatlamidagi g‘/g/r buzilishi sababli asl tasvir tekshiruvi kerak.',[('T4',153,'Курама')],'Qurama va boshqa nomlangan qipchoq shevalari'),
 ('-yotir adabiy ta’sirda','T4 Toshkentda odatiy shakl emasligini, lekin adabiy til/media ta’sirida uchrashini yozadi. 2026 nutqiga taqiq sifatida olinmaydi.',[('T4',206,'Ленин алабий тил')],'Toshkent va Farg‘ona; tarixiy kuzatuv'),
 ('Hamma inkor hozirgi davom emas','T4 bermavotti bilan birga aytmayman/yozmayman beradi. Fe’l zamoni va inkor alohida tahlil qilinadi.',[('T4',208,'б е р м э в э т т ъ'),('T4',208,'й э з м а й м а н')],'Qarluq-chigil-uyg‘ur guruhidagi misollar'),
 ('adasi kevottila','Toshkentka nisbat berilgan oilaviy evfemistik murojaat va hurmat shakli. Begonaga erkin murojaat emas.',[('T4',287,'э д э с ъ кевзттила')],'Toshkent; oilaviy kontekst')]:
    add('GRAMMATIKA',label,explanation,refs,area=area,
        status='tekshirish_kerak' if label in ['Istak I ko‘plik: -iylu','Qurama jo‘nalish olmoshlari'] else 'manbada_qayd_etilgan')

# Korpus ko‘chirmasi va analitik o‘qish ikki alohida maydon.
for n, needle, latin, meaning, purpose in [
 (89,'Йэрмъ тэк','Yarmi tok','Tomorqaning bir qismi tok ekilgani haqida.','mavzuni tanishtirish'),
 (89,'олмэ-полмэ, нэк-пэк','olma-polma, nok-pok','Meva turlarini umumlashtiradigan juftlash.','so‘zlashuvdagi umumlashtirish'),
 (89,'Бэллэ ДЭЛЭДЭ ЪШЛЭШЭДЪ','Balla dalada ishlashadi','Bolalarning dalada ishlashi.','qisqarish va III ko‘plik'),
 (89,'Кэръп кзлдъм','Qarib qoldim','So‘zlovchi o‘zining yoshini izohlaydi.','katta yoshdagi informant konteksti'),
 (89,'Кельн, съзгэ','Kelin, sizga…','Bog‘dorchilik mavzusiga suhbatdoshni jalb qilish.','sizlab gapirish'),
 (90,'бэйлъйвуз','bog‘layvuz','Ishkom qismlarini bog‘laymiz.','I ko‘plik'),
 (90,'ъстэй дъйвуз','istay diyvuz','Ingichka tol novdasini istay deymiz.','kasbiy so‘zni izohlash'),
 (90,'хэмтэв дъйвуз','xomtav diyvuz','Barglarni yulish amalining nomi.','so‘zning ma’nosini gap ichida ochish'),
 (90,'Тэртэрэй чэлсэц','Tartaray chalsang','Tartaray chalsang, qush qochadi.','shart va natija; faqat qush konteksti'),
 (90,'Кечэсъйэм хэвэзэдэ йэтэмэн','Kechasiyam havazada yotaman','Havazada tunash haqida.','-yam yuklama qisqarishi'),
 (90,'Бу йъл йэздэ бър келъйлэ','Bu yil yozda bir keliyla','Yozda kelishga taklif.','hurmatli taklif'),
 (90,'Хэвэзэгэ джэй къ-бърэмэн','Havazaga joy qi-beraman','Havazada joy tayyorlab berish.','yordam fe’li va suhbat taklifi'),
 (90,'ошэндэ бълэсъс','O‘shanda bilasis','Bog‘ va uzumning mazasini ko‘rgandan so‘ng bilasiz.','II shaxs hurmat'),
 (90,'бэ:дэрчълъйгэ кесэв','Bog‘dorchilikka kesav','Asosiy mavzuga qaytish; manba kel­sak deb izohlaydi.','mavzuni qayta davom ettirish'),
 (90,'кондэ: дъйвуз','Konda: diyvuz','Novdalarni yig‘ib bog‘lash amalini atash.','ta’rif berish'),
 (91,'съзгэйэм бъттэ екъп','Sizgayam bitta ekib…','Suhbatdoshga qalamchadan ekib berishni taklif qiladi.','sizlash; amaliy yordam'),
 (91,'узъмлъй ойгэ нъмэ йессън','Uzumli uyga nima yetsin','Uzumli hovlining yaxshi ekanini ifodalaydi.','baholovchi ibora; savolga literal javob emas')]:
    add('NUTQ_NAMUNALARI',needle,meaning,[('T1',n,needle)],area='Toshkent; bog‘dorchilik monologi',
        latin=latin,notes='Lotincha o‘qish taxminiy. Yozib olingan matndan parcha; tahlilchi yangi dialog tuzmagan.',
        genre='kasbiy monolog',interaction_function=purpose)
add('NUTQ_NAMUNALARI','qayga keyvossan?','Qayerga kelyapsan? Mazmuni kel- fe’li bilan; ket- fe’liga almashtirilmaydi.',
    [('T4',208,'ке йв ос с ан')],latin='qayga keyvossan?',notes='Tasvirda qayga; PDF matn qatlamida ka?$ buzilishi bor.',genre='qisqa manba misoli')
add('NUTQ_NAMUNALARI','adasi kevottila','Oilaviy evfemistik murojaat; hurmatli kelish holati.',
    [('T4',287,'э д э с ъ кевзттила')],latin='adasi kevottila',notes='Oilaviy munosabatni bilmasdan begona adresatga ishlatilmaydi.',genre='qisqa manba misoli')
add('NUTQ_NAMUNALARI','Parkent yor-yori','T4 opkevottim shaklini Parkent folkloridan keltiradi.',
    [('T4',208,'йэр-йэр')],area='Parkent',notes='Folklor namunasi kundalik zamonaviy suhbat chastotasining dalili emas.',genre='yor-yor')

for title, analysis, refs in [
 ('T2 unli ro‘yxati buzilgan','Oltita deb i ikki marta, sakkizta deb oltita belgi keltiriladi. Tovushlar jadvali shu ro‘yxatdan qurilmaydi.',[('T2',80,'oltita'),('T2',81,'sakkizta')]),
 ('T2 q keladi degan jumla misolga zid','Issiq→issi, tirnoq→tirno, sandiq→sandi misollari tushishni ko‘rsatadi. Da’vo va misol ajratiladi.',[('T2',81,'ushbu lahjada ham keladi')]),
 ('T2 qilutti shaxs glossi','Qilutti qilyapman deb berilgan; III shaxs bilan I shaxs bir xil emas. Bu tenglik o‘qitish jufti sifatida olinmaydi.',[('T2',81,'qilutti (qilyapman)')]),
 ('T2 zavutta ishlatadi / ishlaydi','Ishlatadi va ishlaydi harakat vazifasi bilan farq qiladi; sof talaffuz almashtirish jufti emas.',[('T2',81,'zavutta ishlatadi')]),
 ('T2 lahjada singarmonizm yo‘q','Butun lahjaga umumlashtirish T1 shimoliy singarmonizmli qarluq shevalari istisnosiga zid.',[('T2',80,'uchramaydi'),('T1',57,'shimoliy o‘zbek shevalarigina')]),
 ('T3 adabiy tilda 9 unli','Fonema/allofon/transkripsiya mezoni ochiq emas; zamonaviy adabiy tilga tayyor fonemik xulosa emas.',[('T3',39,'9 unli')]),
 ('T3 v yo‘q talqini','39-bet lab-tish v haqida; 40-bet lab-lab v ni qayd qiladi. Lotin v harfini butunlay taqiqlash noto‘g‘ri.',[('T3',39,'lab-tish'),('T3',40,'lab-lab, sirg’aluvchi')]),
 ('T3 ovoz/orzu arabcha degan umumlashtirish','Shakllar saqlanadi; etimologik belgi shu paragraflardan avtomatik meros olinmaydi.',[('T3',42,'arabcha so’zlar')]),
 ('T1 harakat nomi qatori','-ish harakat nomi deya yetishdi/qurishdi misoli berilgan; -ish va -di vazifalari alohida tahlil talab qiladi.',[('T1',58,'harakat nomining')]),
 ('Parkentda faqat -ot','T1 -ot ni qayd etgan, T4 -vat ham mavjudligini aytadi. Bir-birini inkor qiluvchi profil tuzilmaydi.',[('T1',58,'Parkentda'),('T4',208,'Паркент')]),
 ('T4 -na davomiy o‘tgan','Ta’rif bor, lekin shu paragrafda misol yetishmaydi; bot uchun yangi paradigma yasalmaydi.',[('T4',224,'-н э')]),
 ('O‘g‘ir / keli ma’nosi','T3 jadvalida o‘g‘ir, T3 p56 uy buyumlari qatori bor; aniq adabiy ma’noni mustaqil lug‘at bilan tasdiqlash kerak.',[('T3',42,'o’gъr'),('T3',56,'og’r- keli')]),
 ('Eski bog‘bon matni va yoshlar nutqi','T1 matnida so‘zlovchi qariganini aytadi; texnologiya/yoshlar slengi haqida bevosita dalil bermaydi.',[('T1',89,'Кэръп кзлдъм')]),
 ('Xalqona davo haqidagi gap','Uzum ming bir dardga davo degan ibora monologning baholovchi xalqona fikri; tibbiy bilim sifatida kiritilmaydi.',[('T1',90,'мън бър дэрткэ дэвэ')]),
 ('Adabiy til = aynan Toshkent emas','T1 shartli tayanch deb beradi va bir-ikki sheva bilan bog‘lash to‘g‘ri emasligini qo‘shadi.',[('T1',76,'shartli ravishda'),('T1',76,'juda ham to‘g‘ri emas')]),
 ('T2 katalog 74, PDF 96','Nashr metama’lumoti 74 bet deydi; yuborilgan PDF 96 sahifa. Havolalar PDF tartib raqamiga bog‘lanadi.',[('T2',2,'74 b.')])]:
    add('TEKSHIRILADIGAN_DAVOLAR',title,analysis,refs,area='Manba sifati va talqin',status='tayyor_qoida_emas')

for title, analysis, refs in [
 ('Toshkent shahar','-vot/-vat davom; assimilyatsiyali shaxs variantlari; -la ko‘plik/hurmat; -gi jamlik. Yil/yosh/kasb farqi saqlanadi.',[('T1',58,'Toshkentda'),('T1',59,'adamgila')]),
 ('Parkent','T1 -ot, T4 -vat ham qayd etadi. Folklor bilan kundalik misollar ajratiladi.',[('T1',58,'Parkentda'),('T4',208,'Паркент')]),
 ('Piskent / Yangiyo‘lning ayrim shevalari','T1 guruhga qo‘shgan; T4 -ot misolini Niyozboshi va boshqa nomlangan joylarga bog‘laydi. Butun tuman uchun yakdil profil emas.',[('T1',57,'Piskent'),('T4',208,'Янгий^л')]),
 ('Ohangaron / Qurama qipchoq muhiti','Shahar qarluq profili bilan birlashtirilmaydi; T1 Ohangaron vodiysida qipchoq vakillarini, T4 Quramada jo‘nalish olmoshlari farqini qayd etadi. Butun vodiy bir xil degan xulosa emas.',[('T1',84,'Ohangaron'),('T4',153,'Курама'),('T4',177,'курама'),('T2',80,'qipchoq shevalaridan boshqa')]),
 ('Toshkent bog‘dorchilik monologi','Manba Toshkent deb sarlavhalagan, mahalla/yozuv sanasi yo‘q. Katta yosh, tomorqa va tokchilik konteksti bor; bugungi barcha Toshkent vakili modeli emas.',[('T1',89,'Toshkent shevasi'),('T1',89,'Кэръп кзлдъм')])]:
    add('HUDUDIY_PROFILLAR',title,analysis,refs,area=title)

for label, analysis, refs in [
 ('Toshkent—Farg‘ona davom zamoni','T1 Toshkent -vot, T2 Andijon/Marg‘ilon/Qo‘qon -yap; Namangan alohida. Farg‘onaning barcha shevalari bir xil emas.',[('T1',58,'-вот'),('T2',81,'Andijon')]),
 ('Toshkent—Namangan -ut','T2 -ut variantini Namanganga bog‘laydi. T4 Uychi -vat/-ot misolini ham qayd etadi; viloyatlar o‘rtasida belgilar ustma-ust kelishi mumkin.',[('T2',81,'Namangan'),('T4',208,'Уйчи')]),
 ('Toshkent—Buxoro/Samarqand -op','T1 Toshkent borvotti, Buxoro boropti qatorlarini yonma-yon beradi.',[('T1',47,'борвоттъ'),('T1',47,'бороптъ')]),
 ('Ona nomlari','Toshkent oyi; T4 Farg‘ona aya/buvi, T2 Buxoro qalampur bilan qiyoslash ham bor. Bu so‘zlar faqat shu hududlarda bo‘ladi degani emas.',[('T4',269,'ой и'),('T2',82,'ayya, buvi')]),
 ('Chumoli—mo‘rcha—chumalik','T2 Toshkent, Samarqand/Buxoro, Farg‘ona ustunlari. Fonetik va leksik farq birga.',[('T2',68,'chumoli')]),
 ('Shoti ma’nosi','T4 Toshkent arava qismi; Farg‘ona narvon. T3 Farg‘onada arava qismi ma’nosi ham bor deydi.',[('T4',276,'Ш э т ъ'),('T3',57,'arava qismi')]),
 ('Toshkent—Jizzax umumiy belgilar','T4 -la/ula va hech nima qisqarishini ikkala hududda qayd etadi. Bular hududni yolg‘iz o‘zi aniqlamaydi.',[('T4',166,'Жиз'),('T4',138,'х ъ ш тъмэ')]),
 ('Toshkent—Qarshi umumiy shaxs affikslari','T1 -vuz, -sila, -yla bir necha hududda qayd etilgan. Qashqadaryo ham yaxlit bitta profil emas.',[('T1',38,'Qarshi'),('T1',42,'Qarshi')]),
 ('Surxondaryo bilan cheklangan qiyos','T1 Surxondaryo y-lovchi shevalarida jo‘nalish/o‘rin-payt bitta ko‘rsatkich bo‘lishini aytadi. Buni Toshkent shahar qoidasiga ko‘chirishga asos yo‘q.',[('T1',33,'Surxondaryoning')])]:
    add('HUDUDLAR_QIYOSI',label,analysis,refs,area='Manbalarda nomlangan hududlar qiyosi')

metadata={
 'T1':{'author':'Samixon Ashirboyev','title':'O‘zbek dialektologiyasi','year':2016,'publisher':'Navro‘z, Toshkent'},
 'T2':{'author':'Yoqub Saidov','title':'O‘zbek dialektologiyasi (to‘ldirilgan va qayta nashri)','year':2021,'publisher':'Durdona, Buxoro'},
 'T3':{'author':'Sh. Xudoyqulova','title':'O‘zbek dialektologiyasi, o‘quv-uslubiy majmua','year':2008,'publisher':'Guliston'},
 'T4':{'author':'Nazar Rajabov','title':'O‘zbek shevashunosligi','year':1996,'publisher':'O‘qituvchi, Toshkent'}}

def recursive_dicts(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from recursive_dicts(v)
    elif isinstance(x,list):
        for v in x:yield from recursive_dicts(v)

for s in manifest:
    s.update(metadata[s['id']])
    s['pdf_path']=s['path']
    s['text_extraction']='PDF matn qatlami; fonetik shrift/OCR buzilishlari bo‘lishi mumkin'
    s['exact_duplicates_in_previous_regions']=[]
    for f in ROOT.parent.glob('*/MANBALAR.json'):
        if f.parent==ROOT:continue
        for old in recursive_dicts(json.loads(f.read_text())):
            if old.get('sha256')==s['sha256']:
                s['exact_duplicates_in_previous_regions'].append({'region':f.parent.name,'source_id':old.get('id',old.get('source_id'))})
    s['independent_field_observation_proven']=False
    assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
save('MANBALAR.json',{'uploaded_sources':manifest,'source_reuse_note':'Bir xil SHA yangi mustaqil dalil hisoblanmaydi. Turli darsliklar bir tarixiy materialni takrorlagan bo‘lishi ham mumkin.'})

for cat, rows in collections.items():save(cat+'.json',rows)
raw=[]
for n in [89,90,91]:
    p=pages['T1'][n-1]
    if n==89:p=p[p.index('Мэн озъм'):]
    if n==91:p=p[:p.index('Farg‘ona shevasi')]
    raw.append({'source_id':'T1','pdf_page':n,'printed_page':n-1,'raw_pdf_text':p,'image_path':str(ROOT/'tekshiruv'/f'T1_{n:03d}.png')})
save('TOSHKENT_MONOLOG_ASL.json',{'description':'T1 Toshkent sarlavhasi ostidagi matn; Farg‘ona ertaklari chegarasida to‘xtatilgan. PDF matn qatlami buzilishlari saqlangan.','pages':raw})

coverage={
 'total_pdf_pages':sum(x['pages'] for x in manifest),
 'all_pages_text_extracted':True,
 'all_pages_deeply_read':False,
 'scope':'Toshkentka oid topilgan bo‘limlar, qiyosiy izohlar, asosiy nutq namunasi batafsil o‘qildi; butun 625 sahifalik kitoblar to‘liq o‘qilgan deb da’vo qilinmaydi.',
 'focused_reading_pages':{
 'T1':[31,32,33,34,36,38,39,40,41,42,46,47,57,58,59,76,83,84,89,90,91],
 'T2':[1,2,68,80,81,82],
 'T3':list(range(38,45))+list(range(53,58)),
 'T4':[56,88,128,134,135,137,138,149,150,151,152,153,154,156,166,167,170,172,173,174,177,206,207,208,209,211,224]+list(range(269,277))+[287,300,301]},
 'focused_does_not_mean_every_line_on_page_read':True,
 'page_images_inspected':[{'source_id':s,'pdf_page':n} for s,n in sorted(visual)],
 'printed_pagination':'T1 tasdiqlangan tana sahifalarida PDF−1; T3 tana sahifalarida PDF tartibi bilan mos. T2 noma’lum. T4 faqat aniq ko‘rilgan sahifa raqamlari qo‘yildi; qolganlari null.',
 'audio_or_native_speaker_validation':False,
 'model_weights_trained':False,
 'bot_code_implemented':False}
save('OQISH_QAMROVI.json',coverage)

anchor_count=0
for rows in collections.values():
    for row in rows:
        for r in row['refs']:
            assert r['anchor_normalized_whitespace'] in norm(pages[r['source_id']][r['pdf_page']-1])
            anchor_count+=1
stats={'counts':{k:len(v) for k,v in collections.items()},'pdf_pages':coverage['total_pdf_pages'],
       'anchor_count':anchor_count,'sources':len(manifest),'page_images_inspected':len(visual),
       'lexicon_status_counts':{s:sum(x['evidence_status']==s for x in collections['LUGAT']) for s in ['manbada_qayd_etilgan','tekshirish_kerak']}}
save('HISOBOT_STATISTIKASI.json',stats)
validation={'source_sha256_checks_passed':4,'page_anchors_checked':anchor_count,'all_anchors_found':True,'scope_and_uncertainty_recorded':True}
page_records=(ROOT/'SAHIFALAR.jsonl').read_text().splitlines()
assert len(page_records)==coverage['total_pdf_pages']
validation['extracted_page_records_checked']=len(page_records)
report=ROOT/'OQISH_XULOSALARI.md'
if report.exists():
    links=re.findall(r'\]\((/[^)]+)\)',report.read_text())
    assert all(Path(x).exists() for x in links)
    validation.update({'report_links_checked':len(links),'all_report_links_exist':True})
save('TEKSHIRUV_NATIJASI.json',validation)
print(json.dumps(stats,ensure_ascii=False,indent=2))
