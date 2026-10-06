import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/research/buxoro')

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

sources = json.loads((ROOT / 'download_manifest.json').read_text())
updates = {
    'B1': dict(title='O‘zbek dialektologiyasi', author='Ashirboev Samixon', year=2011,
               institution='Nizomiy nomidagi Toshkent davlat pedagogika universiteti',
               read_pages=[1,2,19,20,21,22,35,36],
               context_reviewed_pages=[6,9,10,30,31,32,76], visual_pages=[19,20,22],
               scope='Metodik qo‘llanma; hududiy tasnif va tegishli morfologiya o‘qildi. Avvalgi 2016-yilgi darslikning aynan bir fayli emas; bir muallifning qayta ishlangan umumiy bayonlari mustaqil dala kuzatuvi deb hisoblanmaydi.'),
    'B2': dict(title='O‘zbek shevashunosligi', year=2012,
               authors=['T. J. Enazarov','V. A. Karimjonova','M. S. Enazarova','Sh. S. Mahmadiyev','K. G‘. Rixsiyeva'],
               publisher='Universitet, Toshkent', same_as_samarqand_source='M5',
               read_pages=[11,20,29,39,40,75,82], visual_pages=[11,20,29,39,75,82],
               context_reviewed_pages=[13,14,15,16,18],
               ocr_text_path=str(ROOT/'B2_ocr.txt'),
               scope='Samarqand M5 bilan SHA-256 aynan teng; oldingi OCR qayta ishlatildi. Ko‘p PDF sahifalarida ikkita bosma sahifa bor. Kitob to‘liq o‘qilgan yoki OCR to‘liq qo‘lda tuzatilgan emas.'),
    'B3': dict(title='Buxoro shevalarida morfonologik o‘zgarishlar',
               author='Asatullayeva Dilnavoz Jondullayevna', doi='10.5281/zenodo.15243844',
               year=None, year_note='Yuborilgan to‘rt sahifada nashr sanasi aniq ko‘rsatilmagan.',
               venue='O‘zbek filologiyasi: muammo va yechimlar respublika ilmiy-amaliy anjumani',
               read_pages=[1,2,3,4], visual_pages=[2,3], printed_pages=[118,119,120,121],
               scope='Maqola to‘liq o‘qildi. Sarlavha/annotatsiya qarluqni ko‘rsatadi, asosiy matn o‘g‘uz misollariga ham o‘tadi; ikki qatlam ajratildi.'),
    'B4': dict(title='Buxoro o‘g‘uz shevalarining til xususiyatlari',
               author='Allaberdiyev Alijon Avezberdiyevich', year=2025, city='Qarshi',
               document_type='Filologiya fanlari doktori (DSc) dissertatsiyasi avtoreferati',
               research_institution='Navoiy davlat universiteti',
               read_pages=list(range(5,31)), context_reviewed_pages=[1,2,3,4],
               visual_pages=[20,25,29],
               fieldwork_years=[2005,2023],
               fieldwork_districts=['Qorako‘l','Olot','Jondor','Romitan','Peshku','Shofirkon','Kogon','Buxoro'],
               scope='O‘zbekcha kirish, asosiy mazmun va xulosalar 5–30 to‘liq o‘qildi; ruscha 31–60 va inglizcha qismlar to‘liq qayta o‘qilmadi. Yuborilgan 69 sahifali avtoreferat 269 sahifali dissertatsiyaning o‘zi emas; unda aytilgan 1500 ga yaqin so‘zli lug‘at to‘liq ilova sifatida mavjud emas.'),
    'B5': dict(title='Buxoro shevasiga oid dialektizmlar tahlili', year=2023,
               authors=['Xudoyberdiyeva Gulmira Allaberdi qizi','Abdurahmonova Gulorom Iskandar qizi'],
               venue='Modern Science and Research, 2-jild, 4-son', doi='10.5281/zenodo.7878010',
               read_pages=[1,2], visual_pages=[2], printed_pages=[677,678],
               scope='Maqola to‘liq o‘qildi; tanlangan birliklari avval yuborilgan 1971-yilgi lug‘at bilan qiyoslandi. Matndagi muallif telefon raqamlari bilim bazasiga kiritilmadi.'),
}
for source in sources:
    source.update(updates[source['id']])
    source['text_path'] = str(ROOT/(source['id']+'.txt'))

