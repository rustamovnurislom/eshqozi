"""Dalil kartotekasi: yozishma shakli, ma’no, qidiruv soni va bot namunalari aralashtirilmaydi."""
import csv
import json
import re
from pathlib import Path
import analyze_export as a

ROOT=Path(__file__).parent
BASE=ROOT.parent/'toshkent'

# Har qatorda lemma, eksportdagi qidiruv shakllari, ma’no, tur va talqin chegarasi.
families=[
 ('qalesla',['qalesla','qalesila'],'qalaysizlar; davraga hol-ahvol savoli','murojaat','Ko‘plik/hurmat konteksti alohida; faqat yigitlarga xos shakl emas.'),
 ('qales',['qales','qalesa','qale','qalesan'],'qalaysan/qalay; hol-ahvol savoli','murojaat','Qisqa yozuvda adresat shaxsi hamisha to‘liq yozilmagan.'),
 ('qalesiz',['qalesz','qalesiz','qaleysiz','qalisizz'],'qalaysiz; hurmatli yoki ko‘plik savoli','murojaat','Ko‘cha uslubida sizlash ham uchraydi.'),
 ('nma',['nma'],'nima','yozuv_qisqarishi','Qisqartma; alohida mahalliy predmet yoki ruscha slang emas.'),
 ('nme/nmey',['nme','nmey'],'nima/nega mazmunidagi qisqa savol','yozuv_qisqarishi','Vaziyatga qarab sababni ham so‘raydi; hammasini bitta glossga majburlash mumkin emas.'),
 ('nmala',['nmala'],'nimalar; nima ishlar/gaplar','yozuv_qisqarishi','Odatda savol gap tarkibida; manbada -lar qisqargan yozuv.'),
 ('nmaga',['nmaga'],'nimaga','yozuv_qisqarishi','Sabab yoki maqsad savoli kontekst bilan.'),
 ('nma gap / nmagap',['nma gap','nmagap','nmagapla','nmgap'],'nima gap; davrani ochish','diskurs','Fakt talab qiluvchi savol yoki oddiy hol-ahvol bo‘lishi mumkin.'),
 ('qvosan',['qvosan','qvosanmi'],'qilyapsan; qilayapsanmi','fel_shakli','II birlik; hamma shaxsga bir xil qo‘llanmaydi.'),
 ('qvos',['qvos','qvosmi'],'qilyapsiz/qilyapsan mazmunidagi qisqargan shakl','fel_shakli','Oka bilan qvos yozuvi hurmatli adresatda ham uchraydi; shaxsni vaziyat aniqlaydi.'),
 ('qvosla/qvosila',['qvosla','qvosila'],'qilyapsizlar','fel_shakli','II ko‘plik/adresat; qisqartma tugallanishi aniqligi tekshiriladi.'),
 ('qvoman/qvomma',['qvoman','qvomma'],'qilyapman','fel_shakli','I birlik; qovurmoq kabi tashqi o‘xshash so‘zlardan ajratiladi.'),
 ('qivotti/qvoti',['qivotti','qvoti','qvot'],'qilyapti','fel_shakli','III shaxs mazmuni; har votti bilan tugagan so‘z bir xil ildiz emas.'),
 ('kevoman',['kevoman'],'kelyapman','fel_shakli','Kelish yo‘nalishi ketishga aylantirilmaydi.'),
 ('kevot/kevoti',['kevot','kevoti'],'kelyapti/kelyap- mazmunidagi qisqa yozuv','fel_shakli','Tugallangan yoki qisqargan gap kontekstda o‘qiladi.'),
 ('ketvoman',['ketvoman','ketvoma'],'ketyapman','fel_shakli','I birlik; qaytish/kelish bilan adashtirilmaydi.'),
 ('ketvosan',['ketvosan','ketvosanu'],'ketyapsan','fel_shakli','II birlik; so‘z oxiridagi yuklama qo‘shimcha tus beradi.'),
 ('ketvoti',['ketvoti','ketvott'],'ketyapti','fel_shakli','III shaxs yoki tugallanmagan tez yozuv.'),
 ('etvoman',['etvoman','etvoma'],'aytyapman','fel_shakli','Tanlangan misollarda aytish; universal etmoq tarjimasi emas.'),
 ('dvoman',['dvoman','dvoma','dvomman'],'deyapman','fel_shakli','I birlik aytish fe’li, chatda qisqartirilgan.'),
 ('bovot/buvot',['bovot','bovoti','buvot'],'bo‘lyapti/bo‘layap-','fel_shakli','Nima bo‘lyapti mazmunida; tugallanmagan yozuvni yangi zamon deb olmaymiz.'),
 ('bomi',['bomi'],'bormi','grammatik_qisqarish','Borlik haqida savol; emaslikka aylantirilmaydi.'),
 ('bomid/bomidi',['bomid','bomidi'],'bo‘lmaydi/bo‘lmaydimi mazmunidagi qisqa shakl','grammatik_qisqarish','Nomeri bomidi kabi gaplar aniq kontekst talab qiladi.'),
 ('yom/yomi',['yom','yomi'],'yo‘qmi/yo‘q mazmunidagi qisqartma','grammatik_qisqarish','Bitta doimiy paradigmani faqat yozuvdan chiqarish mumkin emas.'),
 ('kere',['kere'],'kerak','talaffuzga_yaqin_yozuv','Oxirgi k tushgan yozuv; barcha k ni tushirish algoritmi emas.'),
 ('keremas',['keremas'],'kerak emas','grammatik_qisqarish','Talabning inkori; kerak bilan ma’no qarama-qarshi.'),
 ('man',['man'],'men','olmosh','Umumiy norasmiy shakl; joylashuvni yolg‘iz o‘zi ko‘rsatmaydi.'),
 ('san',['san'],'sen','olmosh','Adresat bilan yaqinlik/munosabatni hisobga olish kerak.'),
 ('manga',['manga'],'menga','olmosh','Jo‘nalish munosabati; boshqa hududlarda ham bor.'),
 ('sanga',['sanga'],'senga','olmosh','Menga bilan shaxs farqi saqlansin.'),
 ('mani',['mani'],'meni/mening','olmosh','Tushum va qaratqichni gap qurilishi ajratadi.'),
 ('sani',['sani'],'seni/sening','olmosh','Tushum va qaratqichni gap qurilishi ajratadi.'),
 ('bza',['bza'],'biz/biza','olmosh','I ko‘plik; qisqartirish va sheva belgisi aralashgan.'),
 ('sz',['sz'],'siz','yozuv_qisqarishi','Ko‘cha yozishmasida hurmatni avtomatik o‘chirish uchun asos yo‘q.'),
 ('ozin',['ozin'],'o‘zing','olmosh','Qisqartma; kimning o‘zi ekanini kontekst belgilaydi.'),
 ('ozila',['ozila','oziladaci'],'o‘zlaringiz/o‘zlaringizda-chi','olmosh','Savolni suhbatdoshga qaytarish vazifasi ham bor.'),
 ('oka',['oka'],'aka; katta/yaqin kishiga murojaat','murojaat','Yosh, qarindoshlik yoki haqiqiy maqom avtomatik taxmin qilinmaydi.'),
 ('bolla',['bolla'],'bolalar','ot_qisqarishi','Davra ko‘pligi; barcha davra yigitlardan iboratligini isbotlamaydi.'),
 ('qatta',['qatta','qattasan'],'qayerda/qayerdasan','savol','Shaxs va joylashuvni adashtirmaslik kerak.'),
 ('qattan',['qattan'],'qayerdan','savol','Qatta savolidan yo‘nalish jihatidan farq qiladi.'),
 ('hoz',['hoz'],'hozir','yozuv_qisqarishi','Hozirning har doim talaffuzdagi shakli emas, tez yozuv ham bo‘lishi mumkin.'),
 ('end',['end'],'endi','yozuv_qisqarishi','Inglizcha end ma’nosi bilan avtomatik tenglashtirilmaydi.'),
 ('bn',['bn'],'bilan','yozuv_qisqarishi','Internet yozuvi; Toshkentga mutlaq xos deb bo‘lmaydi.'),
 ('db',['db'],'deb','yozuv_qisqarishi','Texnik qisqartma DB bilan gap kontekstida ajratiladi.'),
 ('un',['un'],'uchun','yozuv_qisqarishi','Faqat tanlangan kontekstlarda; un otiga doimiy almashtirish emas.'),
 ('kr',['kr'],'kir','yozuv_qisqarishi','Buyruq, taklif yoki ildizning qisqa yozuvi.'),
 ('krb',['krb'],'kirib','yozuv_qisqarishi','Ravishdosh vazifasi; kr buyruq shakli bilan bir emas.'),
 ('cqb',['cqb'],'chiqib','yozuv_qisqarishi','c bilan ch berilishi va unlilar tashlanishi birga.'),
 ('qow',['qow','qowb'],'qo‘sh/qo‘shib','yozuv_qisqarishi','w orqali sh yozuvi; shaxs va buyruq konteksti saqlansin.'),
 ('yaxw/yaxwi',['yaxw','yaxwi','yahw','yahwi'],'yaxshi','grafik_variant','w=sh internet yozuvi; audio orqali talaffuz tekshirilmagan.'),
 ('wunaqa',['wunaqa'],'shunaqa','grafik_variant','w=sh; global almashtirish ayniqsa ruscha/inglizcha so‘zlarda xato beradi.'),
 ('bowqa',['bowqa'],'boshqa','grafik_variant','w=sh internet yozuvi.'),
 ('iwla',['iwla','iwlarm'],'ishlar/ishlarim','grafik_variant','Chatda ishlar qale kabi hol-ahvol tarkibi; literal ish fe’li bilan kontekst ajratiladi.'),
 ('gapla',['gapla'],'gaplar','ot_qisqarishi','Nima gaplar ma’nosida; faqat yozuvdan audio tasdiq olinmaydi.'),
 ('gap yo',['gap yo','gapyo'],'gap yo‘q; qoyil yoki gap yo‘qligi','diskurs','Maqtov va literal gap yo‘qligi vaziyatga qarab.'),
 ('hop/xop',['hop','xop',"xo'p"],'xo‘p; rozilik','diskurs','Qisqa qabul javobi, har safar yangi ma’lumot emas.'),
 ('xm/hm',['xm','hm','xmm','hmm'],'tasdiq, o‘ylash yoki suhbatni davom ettiruvchi qisqa reaksiya','diskurs','Ohang va kontekstsiz doimo befarqlik deb olinmaydi.'),
 ('raxmat',['raxmat'],'rahmat','talaffuzga_yaqin_yozuv','h/x grafik/talaffuz farqi; alohida audio dalili yo‘q.'),
 ('yoĝe',['yoĝe'],'yo‘g‘-e; hayrat/ishonmaslik','diskurs','Unicode belgisi aynan saqlangan; yo‘q inkori bilan doimiy teng emas.'),
 ('voy/voooy',['voy','vooy','voooy'],'hayrat, afsus, hissiy reaksiya','diskurs','Unlini cho‘zib yozish hissiy kuchaytirish bo‘lishi mumkin.'),
 ('catka/catga',['catka','catga','chatka'],'chatga','grafik_variant','Bu korpusda chatga kirish bilan keladi; avtomatik o‘yin katkasi emas.'),
 ('go',['go'],'kel/bor/boshlaylik mazmunidagi chaqiriq','ozlashma','Go catka — chatga kirishga chaqirish; inglizcha umumiy internet birligi.'),
 ('da',['da','да'],'ha; rozilik','ruscha_birlik','Ruscha to‘liq gap yoki o‘zbekcha aralash javobda; hammasi o‘zlashma emas.'),
 ('ok',['ok'],'xo‘p, qabul qildim','internet_birligi','Ruscha va inglizcha internet yozuvida ham umumiy.'),
 ('uje',['uje','уже'],'allaqachon, endi bo‘lib bo‘lgan','ruscha_birlik','Kontekstga qarab endi/allaqachon; o‘zbekcha gapga kiritilishi kuzatiladi.'),
 ('atak',['atak'],'a tak; aslida/boshqa jihatdan/esa','ruscha_birlik','Ruscha diskurs bo‘lagi; bir xil tarjima barcha gapga mos emas.'),
 ('norm',['norm','normalniy','narmalni'],'yaxshi, odatdagidek, normal','ruscha_birlik','Hol-ahvol javobida qisqa baho.'),
 ('paka/poka',['paka','poka','пока'],'xayr yoki hozircha','ruscha_birlik','Paka tinc — hozircha tinch; har uchrashuv xayrlashuv emas.'),
 ('spat',['spat','спать'],'uxlash, uxlashga ketish','ruscha_birlik','Yakka infinitiv javobi; avtomatik o‘zbekcha to‘liq tuslanish emas.'),
 ('davay',['davay','davaytiy','давай'],'kel, qani, boshlaylik yoki xayrlashuv chaqirig‘i','ruscha_birlik','Juda kam uchrashuv; ma’no kontekstdan.'),
 ('pozna',['pozna'],'kech','ruscha_birlik','Yagona kuzatuv; yuqori chastotali deb ko‘rsatilmaydi.'),
 ('davno',['davno'],'ancha oldin, anchadan beri','ruscha_birlik','Ruscha ravish; hududga mutlaq xos emas.'),
 ('seryoz/seryozniy',['seryoz','seryozni','seryozniy','seryozna','serozni','serezno'],'jiddiy/rostdanmi/jiddiy aytyapman','slang_yoki_ruscha_birlik','Ko‘p seryoz? xabari qayta so‘rash; faqat maqomga oid sifat emas.'),
 ('vapshe oilasi',['vapshe','vapwe','vapshm','vapwem'],'umuman; kuchaytirish; ayrim yozuvda v obshchem bilan yaqinlashish','slang_yoki_ruscha_birlik','vapshm/vapwem va вообще/в общем aralashuvi: bitta qat’iy gloss emas.'),
 ('chotki oilasi',['chotki','cotki','chotqi','cotkiy','cotk'],'yaxshi, zo‘r; hol-ahvolga ijobiy javob','slang','Chotki qisqa javob ham bo‘lib ishlatilgan.'),
 ('malades',['malades','maladec','молодец'],'barakalla, qoyil','slang','Oddiy maqtov; Moskva/Rossiya yoki boshqa joylarda ham bor.'),
 ('karoc oilasi',['karoc','karociy','karochi'],'qisqasi, gapni jamlash/o‘tkazish','slang','Ruscha koroche qisqarishi; noyob Toshkent dalili emas.'),
 ('brat oilasi',['brat','брат','bratka','bratik'],'birodar/oshna deb yaqin murojaat','slang_murojaat','Ruscha literal aka-uka ma’nosi ham bo‘lishi mumkin; har mos xabar bitta ma’noda emas.'),
 ('bratan',['bratan'],'yaqin murojaat','slang_murojaat','Bitta yozuv; qo‘shiq/parodiya tusidagi gap. Kundalik yuqori chastota tasdiqlanmagan.'),
 ('bratiwkayu',['bratiwkayu'],'bratishka asosidagi yaqinlikka oid shakl','slang_murojaat','Bitta misol, gap juda qisqa; aniq munosabat va ohang taxminiy.'),
 ('rodnaya',['родная'],'qadrdonim mazmunidagi ruscha ayol jinsli murojaat','ruscha_murojaat','Rodnoy bilan aynan bir shakl emas; bu grammatik shakl ishtirokchining shaxsiy profilini aniqlamaydi.'),
 ('kotta bola',['kotta bola'],'katta bo‘lgan bola; hazil/tabrikdagi murojaat','murojaat','Tug‘ilgan kun konteksti bor; jinoyat maqomi yoki rahbarlik ma’nosi tasdiqlanmadi.'),
 ('dvijeniya',['dvijeniya'],'harakat/faollik mazmunidagi ruscha birlik','slang_yoki_ruscha_birlik','Bir so‘zli yagona misol. Davra tashkil qilish ma’nosiga yetarli kontekst yo‘q.'),
 ('sokmastan',['sokmastan'],'so‘kmasdan; so‘kinishni to‘xtatish','diskurs','Pizdes javobidan keyingi haqiqiy reply; qo‘pol so‘zlarning mavjudligi hamma ularni xohlaydi degani emas.'),
 ('pizdes/pzds',['pizdes','pzds'],'qo‘pol hissiy kuchaytirish; keskin holat','qopol','Barcha mos xabarlar konteksti aynan bir xil emas; yangi haqoratli gaplar tuzilmaydi.'),
 ('blin',['blin'],'yumshoqroq ruscha hissiy undov','qopolroq_undov','Kam misol; asosiy persona har javobda ishlatishi shart emas.'),
 ('zb',['zb'],'qo‘pol bezor bo‘lish/jonga tegish qisqartmasi','qopol','Ikki misol; vaziyat va oluvchi munosabati hisobga olinadi.'),
 ('radnoy',['radnoy'],'qadrdonim/yaqinim deb norasmiy murojaat','slang_murojaat','Lotincha radnoy haqiqiy chatda bor. Bir xabar; umumiy chastotaga dalil emas.'),
 ('adushi oilasi',['adushi','aduwi','aduwiy'],'chin dildan, samimiy, bemalol jon-dildan','slang','Soxta bo‘lmasin aduwi bosed kabi kontekstlar bor; har bir yozuvning ma’nosi gap bilan.'),
 ('ot dushi oilasi',['ot dushi','ot dushu','от души','от душы'],'chin dildan; ayrim misolda mashhur takror ibora','slang','Meme va oddiy suhbatdagi samimiylik vazifasi alohida.'),
 ('kidala',['kidala'],'ruscha aldovchi/va’dasiga turmaydigan odam atamasi','slang','Ikki qisqa misol. Gap hazilmi/jiddiy ayblovmi — aniq emas; hech kim haqida real ayblov chiqarilmaydi.'),
 ('bez raznici',['bez raznici'],'farqi yo‘q','ruscha_birikma','Gap tarkibida ham, yakka javobda ham bor; bazar yo‘q bilan aynan teng emas.'),
 ('bomba',['bomba'],'juda zo‘r/faol/kuchli taassurotli degan ko‘chma baho','slang','Chat/davra/tadbirni maqtash misollari; asl portlovchi buyum ma’nosi emas.'),
 ('kruto',['круто'],'zo‘r','ruscha_birlik','Ruscha javoblarda bor; krutoy sifatining mahalliy chastotasi emas.'),
 ('blyat oilasi',['blyat','бля','блять','блят'],'qo‘pol hissiy undov','qopol','Bla alohida noaniq qisqartma bo‘lgani uchun bu qidiruvga avtomatik kiritilmagan.'),
 ('prosta',['prosta','просто'],'shunchaki/oddiygina; izoh va ta’kid','ruscha_birlik','O‘zbekcha aralash gaplarda ham bor; har birida bitta tarjima majburiy emas.'),
 ('po faktu',['по факту'],'fakt bo‘yicha/amaldagi holat bo‘yicha','ruscha_birikma','Bir so‘z-birikmali yozuv; ko‘p uchraydigan deb bo‘lmaydi.'),
 ('tema',['tema','тема'],'mavzu, gap ketayotgan narsa','slang_yoki_ruscha_birlik','PUBG tema qilmang va mening temam kabi turli kontekst; noqonuniy ish ma’nosi yuklanmaydi.'),
 ('prikol',['prikol','прикол'],'hazil, qiziq yoki g‘alati holat','slang_yoki_ruscha_birlik','Hazil va masxara ma’nosi gapdagi vaziyatga qarab.'),
 ('realni',['realni'],'haqiqiy/jiddiy mazmunidagi ruscha sifat varianti','slang_yoki_ruscha_birlik','Bir misol; alohida nufuz yoki ishonchlilik ma’nosiga dalil emas.'),
 ('top',['top','топ'],'yuqori baho, zo‘r','internet_birligi','Ruscha maqtov misollari bor. Lotincha top o‘zbekcha topmoq bo‘lishi ham mumkin; qidiruv soni faqat maqtov chastotasi emas. Top Players bot jadvallari chiqarilgan.')]

