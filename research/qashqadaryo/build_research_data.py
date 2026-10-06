"""Rebuild source indices and curated research notes; this is not model training."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

manifest = json.loads((ROOT / 'download_manifest.json').read_text())
metadata = {
    'Q1': dict(title='Qashqadaryo shevalarining o‘rganilish tarixidan', author='Xojamurod Jabborov', year=2025, publisher='Uluslararası Türk Dünyası Araştırmaları Dergisi, 8(2), 139–146', doi='10.59182/tudad.1619886', scope='Qashqadaryo tadqiqotlari tarixi; boshqa asarlardan ikkilamchi misollar', read_pages=list(range(1,9)), reading='To‘liq maqola o‘qildi.'),
    'Q2': dict(title='O‘zbek dialektologiyasi fanidan o‘quv-uslubiy majmua', author='Sh. Xudoyqulova', year=2008, publisher='Guliston davlat universiteti', scope='Umumo‘zbek dialektologiya kursi', read_pages=[19,20,32,33,34,38,46], reading='Tuzilishi va Qashqadaryo bo‘yicha qidiruv natijalari ko‘rildi; ko‘rsatilgan asosiy nazariy sahifalar o‘qildi. Topshiriq va testlar foydalanuvchi buyrug‘i sifatida bajarilmadi.'),
    'Q3': dict(title='O‘zbek dialektologiyasi', author='Samixon Ashirboyev', year=2016, publisher='Navro‘z, Toshkent', scope='Umumo‘zbek darsligi; Qarshi/Koson grammatikasi va Qashqadaryo nutq namunalari', read_pages=[13,14,15,16,24,33,34,38,39,40,41,42,44,46,60,61,62,63,64,72,87,97,98,99,100,101], reading='Qashqadaryoga tegishli tasnif, fonetika, grammatika, Koson ertagi va Kitob tumani Chechak nutqi o‘qildi. Qolgan hududiy qidiruv topilmalari kontekst bilan ko‘rildi. Butun darslik to‘liq o‘qilgan deb hisoblanmaydi.'),
    'Q4': dict(title='O‘zbek xalq shevalari lug‘ati', editor='Sh. Sh. Shoabdurahmonov', year=1971, publisher='Fan, Toshkent', scope='Ko‘p hududli, uch lahjali lug‘at; qarindoshlik ilovasi ham bor', read_pages=[1,2,3,4,5,6,7,8,12,13,14,15,16,18,21,24,25,27,28,48,90,93,97,116,118,129,130,147,210,217,276,285,325,332,333,353], visual_checked_pages=[16,18,21,24,25,27,28,48,90,93,97,116,118,129,130,147,210,217,276,285,325,332,333,353], reading='Kirish, foydalanish tartibi, hudud belgisi va tanlangan lug‘aviy maqolalar o‘qildi. 410 sahifaning barchasi so‘zma-so‘z tekshirilmagan; hudud qidiruvi to‘liq yoki xatosiz ro‘yxat emas.'),
}
sources=[]
with (ROOT/'SAHIFALAR.jsonl').open('w') as out:
    for m in manifest:
        sources.append({**m, **metadata[m['id']]})
        pages=Path(m['text_path']).read_text().split('\f')
        assert len(pages) >= m['pages']
        for n in range(1,m['pages']+1):
            printed = 138+n if m['id']=='Q1' else n-1 if m['id']=='Q3' and 13<=n<=101 else n if m['id']=='Q4' and 12<=n<=353 else None
            out.write(json.dumps(dict(source_id=m['id'],pdf_page=n,printed_page=printed,text=pages[n-1],text_status='Avtomatik ajratilgan matn; shrift/OCR xatolari bo‘lishi mumkin.'),ensure_ascii=False)+'\n')
save('MANBALAR.json',sources)

# Latin forms below are editorial reading forms, not exact phonetic transcription.
# The Cyrillic headwords were read from the cited page images.
rows=[
 ('aq','ақ','sut-qatiq',['Qovchin'],16,None,''),
 ('aqlamatta','ақламатта','aqalli, hatto',['Qashqadaryo'],16,None,''),
 ('alqamoq','алқамоқ','duo qilmoq',['Qashqadaryo'],18,None,''),
 ('arrabur','аррабур','jodi, somon maydalash asbobi',['Qarshi'],21,None,'Manbadagi «жоди» izohining tushuntirilgan shakli.'),
 ('avliya','авлия','qabriston',['Beshkent guruhi'],24,None,'Adabiy tildagi avliyo ma’nosi bilan tenglashtirilmasin.'),
 ('aylava','айлава','qabriston',['Beshkent guruhi'],24,None,'Avliya bilan parallel variant.'),
 ('avg‘a','авға','dovon',['Yuqori Qashqadaryo'],24,None,''),
 ('addisar','аддисар','bo‘lsa-bo‘lmasa, baribir, albatta',['Qashqadaryo'],25,None,'Shu maqoladagi addusar varianti Samarqand/Buxoroga tegishli.'),
 ('aynak(i)la','айнак(и)ла','ko‘rmoq',['Qashqadaryo'],27,None,'Lug‘atda aynan shu shaklda; sun’iy ravishda -moq qo‘shilmadi.'),
 ('ayrit qilmoq','айрит қилмоқ','farqlamoq, ajratmoq',['Qashqadaryo'],27,None,''),
 ('ayron','айрон','qatiqqa suv qo‘shilgan ichimlik',['Qashqadaryo','Toshkent','Jizzax'],27,'I','Bu va keyingi maqola alohida ma’nolardir.'),
 ('ayron','айрон','qimron: tuya sutidan qilingan qimiz',['Qashqadaryo'],27,'II','Tuya suti ma’nosini barcha ayron ishlatilishiga ko‘chirmaslik kerak.'),
 ('akkal','аккал','ahd, qat’iy qaror',['Qashqadaryo'],27,None,''),
 ('alaxom','алахом','alag‘da bo‘lmoq, xavotirlanmoq',['Yuqori Qashqadaryo'],28,None,'Lug‘at alag‘da bo‘lmoq bilan izohlaydi; xavotirlanmoq — tushuntirish.'),
 ('ba:nnave','бэ:ннэве','yaxshi hamki, har holda',['Yuqori Qashqadaryo'],48,None,'Cho‘ziqlik belgisi saqlandi; lotin yozuvi soddalashtirilgan.'),
 ('bo','бо','tag‘in, yana',['Qashqadaryo','Buxoro'],48,None,''),
 ('bodi','боди','1. takabbur, dimog‘dor; 2. ko‘p gapiruvchi kishi',['Qashqadaryo'],48,None,''),
 ('badhavo','бадҳаво','ob-havo',['Qashqadaryo'],48,None,'Salbiy ob-havo deb talqin qilinmasin.'),
 ('boza','боза','buyon, beri (vaqtga nisbatan)',['Qashqadaryo'],48,None,''),
 ('bolg‘undor','болғундор','taxmon',['Qashqadaryo'],48,None,'Maqola izohi keyingi sahifaga davom etadi; taxmon ekani shu sahifada aniq.'),
 ('duvora','дувора','ikkinchi',['Qashqadaryo'],90,None,''),
 ('duv-duvora','дув-дувора','ikkinchi marta',['Qashqadaryo'],90,None,''),
 ('dushvara','душвара','chuchvara',['Mirishkor'],93,None,''),
 ('er','эр','u yer',['Qashqadaryo'],97,None,'Erkak yoki turmush o‘rtog‘i ma’nosi bilan aralashtirilmasin.'),
 ('ilmissiq','илмиссиқ','iliq',['Qashqadaryo'],116,None,'Buxorodagi ilimsindi variantidan farqlanadi.'),
 ('inak','инак','sigir',['Qashqadaryo','Samarqand'],116,None,'Qashqadaryoda ina: varianti ham berilgan; misol Shahrisabzdan. Buxoro varianti alohida transkripsiyada.'),
 ('innim','инним','farosat, odob',['Qashqadaryo'],116,None,''),
 ('ichkuyar','ичкуяр','jonkuyar',['Qashqadaryo','Andijon'],118,None,''),
 ('ishi-kuchi / ishkuchi','иши-кучи / ишкучи','o‘y-fikri, qiladigan ishi',['Qashqadaryo'],118,None,''),
 ('ishtarop','иштароп','shoshilinch',['Qashqadaryo'],118,None,''),
 ('yakshoxa','якшоха','qiyshiq, bir tomonlama (masalan, do‘ppini kiyish)',['Qashqadaryo'],129,None,''),
 ('yangngi','янгнги','endi',['Qashqadaryo'],129,None,'Lug‘at yozuvi ng + g tovushlarini ajratadi; zamonaviy «yangi» bilan ma’no bir xil emas.'),
 ('ya:zayil','йэ:зэйил','har doim',['Qashqadaryo'],129,None,'Cho‘ziqlik saqlandi; lotin ko‘rinishi fonetik aniqlik da’vosi emas.'),
 ('ya:lux','йэ:лух','ko‘tara, bir yo‘la',['Qashqadaryo'],129,None,''),
 ('yodi baxay','ёди бахай','barakalla, ofarin',['Qashqadaryo','Buxoro'],129,None,'Ma’no va Qashqadaryo misoli 130-sahifada davom etadi.'),
 ('yod-yuxlov','ёд-йўхлов','yo‘qlab turish, xabar olib turish',['Qashqadaryo'],130,None,''),
 ('yo:mur','йо:мур','yomg‘ir',['Qashqadaryo'],130,None,'Shu maqoladagi boshqa variantlar boshqa hududlarga tegishli.'),
 ('yoshimmachog‘','ёшиммачоғ','bekinmachoq',['Qashqadaryo'],130,None,'Jizzax shaklining unlilari alohida transkripsiyada berilgan.'),
 ('kubbala','кўббала','juda ko‘p',['Qashqadaryo'],147,None,'Manbadagi sodda kirill yozuviga tayangan o‘qilish; transkripsiyada kobbalo.'),
 ('kutirak','кўтирак','choyning oxirgi piyolasini ichgan kishi',['Qashqadaryo'],147,None,''),
 ('paygir','пайгир','xamirturush',['Qashqadaryo'],210,None,''),
 ('porimoq','поримоқ','xush kelmoq, yoqmoq',['Qashqadaryo'],217,'I','Umumiy yoqtirish ma’nosi.'),
 ('porimoq','поримоқ','ovqatning organizmga yoqishi, mos kelishi',['Qarshi'],217,'II','Manbada ovqatga tegishli alohida ma’no.'),
 ('hayme','хайме','xo‘pmi (uqtirish, tayinlash)',['Qashqadaryo'],276,None,'Faqat odatiy xo‘p tasdig‘i deb ma’noni toraytirmaslik kerak.'),
 ('hambo‘yinsa / hampira','ҳамбўйинса / ҳампира','tengqur, tengdosh',['Qashqadaryo'],285,None,''),
 ('hamishaki','ҳамишаки','har doim, doimiy',['Qashqadaryo'],285,None,''),
 ('hamsatavaq','ҳамсатавоқ','qo‘shnilar o‘rtasidagi taom almashuvi',['Qashqadaryo'],285,None,'Oddiy taom yoki idish nomi emas.'),
 ('hamsoya','ҳамсоя','qo‘shni',['Qashqadaryo'],285,None,'Boshqa joylarda ham ishlatilishi mumkin; bu yerda Qashqadaryo belgisi tasdiqlangan.'),
 ('aytti','айтти','xola',['Qarshi'],325,'2','Turkiston/Iqonda ayni maqolaning 1-ma’nosi opa; Qarshiga o‘sha ma’no ko‘chirilmasin.'),
 ('oybiye','ойбийе','opa; o‘zidan katta ayolga hurmat bilan murojaat',['Shahrisabz','Chiroqchi','Yakkabog‘','Qamashi','Kitob','Miroqi'],332,None,''),
 ('oyxola','ойхола','xola; o‘zidan katta ayolga hurmat bilan murojaat',['Yakkabog‘','Chiroqchi','Qamashi','Shahrisabz','Kitob'],332,None,'Izoh va misol 333-sahifada davom etadi.'),
 ('enabiye','энабийе','qaynana',['Shahrisabz','Yakkabog‘','Chiroqchi','Qamashi','Kitob'],333,None,'Shu maqoladagi oybi varianti Buxoroga tegishli.'),
 ('o‘na','ўна','ona',['Beshkent','Mirishkor'],353,None,'Lug‘at ana bosh so‘ziga havola beradi.'),
 ('o‘ta','ўта','ota',['Beshkent','Mirishkor'],353,None,'Lug‘at ata bosh so‘ziga havola beradi.'),
 ('o‘ta-o‘na','ўта-ўнэ','ota-ona',['Beshkent','Mirishkor'],353,None,'Kirill yozuvi manba transkripsiyasini o‘qish uchun keltirilgan.'),
]
entries=[]
for latin,cyrillic,meaning,regions,page,sense,note in rows:
    entries.append(dict(id=f'QL{len(entries)+1:03}',form_latin=latin,headword_cyrillic_reading=cyrillic,meaning_uz=meaning,regions=regions,source_id='Q4',pdf_page=page,printed_page=page,sense=sense,evidence='Tanlangan maqola sahifa tasviri bilan solishtirildi.',writing_status='Lotin va kirill shakllari tahririy o‘qilish; aniq fonetik transkripsiya yoki diplomatik ko‘chirma emas.',dialect_branch='Hudud belgisidan avtomatik aniqlanmagan.',current_usage='1971-yil manbasida qayd etilgan; bugungi qo‘llanish sheva vakili bilan tasdiqlanmagan.',note=note))
secondary=[
 ('azza','ariza',['Yuqori Qashqadaryo'],4,142),
 ('javrannan','nohaqdan, gunohsiz',['Yuqori Qashqadaryo'],4,142),
 ('patarat','vayrona',['Yuqori Qashqadaryo'],4,142),
 ('bo‘yimjon','baqlajon',['Yuqori Qashqadaryo'],4,142),
 ('qas','belbog‘',['Yuqori Qashqadaryo'],4,142),
 ('alvonch','bola belanchagi',['Qarshi'],5,143),
 ('joyposh','so‘zana, palak',['Qarshi'],5,143),
 ('tota','buvi, momo',['Qarshi'],5,143),
]
for latin,meaning,regions,page,printed in secondary:
    entries.append(dict(id=f'QL{len(entries)+1:03}',form_latin=latin,meaning_uz=meaning,regions=regions,source_id='Q1',pdf_page=page,printed_page=printed,evidence='Jabborov maqolasida Jo‘rayev/Shermatov asarlaridan keltirilgan ikkilamchi misol.',latin_status='Tahririy o‘qilish; maqola maxsus transkripsiyadan foydalanadi.',dialect_branch='Hududga asoslanib yagona lahjaga biriktirilmagan.',current_usage='2025-yil maqolasida tarixiy asardan iqtibos; bugungi qo‘llanish tasdiqlanmagan.'))
save('LUGAT.json',dict(description='Manbali ishchi lug‘at. Hamma hudud uchun yagona profil yoki tayyor trening to‘plami emas.',entry_count=len(entries),entries=entries))

rules=[
 ('oldi','alli',['Qarshi','Shahrisabz'],24,'ld → ll, to‘liq assimilatsiya'),
 ('bo‘ldi','boddi',['Shahrisabz'],24,'ld → dd, to‘liq assimilatsiya'),
 ('oldim','allim',['Samarqand-Buxoro guruhi (Qarshi, Koson ham keltirilgan)'],60,'Oldingi l keyingi d ga ta’sir qiladi.'),
 ('keldim','kellim',['Samarqand-Buxoro guruhi (Qarshi, Koson ham keltirilgan)'],60,'Xuddi shu assimilatsiya misoli.'),
 ('qilamiz','qilavuz',['Qarshi','Toshkent'],38,'I shaxs ko‘plik -vuz.'),
 ('kelasizlar','kelasila',['Qarshi','Toshkent'],39,'II shaxs ko‘plik -sila.'),
 ('urdik','urdi:y',['Qarshi','Toshkent'],40,'I shaxs ko‘plik -i:y; cho‘ziqlik belgisi saqlandi.'),
 ('bordingiz','bordizla',['Qarshi'],41,'II shaxs ko‘plik -zla; unli nozikligi soddalashtirilgan.'),
 ('oldinglar','oldiyla',['Qarshi','Toshkent'],41,'II shaxs ko‘plik -yla.'),
 ('kelinglar','keliyla',['Qarshi','Toshkent'],42,'Buyruq mayli, II shaxs ko‘plik -yla.'),
 ('olib boringlar','oboriyla',['Qarshi','Toshkent'],42,'Buyruq mayli; qisqargan fe’l va -yla.'),
 ('xurmaga','xurmaya',['Qarshi'],34,'Jo‘nalish -ya; maxsus transkripsiyadagi j bu yerda y tovushidir.'),
 ('kelyapman','kelappan',['Samarqand-Buxoro guruhi (Qarshi, Koson ham keltirilgan)'],61,'Davom fe’li -ap; butun Qashqadaryo uchun majburiy qoida emas.'),
 ('so‘rayapsan','so‘ropsan',['Samarqand-Buxoro guruhi (Qarshi, Koson ham keltirilgan)'],61,'Davom fe’li misoli; unlilar tahririy o‘qilishda.'),
 ('kelar edim','kelayidim',['Qarshi-Buxoro guruhidagi shevalar'],61,'Sifatdoshdagi r → y; barcha r tovushlariga qo‘llanmaydi.'),
 ('kelmas edim','kelmayidim',['Qarshi-Buxoro guruhidagi shevalar'],61,'Bo‘lishsiz sifatdoshdagi s → y; boshqa s larni almashtirmaslik kerak.'),
]
save('GRAMMATIKA.json',dict(description='Darslikdan tanlangan shakllar. Lotin yozuvi soddalashtirilgan; qoida qo‘llanish sohasi hudud va grammatik shakl bilan cheklangan.',rules=[dict(standard=a,dialect_reading=b,regions=reg,source_id='Q3',pdf_page=p,printed_page=p-1,explanation=note,current_usage='Hozirgi nutqda alohida tekshirish kerak.') for a,b,reg,p,note in rules]))

compare=[('oyg‘oq','ayg‘aq','shatta, janjalkash',3,230),('chuvoq','chuvaq','issiq',4,231),('oxmoy','axmay','paxta yog‘i',4,231),('ottaba','attaba','oftoba',4,231),('tutandiriq','tutantiriq','quruq o‘tin',4,231),('boybicha','baybicha','xotin-qizlarga murojaat',4,231),('tobaq','tabaq','milliy kurashda polvon uchun sovrin',4,231),('shirvoz','shirboz','sutdan ayrilmagan qo‘zi',3,230)]
save('SURXONDARYO_QIYOS.json',dict(source_id='S2',source_text='/workspace/research/surxondaryo/source_2.txt',doi='10.5281/zenodo.10067310',scope='Maqola jadvalidagi qiyos; Qashqadaryo tomoni B. Jo‘rayevning Yuqori Qashqadaryo kitobiga tayangan. Barcha tumanlar uchun universal moslik emas.',pairs=[dict(qashqadaryo=q,surxondaryo=s,meaning_uz=meaning,pdf_page=p,printed_page=pp) for q,s,meaning,p,pp in compare]))
print(f'{len(sources)} sources; {sum(s["pages"] for s in sources)} indexed PDF pages; {len(entries)} lexical entries; {len(rules)} grammar examples.')