old = json.loads(Path('/workspace/research/qashqadaryo/MANBALAR.json').read_text())[-1]
supplement = dict(id='E1', title=old['title'], editor=old['editor'], year=old['year'],
                  publisher=old['publisher'], pdf_path=old['pdf_path'], text_path=old['text_path'],
                  pages=old['pages'], sha256=hashlib.sha256(Path(old['pdf_path']).read_bytes()).hexdigest(),
                  role='Avval yuborilgan Qashqadaryo Q4; B5 ning lug‘aviy da’volarini tekshirish uchun qo‘shimcha manba.',
                  entries_reviewed_on_pages=[17,29,35,41,43,62,75,78,109,137,166,175,207,224,229,246,269,271,272,275,281],
                  visual_pages=[41,62,75,78,109,137,229,271,281],
                  scope='Tanlangan lug‘aviy maqolalar o‘qildi; ro‘yxatdagi har bir sahifaning barcha maqolalari to‘liq o‘qilgan emas.')
write('MANBALAR.json', {'uploaded_sources':sources,'supplementary_sources':[supplement]})
byid = {s['id']:s for s in sources+[supplement]}
texts = {s['id']: Path(s.get('ocr_text_path',s['text_path'])).read_text().split('\f') for s in sources+[supplement]}

def printed(sid, n):
    if sid=='B2' and 3<=n<=95: return [2*n-4, 2*n-3]
    if sid=='B3': return [n+117]
    if sid=='B5': return [n+676]
    if sid in ['B1','B4','E1']: return [n]
    return []

with (ROOT/'SAHIFALAR.jsonl').open('w') as f:
    for s in sources:
        for n in range(1,s['pages']+1):
            f.write(json.dumps(dict(source_id=s['id'],pdf_page=n,printed_pages=printed(s['id'],n),
                                    text=texts[s['id']][n-1], extraction='OCR; qidiruv uchun, to‘liq tekshirilmagan' if s['id']=='B2' else 'PDF matn qatlami'),ensure_ascii=False)+'\n')

lex=[]
def add(form, meaning, sid, page, region, branch, anchor, variants=None, note='', corroboration=None):
    t=texts[sid][page-1]
    pos=t.find(anchor)
    assert pos>=0,(form,sid,page,anchor)
    lex.append(dict(id=f'BL{len(lex)+1:03}',form=form,variants=variants or [],meaning_uz=meaning,
                    region=region,dialect_branch=branch,source_id=sid,pdf_page=page,printed_pages=printed(sid,page),
                    evidence_excerpt=t[max(0,pos-130):pos+220].replace('\n',' '),
                    note=note,comparative_mentions=corroboration or [],exclusive_to_region=False,
                    evidence_status='Manbada qayd etilgan; bugungi tabiiy ishlatilishi alohida tasdiqlanmagan.',
                    writing_status='Tahririy sodda o‘qilish; manbaning barcha fonetik diakritikalari va cho‘ziqliklari saqlanmagan.'))