MANUAL={
 'qalesla':[1367,5885],'qales':[1737,1738], 'qvosan':[2703,3342],
 'qvos':[287], 'qivotti/qvoti':[389,7743], 'kevoman':[394], 'ketvoman':[4499,8326],
 'etvoman':[667], 'dvoman':[685,2113], 'bomi':[509,1223], 'keremas':[1341,2614],
 'oka':[3975], 'catka/catga':[38,540], 'go':[2115,3727],
 'chotki oilasi':[5060,9195,20551], 'malades':[15559,19746],
 'vapshe oilasi':[2601,17354,28540], 'brat oilasi':[4939,20456],
 'bratan':[24075], 'bratiwkayu':[5994], 'rodnaya':[27514,27577],
 'kotta bola':[271,21122], 'dvijeniya':[8863], 'sokmastan':[20456],
 'pizdes/pzds':[20454,28540], 'zb':[3953,25311], 'seryoz/seryozniy':[667,1109,1225],
 'radnoy':[47], 'adushi oilasi':[15045,20192], 'ot dushi oilasi':[3667,18882],
 'kidala':[22427,26992], 'bez raznici':[5093,7743], 'bomba':[5155,23418],
 'kruto':[5782,26591], 'blyat oilasi':[4340,12533],
 'prosta':[2203,9314,15237], 'po faktu':[22541], 'tema':[3640,20240,28137],
 'prikol':[12111,14762,14945], 'realni':[17446], 'top':[26096,26780,27445]}