oguz='Buxoro o‘g‘uz shevalari; aniq misolning qishlog‘i avtoreferatda ko‘rsatilmagan'
oguz_rows=[
 ('susaq','cho‘mich',13,'cho‘mich'),
 ('uxu','uyqu',13,'uyqu'),
 ('o‘g‘rincha','yashirincha',13,'yashirincha'),
 ('oyaq','uyg‘oq',13,'uyg‘oq'),
 ('tiramo','kuz',15,'kuz'),
 ('mushoyit','halaqit',15,'halaqit'),
 ('chakida','suzma',15,'suzma'),
 ('naymit','epchil',15,'epchil'),
 ('lekot','holsiz',16,'holsiz'),
 ('resh','jarohat',16,'jarohat'),
 ('resha','ildiz',16,'ildiz'),
 ('roda','ichak',16,'ichak'),
 ('nakora','qanday',16,'qanday'),
 ('hitlo','anavi',16,'anavi'),
 ('haz','huzur, halovat, maza, kayf',19,'huzur'),
 ('balli','nishon, belgi',19,'nishon'),
 ('balli-kulli','butunlay, batamom',19,'butunlay'),
 ('ravot','qishloq',19,'qishloq'),
 ('juba','bolalar kiyimi',19,'bolalar kiyimi'),
 ('dutkash','mo‘ri',19,'mo‘ri'),
 ('jorip','supurgi',19,'supurgi'),
 ('gulmix','temir qoziq',19,'temir qoziq'),
 ('ravoq','tokcha',20,'tоkҫа'),
 ('mo‘hra','sop, dasta',20,'sop, dasta'),
 ('toqurqo','devor tagidan yoki yo‘l ostidan qilingan suv yo‘li',20,'devor tagidan'),
 ('dorji','zich, tig‘iz; tiqilinch',20,'zich, tig‘iz'),
 ('tendor','sog‘lom, baquvvat; semiz, yetilgan',20,'sog‘lom, baquvvat'),
 ('begenmak','quvonmoq',22,'quvonmoq'),
 ('aqrava','sho‘r',23,'sho‘r'),
 ('mozziq','bemaza, ta’msiz',23,'bemaza'),
 ('ner','qayer',24,'qayer'),
 ('nehel','qanaqa',24,'qanaqa'),
 ('namechin','nima uchun',24,'nima uchun'),
 ('nichik','qanday',24,'qanday'),
 ('navox','qachon',24,'qachon'),
 ('iner / inek','sigir',23,'sigirlar'),
]
for form,meaning,page,anchor in oguz_rows:
    if form=='iner / inek': form='inek'
    notes={
        'jorip':'Avtoreferatdagi j belgisi boshqa manbaning fonetik j (= y) belgisi bilan avtomatik tenglashtirilmadi.',
        'ravoq':'Adabiy tildagi me’moriy ravoqning ta’rifi bilan tenglashtirilmasin.',
        'mo‘hra':'Asbobning sopi/dastasi ma’nosi; adabiy lug‘atdagi boshqa ta’rifdan farqlangan.',
        'begenmak':'Ushbu sahifada quvonmoq deb izohlangan; yoqtirmoq kabi qo‘shimcha ma’no o‘zimizdan kiritilmadi.',
        'inek':'Manbada ınеklеr — sigirlar shakli; bosh shakl inek tahririy ajratilgan.',
        'ner':'Manbadagi cho‘ziqlik sodda yozuvda aks etmagan.',
    }
    add(form,meaning,'B4',page,oguz,'o‘g‘uz',anchor,note=notes.get(form,''))

# E1 — birlamchi lug‘aviy qayd; B5 bu ma’lumotlarni qayta keltiradi.
oldrows=[
 ('badburut','katta, beo‘xshov mo‘ylovli kishi',41,'бадбурут',[],''),
 ('badgo‘y','tili zahar, achchiq gapiradigan',41,'бадгуй',[], 'Kishiga salbiy tavsif; neytral murojaat emas.'),
 ('badimol','serjahl',41,'бадъмол',[],''),
 ('bazarba','kuchli',41,'базарба',[],''),
 ('alvonj','belanchak',17,'алвонж',[], 'Qashqadaryoda alvonch varianti qayd etilgan.'),
 ('alis','g‘ilay',29,'элис//элус',['alus'], 'Buxoro va Qashqadaryo belgisi bor; keltirilgan gap Qashqadaryoga tegishli.'),
 ('obiro‘g‘on','palov uchun guruch solishdan oldin tayyorlanadigan zirvak',35,'збироран',[], 'B5 obirog‘on/obiro‘g‘on shakllarini beradi; lug‘atning fonetik yozuvi alohida saqlangan.'),
 ('bandak','to‘g‘nog‘ich',43,'бандак',[],''),
 ('gavdusha','sut uchun sopol idish, xurma',62,'гавдуша',[], 'E1 ruscha izoh: глиняный горшок для молока. B5 dagi gavdo‘sha — xurmo meva sifatida talqin qilinmasin; shakl ham qayta tekshiriladi.'),
 ('g‘ulva','sopol quvur',75,'рул б а',['g‘ulba'], 'Qashqadaryo g‘alva varianti bilan qiyos; material — keramika.'),
 ('dammakak','jim, tinch, jimgina',78,'«тихо»',[], 'Buxoro va Samarqand qaydi. B5 dagi dammamak shu shaklga tengligi mustaqil tekshiriladi.'),
 ('zardolu','o‘rik',109,'зардэлу',['zaldoru','zaldori'], 'B5 dagi zaldolu varianti bu sahifadagi zardolu bilan aynan bir yozuv emas.'),
 ('kallapush','do‘ppi',137,'кал(л)апуш',['kalapush'], 'B5 kal(l)po‘sh yozadi; birlamchi lug‘at kal(l)apush deb beradi.'),
 ('labdo‘l','labi qalin odam',166,'лабдул',[], 'Tashqi ko‘rinish tavsifi; suhbatdoshga o‘z-o‘zidan laqab qilib qo‘llanmaydi.'),
 ('mag‘al','shovqin',175,'марал I',[],''),
 ('palavkadu','oshqovoq',207,'палавкэди',[], 'Shimoliy Xorazmdagi palavkadi bilan qiyoslangan.'),
 ('rangdon','siyohdon',224,'рацдэн',[], 'Misol Romitonga tegishli.'),
 ('sannon','temirchining sandoni',229,'саннон',['saynon'], 'Sandal Xorazm varianti; Buxoro profiliga shu nom bilan qo‘shilmadi.'),
 ('taxtlash','yerni tekislash; tayyorlash',246,'гах(т)лаш',['taxlash'],''),
 ('ush','daraxt o‘zagi',269,'у ш I',[],''),
 ('o‘g‘loq','uloq, echki bolasi',271,'углэг',[], 'Sport musobaqasi ma’nosidagi uloq bilan aralashtirilmasin; fonetik sodda o‘qilish.'),
 ('falla','og‘iz suti',272,'фалла',[], 'Buxoro va Samarqand qaydi; B5 palla variantini ham beradi, lekin E1 shu joyda falla deb yozadi.'),
 ('xappak','qopqon',275,'хаппак',[], 'B4 PDF 16 da ham xappak — qopqon qaydi bor.'),
 ('xachcha','tirgovuch',281,'хачча хачча',[], 'B5 harra — tirgovuch deb yozadi; E1 da xachcha — tirgovuch, harra esa Bog‘otda arra ma’nosida.'),
]
for form,meaning,page,anchor,variants,note in oldrows:
    refs=[] if form=='xachcha' else [dict(source_id='B5',pdf_page=1 if form in ['badburut','badgo‘y'] else 2)]
    if form=='xappak':refs.append(dict(source_id='B4',pdf_page=16))
    region='Buxoro (1971-yilgi lug‘at belgisi; ichki lahja ko‘rsatilmagan)'
    if form in ['alis']: region+='; Qashqadaryoda ham'
    if form in ['dammakak','falla']:region+='; Samarqandda ham'
    add(form,meaning,'E1',page,region,'aniqlanmagan',anchor,variants,note,refs)

add('qalamfur','qalampir','B2',75,'Samarqand–Buxoro guruhi','guruh qiyosi','qalamfur',
    note='Bosma 146. Oldingi Xudoyqulova kitobidagi qalampur yozuvi bilan farq saqlandi.')
add('chovon','pashsha','B2',82,'Buxoro (qiyosiy lug‘at misoli)','aniqlanmagan','chovon',variants=['chopon'],
    note='Bosma 160. Shu qiyosdagi peshshe — chivin ma’nosi bilan adashtirilmasin. Bu Buxoro uchun qo‘shimcha ma’no qaydi, barcha chopon so‘zlarini almashtirish qoidasi emas.')
add('ko‘la','sho‘rdanak','B3',4,'Buxoro qarluq shevasi (maqola konteksti)','qarluq','sho‘rdanak',
    note='Manbadagi kölä-pölä takroriy birikmasidan bosh shakl tahririy ajratildi; kundalik aytilish audio bilan tekshirilmagan.')
write('LUGAT.json',dict(description='Manbasi va hududi ko‘rsatilgan ishchi lug‘at. Qayd etilganlik bugungi tabiiylik yoki boshqa hududda yo‘qlikni bildirmaydi.',entry_count=len(lex),entries=lex))