def pat(aliases):return r'(?<!\w)(?:'+ '|'.join(re.escape(a.normalize(x)) for x in aliases)+r')(?!\w)'

cards=[]
for lemma,aliases,meaning,kind,note in families:
    pattern=pat(aliases);stats=a.hit_stats(pattern)
    assert stats['matching_messages']>0,(lemma,aliases)
    available=[a.BY_ID[i] for i in stats['matching_message_ids']]
    ids=MANUAL.get(lemma,[])
    if not ids:
        # Ilk ikki turli muallifdan qisqa, odam ismiga bog‘lanmaganroq misollar.
        chosen=[];authors=set()
        for m in sorted(available,key=lambda x:(len(x['text'])>100,len(x['text'])<5,x['message_id'])):
            if any(z in m['text'].casefold() for z in ['aziz','malika','botr','moxi','nazli','mali ','huy','sik','nahuy','yiban','suka','gandon']):continue
            if m['author_code'] in authors:continue
            chosen.append(m['message_id']);authors.add(m['author_code'])
            if len(chosen)==2:break
        ids=chosen or [available[0]['message_id']]
    for i in ids:assert re.search(pattern,a.BY_ID[i]['normalized']),(lemma,i)
    forms={}
    for alias in aliases:
        hits=[m for m in available if re.search(pat([alias]),m['normalized'])]
        if hits:forms[alias]=len(hits)
    cards.append({'id':'SL2-'+str(len(cards)+1).zfill(3),'lemma':lemma,
      'meaning_uz':meaning,'type':kind,'notes':note,'observed_query_forms':forms,
      'corpus_scope':'Foydalanuvchi yuklagan bitta chat; matnlar 2021–2023, asosan 2021.',
      'query_pattern':pattern,'match_stats':stats,
      'evidence':[a.evidence(i) for i in ids],
      'observed_in_uploaded_export':True,'manual_meaning_review_required_beyond_selected_examples':True,
      'independent_external_confirmation':False,'exclusive_to_tashkent_verified':False,
      'current_2026_usage_verified':False,'audio_verified':False})
a.save('SLANG_VA_YOZUV_KARTALARI.json',cards)
with (ROOT/'LUGAT_JADVAL.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','lemma','meaning','type','messages','authors','example_ids','notes']);w.writeheader()
    for c in cards:w.writerow({'id':c['id'],'lemma':c['lemma'],'meaning':c['meaning_uz'],'type':c['type'],
      'messages':c['match_stats']['matching_messages'],'authors':c['match_stats']['distinct_author_codes'],
      'example_ids':','.join(str(x['message_id']) for x in c['evidence']),'notes':c['notes']})

# So‘ralgan oldingi 11 birlik: literal topilish va kerakli ma’no alohida.
seed_review=[
 ('Bratan',r'\bbratan\b',[24075],'kam_misol_kontekst_cheklangan','Yagona misol qo‘shiq/parodiya tusida; ko‘p ishlatiladi degan xulosa yo‘q.'),
 ('Bratishka',r'\bbratiwkayu\b',[5994],'variant_bor_kam_misol','Bratiwkayu yozuvi bor; adresat va ohang qisqa gapdan to‘liq aniqlanmaydi.'),
 ('Rodnoy',r'\b(?:rodnoy|radnoy)\b|\bродной\b',[47,4126,27577],'latin_variant_bevosita_bor','Radnoy lotincha murojaatda bor. Родной she’r ichida, родная alohida murojaat; aynan bir shakl/ma’no deb birlashtirilmaydi.'),
 ('Kotta bola',r'\bkotta bola\b',[271,21122],'iborasi_bor_ma’nosi_chegaralangan','Tug‘ilgan kun/kattalashish konteksti; nufuzli ko‘cha boshlig‘i ma’nosi tasdiqlanmagan.'),
 ('Otdushi',r'\botdushi\b|\bot dush[ui]\b|от душ[иы]|\b(?:adushi|aduwi|aduwiy)\b',[18882,21221,20192,15045],'variantlar_va_meme_bor','Ot dushi va adushi/aduwi samimiylik oilasi bor; meme sitatalari ham bor. Ularning hammasi oddiy rahmat vazifasida emas.'),
 ('Seryozniy',pat(['seryozniy','seryozni','seryoz','seryozna']),[667,1109,1225],'kop_variantli_bevosita_dalil','Sifat, jiddiy aytish va rostdanmi savoli vazifalari ajratiladi.'),
 ('Tupik',r'\btupik\b|\bтупик\b',[],'ushbu_korpusda_topilmadi','Bu korpusda topilmasligi so‘z Toshkentda umuman yo‘q degani emas.'),
 ('Dvijeniya',r'\bdvijeniya\b|\bдвижени\w*',[8863],'bitta_qisqa_misol','Harakat ma’nosi mumkin; do‘stlar davrasi/reja ma’nosi kontekstdan qat’iy chiqmaydi.'),
 ('Kidat qilmoq',r'\bkidat\w*|\b(?:kidala|kidayu)\b|\b(?:кидать|кидай)\b',[27468,22427,26992],'bogliq_birliklar_bor_maqsadli_ibora_yoq','Кидать misoli videoni yuborish haqida. Kidala atamasi ham bor, lekin aynan kidat qilmoq iborasi kuzatilmadi; uni boshqa fe’l ma’nolari bilan aralashtirmaymiz.'),
 ('Zashshita qilish',r'\bzash\w*|\bзащи\w*',[19286,28579],'bogliq_soz_bor_iborasi_yoq','Bez zashitni va защитник birikmalari; o‘zbekcha yordamchi fe’lli maqsadli ibora kuzatilmadi.'),
 ('Vapshe',pat(['vapshe','vapwe','vapshm','vapwem']),[2601,17354,28540],'bevosita_variantlar_bor','Kuchaytirish/umuman ma’nolari bor; v obshchem bilan grafik aralashuv ham ajratiladi.')]