candidates=[
 dict(form='gavdo‘sha',meaning_as_claimed='xurmo',source_id='B5',pdf_page=2,reason='E1:62 gavdusha — sut uchun sopol idish, xurma deb beradi. Meva ma’nosi olinmadi; yozuv farqi ham tekshiriladi.'),
 dict(form='dammamak',meaning_as_claimed='jim, tinch, jimgina',source_id='B5',pdf_page=2,reason='E1:78 dammakak shakli. Variantmi yoki ko‘chirish xatosimi, noma’lum.'),
 dict(form='zaldolu',meaning_as_claimed='o‘rik',source_id='B5',pdf_page=2,reason='E1:109 zardolu/zaldoru/zaldori. Zaldolu alohida tasdiqlanmagan.'),
 dict(form='kal(l)po‘sh',meaning_as_claimed='do‘ppi',source_id='B5',pdf_page=2,reason='E1:137 kal(l)apush. Qisqarishning bugungi varianti bo‘lishi alohida tasdiqlanmagan.'),
 dict(form='palla',meaning_as_claimed='og‘iz suti',source_id='B5',pdf_page=2,reason='E1:272 falla qaydi bor, palla shu maqolada qo‘shimcha variant sifatida berilgan.'),
 dict(form='harra',meaning_as_claimed='tirgovuch',source_id='B5',pdf_page=2,reason='E1:281 xachcha — Buxoro tirgovuch; harra — Bog‘ot arra. Hudud va ma’no tenglashtirilishi asosiy lug‘atga olinmadi.'),
 dict(form='jölkirā',meaning_as_claimed=None,source_id='B3',pdf_page=2,region_as_claimed='G‘ijduvon, yoshi katta kishilar',reason='Ekspeditsiya qaydi bor, lekin maqola bu shaklning ma’nosi va adabiy muqobilini ochiq bermaydi. Yo‘lkira ma’nosi o‘zimizdan kiritilmadi.'),
 dict(form='Sixakti',meaning_as_claimed='qirg‘ichni',source_id='B3',pdf_page=3,region_as_claimed='Buxoro o‘g‘uz konteksti',reason='Sixakti opke jumlasi tarjimasi aniq, lekin asosni Sixak deb ajratish va -ti qo‘shimchasining tahlili yetarlicha asoslanmagan. Butun jumla saqlandi.'),
]
for i,e in enumerate(candidates,1):
    e.update(id=f'BC{i:03}',printed_pages=printed(e['source_id'],e['pdf_page']),status='Tekshirish kerak; bot uchun tayyor almashtirish emas.')
write('TEKSHIRILADIGAN_BIRLIKLAR.json',dict(entry_count=len(candidates),entries=candidates))

rules=[]
def rule(sid,page,standard,form,kind,scope,note=''):
    rules.append(dict(id=f'BG{len(rules)+1:03}',source_id=sid,pdf_page=page,printed_pages=printed(sid,page),
                      standard=standard,dialect_reading=form,kind=kind,scope=scope,note=note,
                      application='Misol doirasida; kontekstsiz umumiy matn almashtirish qoidasi emas.',
                      writing_status='Sodda o‘qilish; to‘liq fonetik transkripsiya alohida manba matnida.'))
q='B3 qarluq konteksti; aniq qishloq ko‘rsatilmagan'
o='B4 Buxoro o‘g‘uz materiali; ichki variant va adabiy til ta’siri hisobga olinadi'
rule('B3',2,'buzildi','buzilli','ld → ll assimilatsiyasi',q)
rule('B3',2,'buni','muni','olmosh asosi',q,'Gap misoli bor; G‘ijduvon yorlig‘i matnda aynan jölkirā kuzatuviga berilgan, barcha qo‘shni misollarga yoyilmadi.')
rule('B3',3,'ko‘rpachaga o‘tir','Körpäčäjä ötir','jo‘nalish -ga/-ya varianti','B3 o‘g‘uz konteksti','Manba j belgisi bu o‘rinda y o‘qiladi; yigit→jigit deb talqin qilinmaydi.')
rule('B3',3,'onamga oldim','Ānämä āldim','jo‘nalish -a varianti','B3 o‘g‘uz konteksti')
rule('B3',3,'opamning kitobi','Āpämiƞ kitāpi','qaratqich va egalik','B3 o‘g‘uz konteksti')
rule('B3',3,'butun, bus-butun','buppä-butun','kuchaytiruvchi takror',q)
rule('B3',3,'gap-so‘z, mish-mish','gäp-päp / gäp-säp','takror va pragmatik ma’no',q,'Noaniqlik, shubha yoki befarqlik kontekstlari; har bir gapda majburiy takror emas.')
rule('B3',4,'non, choy, sho‘rdanak kabi narsalar','nān-pān, čāj-pāj, kölä-pölä','takror bilan sanash',q,'Taklif jumlasidagi shakllar; pān/pāj/pölä alohida buyum nomi sifatida olinmadi.')
rule('B4',16,'aytdi','aytti','td → tt assimilatsiyasi',o)
rule('B4',16,'keldi','gelli','ld → ll va k/g farqi',o,'B4:20 da geldi varianti ham bor; ikki yozuv saqlandi, bittasi hamma joyga majburiy emas.')
rule('B4',16,'nondan','nonnan','nd → nn assimilatsiyasi',o)
rule('B4',16,'bizni / sizni','bizzi / sizzi','zn → zz assimilatsiyasi',o)
rule('B4',17,'yomg‘ir','yog‘mir','metateza',o)
rule('B4',20,'bilgan','bilen','-gan/-an sifatdosh varianti',o,'Manbaning yumshoq unlisi oddiy e bilan yaqinlashtirilgan; fonetik yozuv bılǝn.')
rule('B4',20,'boshlagan','boshlan','unli asosdan keyingi -n',o,'Boshlan- fe’l asosi va boshlagan ma’nosidagi sifatdosh kontekst bilan ajratiladi.')
rule('B4',21,'borgan emish','boranmish','emish qisqarishi',o,'Eshitilganlik ma’nosi saqlanadi; oddiy bordi bilan teng emas.')
rule('B4',21,'qolgan ekan','qolankan','ekan qisqarishi',o)
rule('B4',21,'ketgan edi','gidendi','edi qisqarishi',o,'Manbadagi gıdǝndı shaklining sodda o‘qilishi.')
rule('B4',23,'kiyimlar / sigirlar','giyimlar / inekler','ko‘plik va unli uyg‘unligi',o)
rule('B4',25,'yerni ag‘darmoq','yeri ag‘darish','tushum -i varianti',o,'Manba yеrı аğdаrïș; yordamchi harakat nomi ham misolda farqlanadi.')
rule('B4',25,'ko‘lga qaramoq','ko‘la qaramaq','jo‘nalish -a varianti',o)
rule('B4',25,'sovuqda qolmoq','sovuqda qalmaq','o‘rin-payt -da saqlanishi',o,'Butun Buxoroda -da ni yo‘qotish haqidagi avtomatik qoidaga asos yo‘q.')
rule('B4',26,'sen bilan qolmoq','sen vilan qalmaq','bilan/vilan varianti',o)
rule('B4',28,'deb aytdi','diyip aytti','ko‘chirma gapni bog‘lash',o)
rule('B2',11,'boradigan','boratugan','sifatdosh varianti','Samarqand–Buxoro guruhi, bosma 19','Manbaning maxsus unlilari oddiy yozuvda yaqinlashtirilgan; sahifa rasmi tekshirildi. Bu aniq audio transkripsiya emas.')
write('GRAMMATIKA.json',dict(rule_count=len(rules),rules=rules,
    observations=[
        dict(source_id='B1',pdf_pages=[19,20],scope='Darslikning tarixiy guruh bayoni',observation='Qaratqich/tushum va jo‘nalish/o‘rin-payt formalari birlashishi tasvirlangan. «Buxoroda 4 kelishik» barcha hozirgi nutq profillarining qat’iy soni sifatida olinmadi. Qorako‘l/Olot uchun tushum -i varianti aniq qayd etilgan.'),
        dict(source_id='B1',pdf_page=22,observation='Buxoro hozirgi zamonida -ap ko‘rsatkichi darslikda qayd etilgan; o‘g‘uzning -yatir variantlari bilan bitta majburiy qoida qilinmadi.'),
        dict(source_id='B2',pdf_page=20,printed_pages=[36,37],observation='Umumiy darslik f→p bayonida Samarqand–Buxoroni istisno qiladi. B4:14–15 o‘g‘uz materiali f o‘rnida p ni qayd etadi. «Buxoro» yorlig‘i bilan barcha f larni p ga aylantirish profil farqini yo‘qotadi.'),
        dict(source_id='B2',pdf_page=29,printed_pages=[54,55],observation='Samarqand–Buxoro guruhida -ga/-da almashinuvi; shu sahifadagi Jizzax va Qarshi gaplari Buxoroga tegishli bevosita gap deb olinmadi.'),
        dict(source_id='B2',pdf_page=39,printed_pages=[74,75],observation='Ikki tilli Buxoro nutqidagi izofali birikmalar va gap tartibi tasvirlangan; matnda Buxoro guruhida sifatdosh kesimning shaxs-son bilan moslashmasligi ham qayd etilgan. Keltirilgan man kelgan jumlasidan barcha kesimlarda shaxs qo‘shimchasini olib tashlash qoidasi chiqarilmaydi.'),
        dict(source_id='B4',pdf_pages=[12,13,14,28,29],observation='Muallif sheva xususiyatini saqlagan o‘g‘uz vakillari uchun 13 unli haqidagi tasnifni beradi; ayrim tovushlar yosh va adabiy til ta’siriga bog‘langan. Bu butun Buxoroning bir xil tovushlar tizimi degani emas.'),
        dict(source_id='B4',pdf_page=21,observation='Hozirgi zamon -y, -yatir/-vatir va -yatan turidagi variantlar; -yap/-moqda kamroq deyilgan. Variantlar ichki hudud va vaziyatga qarab tanlanadi; o‘tgan zamonga ko‘chirilmaydi.'),
        dict(source_id='B4',pdf_pages=[23,25],observation='Adabiy til ta’sirida -ning, -gan va boshqa shakllar markazga yaqin nutqda uchrashi qayd etiladi; lahja affikslarini har gapga majburlash asoslanmaydi.'),
    ],source_conflicts=[
        dict(source_id='B4',pdf_pages=[20,29],issue='Asosiy matnda aniq o‘tgan zamon -dı/-dï, -tı/-tï misollar bilan berilgan; xulosa 5-bandda -dır/-dïr/-tır/-tïr deb yozilgan.',decision='-di ni hamma joyda -dir ga almashtirish olinmadi. Aniq keldi/geldi/gelli va aytdi/aytti misollari alohida saqlandi.'),
        dict(source_id='B3',pdf_page=3,issue='Bay-may va o‘qigan-mo‘qigan uchun istehzoli izoh berilgan.',decision='Boy emas yoki ilmli emas degan ma’nolar barcha takror shakllariga majburiy biriktirilmadi; istehzo va befarqlik konteksti alohida talab qilinadi.'),
    ]))