review=[]
for form,pattern,ids,status,note in seed_review:
    review.append({'form':form,'status':status,'notes':note,'query_pattern':pattern,
      'literal_or_related_match_stats':a.hit_stats(pattern),'context_evidence':[a.evidence(i) for i in ids],
      'requested_slang_sense_confirmed_globally':False,'independent_external_confirmation':False})
a.save('OLDINGI_11_SOZ_TEKSHIRUVI.json',review)

pair_cases=[
 (1738,'hol_ahvolni_qaytarish','Yaxshi deb javob berib, savolni o‘ziga qaytaradi.'),
 (4939,'rozilik_va_murojaat','Bopti brat — kelishga rozilik, yaqin murojaat.'),
 (5060,'hol_ahvolga_baho','Cotki oziladaci — ijobiy javob va sizlarda-chi savoli.'),
 (9195,'qisqa_baho','Chotki hol-ahvolga yakka ijobiy javob bo‘lib kelgan.'),
 (20551,'qisqa_baho','Cotki — qalaysan savoliga ijobiy javob.'),
 (20658,'suhbatni_davom_ettirish','Cotk ma gapla — javobdan keyin davrani davom ettirish.'),
 (20456,'sokin_nutq_talabi','Bratka sokmastan — oldingi so‘kinishga e’tiroz.'),
 (19746,'maqtov','Maladec — qisqa javobga maqtov reaksiyasi.'),
 (20713,'maqtov_va_qiyos','Boshqaning qilgan ishiga qoyil qolib, o‘z odati bilan qiyoslaydi.'),
 (27577,'minnatdorlik_murojaat','Спасибо родная — ruscha iliq minnatdorlik.'),
 (3975,'hurmatli_qabul','Hop oka — chatga kirish taklifini qabul qilish.'),
 (3732,'salom_va_taklif','Salomga alik, nima qilyapsan savoli va chatga kirishga taklif bir gapda.'),
 (3782,'joylashuvga_javob','Shuttaman — qayerdasan savoliga javob; manba adresati ismga oid bo‘lsa ko‘rsatishda ajratiladi.'),
 (3342,'faoliyat_savoli','Nmala qvosan — hozircha tinch degan javobdan keyingi savol.'),
 (2703,'faoliyat_savoli','Nma qvosan — suhbatdosh keyinroq kirishini aytgach nima qilayotganini so‘rash.'),
 (8863,'qisqa_ruscha_javob','Dvijeniya — nman? ga bir so‘zli javob; tushib qolgan referent bor.'),
 (1109,'jiddiy_savol','Btta sovol sanga seryozni — jiddiylikni oldindan ta’kidlash.'),
 (15559,'maqtov','Gap yo, qoyil va malades birga maqtov vazifasida keladi.')]