profiles=[
 dict(name='Buxoro qarluq va Samarqand–Buxoro shahar guruhi',sources=['B1:35–36','B2:39','B3:119–121 (qarluq bo‘limlari)'],notes='Shahar guruhi va viloyatning hamma aholisi bir xil emas. Tojik tili bilan aloqa va izofa bu qatlamda qayd etilgan.'),
 dict(name='Buxoro o‘g‘uz shevalari',sources=['B4:9,12–30','B3:119–120 (o‘g‘uz bo‘limlari)'],districts_as_research_scope=updates['B4']['fieldwork_districts'],notes='Tumanlar dala materialining qamrovi; shu tumanlarning barcha aholisi o‘g‘uz degani emas. Ko‘p misol uchun alohida qishloq yorlig‘i avtoreferatda yo‘q.'),
 dict(name='G‘ijduvondagi yoshi katta kishilar nutqi kuzatuvi',sources=['B3:119 jölkirā'],notes='Aynan bitta kuzatuv uchun hudud va yosh berilgan; qo‘shni barcha gaplar G‘ijduvonga avtomatik ko‘chirilmagan.'),
 dict(name='Buxoroning qipchoq nutqi',sources=['B1:31–32 tasnif'],notes='Umumiy tasnifda borligi qayd etilgan. Yangi besh faylda alohida Buxoro qipchoq suhbati yetarli darajada berilmagani uchun to‘liq dialog profili tuzilmadi.'),
 dict(name='1971-yilgi Buxoro yorlig‘idagi lug‘aviy qatlam',sources=['E1 tanlangan maqolalari','B5:677–678'],notes='Ko‘p birliklarda ichki lahja va bugungi yoshlar nutqi belgisi yo‘q; so‘zlarga qarluq/o‘g‘uz yorlig‘i taxminan qo‘yilmadi.'),
]
write('HUDUDIY_PROFILLAR.json',dict(profiles=profiles))
write('OLDINGI_HUDUDLAR_QIYOS.json',dict(comparisons=[
 dict(topic='Takror kitob',sources=['B2','Samarqand M5'],result='SHA-256 teng; bir manba ikki mustaqil tasdiq emas.'),
 dict(topic='Bir muallifning ikki nashri',sources=['B1, 2011','Samarqand M1 / Qashqadaryo Q3, 2016'],result='Fayllar aynan teng emas; umumiy tasnifning takrori yangi dala qaydi sifatida hisoblanmaydi.'),
 dict(topic='Belanchak',sources=['E1:17','B5:678'],result='Buxoro alvonj / Qashqadaryo alvonch. Shu juftlikdan barcha ch tovushini j ga almashtirish qoidasi chiqarilmaydi.'),
 dict(topic='Quvur',sources=['E1:75','B5:678'],result='Buxoro g‘ulva/g‘ulba, Qashqadaryo g‘alva; lug‘atda sopol quvur ma’nosi aniq.'),
 dict(topic='Taom nomlari',sources=['E1:43','Samarqand M4-B:205'],result='Buxoro barak va Samarqand barak chuchvara turida qayd etilgan; viloyatga mutlaq xos so‘z deb olinmaydi. Buxoro barak alohida yangi yozuv sifatida ushbu lug‘at ro‘yxatiga qo‘shilmadi.'),
 dict(topic='Qalampir',sources=['B2:75','Samarqand M2:42'],result='Qalamfur / qalampur yozuv farqi saqlandi; talaffuz audio bilan tasdiqlanmagan.'),
 dict(topic='Og‘iz suti va jimlik',sources=['E1:78,272'],result='Dammakak va falla uchun lug‘at Buxoro bilan birga Samarqandni ham ko‘rsatadi.'),
]))

samples=[]
def sample(sid,page,quote,meaning,scope,kind='Misol jumla',translation_status='Manbaning o‘z tarjimasi'):
    t=texts[sid][page-1]
    assert quote in t,(sid,page,quote)
    samples.append(dict(id=f'BS{len(samples)+1:03}',source_id=sid,pdf_page=page,printed_pages=printed(sid,page),
                        source_text_extracted=quote,meaning_uz=meaning,scope=scope,genre=kind,
                        translation_status=translation_status,usage='Manba namunasi; bot yaratgan yoki zamonaviy audio bilan tasdiqlangan dialog emas.'))
sample('B3',2,'Muni išlätkännän kijin žājigä qāj, män qidirip jurmäj.',
       'Buni ishlatgandan keyin joyiga qo‘y, men qidirib yurmay.',q,translation_status='Tahririy adabiy o‘qilish; maqolada alohida adabiy tarjima yo‘q')
sample('B3',2,'Körpäjä öränip jāt','Ko‘rpaga o‘ranib yot','B3 o‘g‘uz konteksti')
sample('B3',3,'Körpäčäjä ötir','Ko‘rpachaga o‘tir','B3 o‘g‘uz konteksti')
sample('B3',3,'Sixakti opke','Qirg‘ichni olib kel','B3 o‘g‘uz konteksti')
sample('B3',3,'Lövlādi tāzäläš keräk','Loviyani tozalash kerak','B3 o‘g‘uz konteksti')
sample('B3',3,'Ānämä āldim','Onamga oldim','B3 o‘g‘uz konteksti')
sample('B3',4,'Nān-pān, čāj-pāj, kölä-pölä [sho‘rdanak] keräjmäsmi?',
       'Non-pon, choy-poy, sho‘rdanak kabi narsalar kerak emasmi?',q,translation_status='Tahririy adabiy o‘qilish; sho‘rdanak izohi manbaning o‘zida')
sample('B3',3,'Iki žörä bäčäliktän birä kättä bölänlä. Dävr kelip ikkäläsijäm öz bäxtini izläp\n     jölä čiqan.',
       'Ikki jo‘ra bolalikdan birga katta bo‘lgan. Vaqti kelib ikkalasi ham o‘z baxtini izlab yo‘lga chiqqan.',
       'B3: o‘g‘uz misollari orasida, aniq qishloq ko‘rsatilmagan',kind='Hikoya parchasi',translation_status='Tahririy adabiy o‘qilish; to‘liq gapma-gap tarjima maqolada yo‘q')
write('NUTQ_NAMUNALARI.json',dict(description='Manbadagi yozma misollar. B3 fonetik j ko‘pincha y ni, ž esa j ni bildiradi; avtomatik j-lovchi profil deb talqin qilinmaydi.',sample_count=len(samples),samples=samples))
print(f'{len(lex)} lug‘aviy birlik; {len(candidates)} tekshiriladigan birlik; {len(rules)} grammatik misol; {len(samples)} nutq namunasi.')