pairs=[]
for child_id,kind,analysis in pair_cases:
    m=a.BY_ID[child_id];parent=m['reply_to_message_id']
    assert parent in a.BY_ID,(child_id,parent)
    pairs.append({'id':'SN-'+str(len(pairs)+1).zfill(2),'function':kind,'analysis_uz':analysis,
      'parent':a.evidence(parent),'reply':a.evidence(child_id),
      'explicit_reply_link':True,'creative_reconstruction':False})
a.save('HAQIQIY_SUHBAT_JUFTLARI.json',pairs)

# Alohida so‘zdan tashqari yozishma usuli.
patterns=[
 ('Qisqa javob va savolni qaytarish','Bir-ikki so‘zli javob, keyin o‘zingiz-chi/qalay. Uzun monolog shart emas.',[1737,1738,5060]),
 ('Shaxsga qarab davom zamoni','qvosan, qvoman, qivotti va kevoman kabi shakllar bir xil shaxs emas.',[2703,394,389]),
 ('Hurmat yo‘qolmaydi','Hop oka, oziladaci va sz kabi shakllar norasmiy nutqda ham bor.',[3975,5060]),
 ('Grafik w/c','yaxw, wunaqa; catka va cqb kabi yozuvlar audio emas, yozishma odati sifatida olinadi.',[1738,38,317]),
 ('Unli tashlash','nma, kr, bn, db kabi qisqartmalar o‘qilishni kamaytirishi mumkin; botga me’yor bilan.',[38,287]),
 ('Ruscha birlik va til almashishi','Uje bilan o‘zbekcha gap, butun ruscha gap va lotin-kirill aralash yozuv turli hodisalar.',[9170,27577,17354]),
 ('Seryoz savol ham bo‘ladi','Seryoz? qisqa hayrat yoki qayta aniqlashtirish; faqat jiddiy odam sifatlash emas.',[209,667,1225]),
 ('Undov va emoji','Takrorlangan harf/emoji suhbat tusini berishi mumkin. So‘kinish yoki kulgi har vaziyatga majburiy emas.',[4340,20456]),
 ('Chatga chaqirish','Kr catka/go chat — chat/ovozli davraga kirishga chaqiriq. Catka so‘zi o‘yin deb avtomatik talqin qilinmaydi.',[38,540,2115]),
 ('Sheva va internet qisqartmasi','Man/san, -vo, -la bilan birga bn/kr/nma bor. Bu qatlamlarni alohida saqlash kerak.',[258,1738,38])]
a.save('YOZISHMA_USULLARI.json',[{'id':'YU-'+str(i).zfill(2),'title':title,'analysis_uz':text,
 'evidence':[a.evidence(k) for k in ids],'audio_verified':False,'tashkent_exclusive':False}
 for i,(title,text,ids) in enumerate(patterns,1)])

counts={'observed_cards':len(cards),'card_types':dict(__import__('collections').Counter(c['type'] for c in cards)),
 'seed_words_reviewed':len(review),'explicit_reply_pairs':len(pairs),'writing_patterns':len(patterns),
 'selected_quote_refs':sum(len(c['evidence']) for c in cards)+sum(len(c['context_evidence']) for c in review)+2*len(pairs)+sum(len(ids) for _,_,ids in patterns),
 'selected_unique_message_ids':len({e['message_id'] for c in cards for e in c['evidence']} | {e['message_id'] for c in review for e in c['context_evidence']} | {c['parent']['message_id'] for c in pairs} | {c['reply']['message_id'] for c in pairs} | {k for _,_,ids in patterns for k in ids}),
 'new_external_sources_read':0,'participant_gender_age_location_verified':False}
a.save('HISOBOT_STATISTIKASI.json',counts)
print(json.dumps(counts,ensure_ascii=False,indent=2))
