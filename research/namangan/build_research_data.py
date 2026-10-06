import json, hashlib, re
from pathlib import Path
import fitz

ROOT = Path('/workspace/research/namangan')
sources = json.loads((ROOT/'download_manifest.json').read_text())
pages = {s['id']:(ROOT/(s['id']+('_ocr' if s['id']=='N8' else '')+'.txt')).read_text().split('\f')[:s['pages']] for s in sources}
def save(name, value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def common():
    return dict(exclusive_to_region=None,audio_verified=False,independent_modern_usage_verified=False,model_training_performed=False)
def ref(s,p,a,visual=False,original=None):
    t=pages[s][p-1]; assert a in t,(s,p,a)
    n=t.index(a)
    printed={'N1':p,'N2':p-1,'N3':p+1139,'N4':p+40,'N5':p+74,'N6':p+100,'N7':p+636}.get(s)
    if s=='N8': printed={15:[26,27],16:[28,29],80:[156,157],81:[158,159],82:[160,161],83:[162,163]}.get(p)
    return dict(source=s,pdf_page=p,printed_page=printed,anchor_extracted=a,
                evidence_extracted=t[max(0,n-90):n+len(a)+330],
                extraction='avvalgi aynan bir xil PDF nusxasidan OCR' if s=='N8' else 'PDF matn qatlami',
                visual_checked=visual,visual_transcription=original)

bib=[
 ('2022-yilgi II Respublika konferensiyasi materiallari','O‘zbek shevalari tadqiqotlari: amaliyot, metodologiya va yangicha yondashuv',2022,'tahrir: Sh. Sirojiddinov; Donishmand ziyosi, Toshkent','to‘plam'),
 ('Samixon Ashirboyev','O‘zbek dialektologiyasi',2016,'Navro‘z, Toshkent','darslik'),
 ('Qosimova Shodiya Ulug‘bek qizi','O‘zbek dialektologiyasida Namangan shevasining tutgan o‘rni',2025,'Qo‘qon DPI. Ilmiy xabarlar, 1-son; 1140–1148','umumlashtiruvchi maqola'),
 ('Ravshanova Madina Zafarjon qizi','Navkent qishlog‘i shevasiga oid ayrim dialektal so‘zlar',2025,'International Journal of Science and Technology, 02(08); DOI 10.70728/tech.v2.i08.015','mahalliy lug‘at maqolasi'),
 ('Solijonova Behruza Botirjon qizi','Namangan viloyati va Xorazm viloyati shevalari o‘rtasidagi sotsiolingvistik tahlili',2025,'Ilmiy tadqiqotlar va ularning yechimlari jurnali, 7(02); 75–78','qiyosiy maqola'),
 ('Asqaraliyeva Dilshoda Xojiakbar qizi; ilmiy rahbar Qozoqova Nozima Abdulboqiyevna','Namangan shahar shevasining kelib chiqishi va o‘ziga xos xususiyatlari',None,'Interpretation and researches, 1(4/50); 101–103','mahalliy maqola'),
 ('Gulsanam Shokirova (Xolmirzayeva)','Uychi shevasi leksikasidan',2026,'2026-yil 23-may konferensiyasi; 640–642; DOI 10.52773/tsuull.conf.2026.23.05/KZFO4471','konferensiya maqolasi; muqova va mundarija bilan parcha'),
 ('T.J. Enazarov, V.A. Karimjonova, M.S. Enazarova, Sh.S. Mahmadiyev, K.G‘. Rixsiyeva','O‘zbek shevashunosligi',2012,'Universitet, Toshkent','skanerlangan qo‘llanma')
]
for s,b in zip(sources,bib):
    s.update(author=b[0],title=b[1],year=b[2],publication=b[3],genre=b[4],external_instructions_followed=False,references_online_verified=False)
    dup=[]
    for region in ['surxondaryo','qashqadaryo','samarqand','buxoro','jizzax','andijon','fargona']:
        manifest=ROOT.parent/region/'download_manifest.json'
        if manifest.exists():
            for old in json.loads(manifest.read_text()):
                if old.get('sha256')==s['sha256']: dup.append(dict(region=region,source=old.get('id'),sha256_verified=True))
    s['duplicates']=dup
sources[0]['articles_read']=[dict(author='Ibrohim Darvishov',title='O‘zbek tilshunosligida Namangan shevalarining o‘rganilishi',pdf_pages=[37,38,39,40]),dict(author='Usmonov Musurmon Mamirali o‘g‘li',title='Mingbuloq shevasining o‘ziga xos leksik xususiyatlari',pdf_pages=list(range(95,101))),dict(author='Tojiboyev Botir Raximjonovich',title='“O‘zbek tilining izohli lug‘ati”ni yanada boyitish yo‘lidan',pdf_pages=list(range(196,200)))]
sources[6]['article_pdf_pages']=[4,5,6]
sources[7]['ocr_provenance']=dict(reused_from='/workspace/research/andijon/A6_ocr.txt',leading_blank_pdf_page_preserved=True,trailing_form_feed_removed=True,visual_alignment_checked_pdf_pages=[15,16,80,81,82,83])
save('MANBALAR.json',dict(uploaded_sources=sources,note='Takroriy nusxa va bir asardan qayta iqtibos mustaqil yangi kuzatuv hisoblanmaydi.'))

lex=[]
def word(form,meaning,area,s,p,anchor=None,note='',status='manbada_qayd_etilgan',visual=False,table=None):
    row=dict(id=f'NL{len(lex)+1:03}',form_source=form,meaning_uz=meaning,area=area,notes=note,
             evidence_status=status,register='neytral/maishiy; mahalliy qo‘llanish alohida tekshiriladi',table=table,
             refs=[ref(s,p,anchor or form,visual)],**common())
    lex.append(row); return row

# Table cells are paired after visual inspection, rather than zipping the interleaved page text.
tables={
 1:[('bobo','āpāddä / ätätä / kata ata'),('buvi','äčä / enä / ännä'),('ota','dïdä / dedä'),('ona','Äbä'),('tog‘a','kättä dedä'),('tog‘aning va amakining ayoli','kättä äbä'),('singil','üka'),('xolavachcha','Jiyan'),('turmush o‘rtoq','Bülä'),('chaqaloq','čïčï'),('shafyor','Šāpïr'),('militsiya','Mïlïsä')],
 2:[('beshlik','pänšäxï'),('mantiqosqon tovog‘i','list'),('tahorat choynak','ābdästä'),('xontaxta','xān'),('so‘ri','krävät'),('non yopadigan','räpïda'),('yakando‘z','körpäčä'),('cho‘ntak','chönta'),('ostona','päštäŋ'),('zinapoya','pïlpājä'),('arava','tāštkï'),('jom','lägänčä'),('banka','šišä'),('chelak','Päqïr'),('shag‘am','šäm'),('tuz idish','tüzdiš'),('bolish, yostiq','Jāstïy'),('sholcha','Äläčä'),('shisha','Ïššä'),('piyola','pe:lä'),('kosa','Čïnï'),('scho‘chik','učöčïk'),('sumka','päpkä'),('tarnov','tännāv'),('ko‘ylak','köjnäj'),('telefon','tilpān'),('moshina','māšnä'),('likopcha','tälinkä'),('soat','sāhat'),('devor','devāl'),('tufli','töplï'),('finjon','čashka'),('oynak','ajnäk'),('dastro‘mol','römālčä'),('sochiq','čāčïq'),('qo‘lqop','peräčtka'),('tarozi','tārāðï'),('televizor','tïlïðör'),('quluf','qulf'),('qisqich (zagolka)','ðakālka'),('koptok','töp'),('qo‘g‘irchoq','qog‘iččaq'),('ro‘mol','löngï'),('soya','kölänkä'),('ustki kiyim','engïl'),('krant','krän'),('g‘isht','g‘ïš'),('nimcha','kämðil'),('ko‘ylak','köjnä:'),('tomsuvoq','lāysuvāq')],
 3:[('boshim','bašïm'),('tirnoq','tïnnā:'),('yalangoyoq','yālāntäjā:y'),('bosh','Källä'),('yelka','üçäm'),('burnim','münnïm / bünnïm'),('tirsak','čekänä:'),('boshning chakkasi','Čöqqï'),('soch','Čāč'),('eng kichkina barmoq','jimjilāq')],
 4:[('buzoq','böðä:'),('qo‘zichoq','bäbäčāq'),('mushuk','mïšak'),('kaltakesak','kälpïstä'),('chumoli','čïmälïq'),('chayon','gäðändä'),('kabutar','Käptär'),('musicha','mükïčä'),('qo‘y tezagi','čalma'),('mol tezagi','täppï')],
 5:[('lag‘mon','makran'),('ayron','čölāp'),('kartoshka','kätïškö'),('pomidor','pätïnǯān'),('sarimsoq piyoz','čisnāk'),('go‘sht','Göš'),('shaftoli','šäptälï'),('pechenye','pečennïk'),('sabzi','Sävðï'),('tuzqand','āqqänd'),('suzma','syzma'),('palov','Āš'),('xonim','örämä manti'),('garmdori','atām'),('rayxon','rejxān'),('bulg‘or qalampiri','bālgār')],
 6:[('hovli','havli'),('tovuqxona','kätäk'),('qo‘yxona','qörä'),('uy','ö:j'),('qabriston','däšt'),('hovlining oxirgi qismi','etäk'),('hovlining orqa tomonidagi yer','Häjät'),('padval','tölä / jertölä'),('ayvon','Rām'),('bozor','Güðär'),('molxona','āyïlxānä'),('ichkarixona','gi öj')],
 7:[('xunuk','xünö'),('ozg‘in','ärïq'),('mast','älkäš')],
 8:[('borishim kerak','berïšïm kerä:'),('gaplashmoq','gürüŋläšmāq'),('qo‘rqaman','qöqämän'),('hammomga bormoq','kïnnïgänï bārmāq')],
 9:[('mana shu yerda','mäšajdä'),('shu yerda','šejdä'),('uyoqqa ketdi','äqäkettï'),('mana bu yerda','mänïjdä'),('buyoqqa qara','bäqqärä'),('buyoqqa kel','bäqäke:'),('mana bu yerga kel','mänïjgä ke:'),('shu yerdaman','šettämän'),('narigi yoqqa ketdi','närïrāqqä ketdï'),('qayerdasan','qättäsän')]
}
assert sum(map(len,tables.values()))==127
nav_notes={
 'turmush o‘rtoq':'Bülä ma’nosi nikoh va qarindoshlik kontekstida qayta tekshiriladi; boshqa hudud ma’nosi ko‘chirilmaydi.',
 'tog‘a':'Shahar maqolasidagi kättä dada=otaning akasi bilan ma’no farqi bor.',
 'singil':'Manbada ayol qarindoshga tegishli; uka=erkak qarindosh deb avtomatik almashtirilmaydi.',
 'xolavachcha':'Adabiy jiyan bilan qarindoshlik darajasi farq qiladi; faqat jadvaldagi ta’rif.',
 'arava':'tāštkï shakli va predmet turi mahalliy tasdiq talab qiladi.',
 'lag‘mon':'makran taom yoki mahsulot nomi ekanini aniqlash zarur; lag‘mon va makaron retsepti tenglashtirilmaydi.',
 'pomidor':'pätïnǯān predmetga mosligini mahalliy dalil bilan tekshirish zarur.',
 'tuzqand':'Manbadagi sarlavha saqlandi; novvot deb qo‘shimcha ta’rif kiritilmadi.',
 'garmdori':'atām ma’nosi va yozuvi mustaqil mahalliy tasdiqlanmagan.',
 'ayvon':'Rām qaysi qurilma/qismni bildirishini tekshirish kerak.',
 'bozor':'Güðär=bozor, guzar yoki mahalla markazi munosabati kontekstda tekshiriladi.',
 'ichkarixona':'gi öj shaklining boshlanishi va o‘qilishi tekshiriladi; tushib qolgan tovush taxminan tiklanmadi.',
 'non yopadigan':'Adabiy ustunda predmet nomi to‘liq emas; non emas, non yopishda ishlatiladigan asbob konteksti.',
 'scho‘chik':'Adabiy ustun shakli izohlanmagan; hisoblagich deb qat’iy ta’rif kiritilmadi.',
 'mast':'älkäš shaxsga nisbatan baholovchi/haqoratli tusga ega bo‘lishi mumkin; betaraf holat bilan erkin almashtirilmaydi.',
 'qo‘y tezagi':'Hayvonlar jadvalida bo‘lsa ham ma’no tezak; hayvon nomi emas.',
 'mol tezagi':'Hayvonlar jadvalida bo‘lsa ham ma’no tezak; hayvon nomi emas.',
 'yalangoyoq':'Tana a’zolari jadvalidagi holat bildiruvchi birlik; tana a’zosi deb tasniflanmaydi.',
 'xonim':'Taom nomi; barcha manti turiga yoyilmaydi.',
}
nav=[]
for no,pairs in tables.items():
    for meaning,form in pairs:
        anchor=form.split(' / ')[0]
        if meaning=='hammomga bormoq': anchor='kïnnïgänï'
        if meaning=='narigi yoqqa ketdi': anchor='närïrāqqä'
        if meaning=='g‘isht': anchor='gʻïš'
        row=word(form,meaning,'Namangan / Yangiqo‘rg‘on / Navkent','N4',1 if no==1 else 2,anchor,
                 nav_notes.get(meaning,''),'tekshirish_talab' if meaning in ['turmush o‘rtoq','arava','lag‘mon','pomidor','garmdori','ayvon','bozor','ichkarixona','scho‘chik'] else 'manbada_qayd_etilgan',True,no)
        row['unit_type']='yo‘nalish/savol/harakat ifodasi' if no in [8,9] else 'lug‘at juftligi'
        nav.append(row)
save('NAVKENT_JADVALLARI.json',nav)
raw_tables=[]
with fitz.open(sources[3]['path']) as d:
    for p in [1,2]:
        for i,t in enumerate(d[p-1].find_tables().tables): raw_tables.append(dict(pdf_page=p,index_on_page=i,cells_extracted=t.extract()))
save('NAVKENT_JADVALLARI_ASL_AJRATMA.json',raw_tables)

ming=[
 ('döγăča','kosa shaklidagi ichi chuqur tovoq','Rakasoviskiy (manbadagi yozuv)',96,'Rakasoviskiy','99-betda Dehqonobod ham qayd etilgan; ikki nomning tarixiy tengligi tasdiqlanmagan.'),
 ('bărmăvüč / bărmăgüč','borishga kelishib, keyin bormaydigan bo‘lib qolmoq','Mingbuloq',96,'Bormovuch','Kelishuvni bekor qilish vaziyati; oddiy bo‘lishsizlik bilan barcha kontekstda teng emas.'),
 ('ăvxir','chorvaga o‘t/hashak solinadigan joy','Mingbuloq',96,'Ovxir','99-betdagi ăγil molxona/o‘t solish joyi ma’nolari kontekstga bog‘liq.'),
 ('mällä','qatlama turi','Alami; Mingbuloq',96,'Malla','Taom, rang ma’nosi bilan almashtirilmaydi.'),
 ('sürgürünč / sürgürüč','sut va guruchdan pishiriladigan shirguruch','Mingbuloq',96,'Surguruch','Lotin boshso‘z Surguruch/Surgurunch transkripsiya bilan to‘liq mos emas; ikkalasi saqlandi.'),
 ('jϵŋsä','tandirga non yopishda qo‘lni himoyalovchi yengcha','Mingbuloq',96,'Engsa',''),
 ('kättä dädä / ăpädädä / ăppăqdädä','otaning akasi','Alami va maqolada sanalgan Mingbuloq qishloqlari',96,'Katta dada','Otaning ukasi uchun ham ishlatiladi degan dalil yo‘q.'),
 ('ăppăqayä / kättä ayä','katta amakining xotini','Mingbuloq',96,'Oppoqaya',''),
 ('soppi','so‘filar kiyadigan oq do‘ppi','Mingbuloq',97,'So‘ppi','So‘fi odam bilan tenglashtirilmaydi.'),
 ('sălčä / šălčä / dărăškä','gilamdan yupqa, oyoq ostiga solinadigan sholcha','Mingbuloq',97,'Solcha',''),
 ('ǯäps / ǯämäti','qarindosh/urug‘','Gurtepa: ǯäps; Yakkatol: ǯämäti',97,'Japs','100-betdagi aniq qishloq taqsimoti saqlandi; etimologik taxmin mustaqil tekshirilmagan.'),
 ('băsăldä','chamasi, taxminan, ehtimol','Mingbuloq',97,'Bosolda',''),
 ('tindăq / tinnăq','tirnoq','Mingbuloq',97,'Tindoq',''),
 ('čăvdiš / čăvin / ăvdästä','obdasta/chovgun turidagi idishlar','Mingbuloq',97,'Chovdish','Qo‘l yuvish va choy qaynatish vazifalarini farqlash kerak; hamma idish teng emas.'),
 ('dombä / dompä / tepäliq','yer sathidan baland tepalik','Mingbuloq',97,'Do‘mba',''),
 ('kötärmä','chorva boqiladigan/turadigan bino','Qorashahar, Jiydaqishloq, Momoxon, Qirqchek, Yakkatol',97,'Ko‘tarma','99-bet taqsimoti; boshqa hududdagi ko‘tarma ko‘prik ma’nosi ko‘chirilmaydi.'),
 ('băstirmä','chorva saqlanadigan, asosan yozgi bino','Qorashahar, Jiydaqishloq, Momoxon, Qirqchek, Yakkatol',97,'Bostirma','Ochiq/yengil usti yopiq qurilma xususiyati ham bor.'),
 ('lägän','ichi chuqur idish','Mingbuloq qipchoq hududlari',97,'Lagan','98-betda davom etadi; janub/janubi-g‘arbiy hududda sayoz idish ma’nosi.'),
 ('lägän','ichi sayoz idish','Mingbuloq janubi va janubi-g‘arbi',98,'janubi','Bir shaklning ikki hududiy ma’nosi alohida yozuvda.'),
 ('tăjlăq','sirpanadigan joy; sirpanchiq','Mingbuloq',98,'Toyloq','Kichkina toy hayvoni ma’nosidan farq qiladi.'),
 ('ăpä','ona','Mingbuloq',98,'Opa','100-betda opä, aya, ϵnä qishloqlar bo‘yicha beriladi.'),
 ('ariq','ekin uchun uzun uyilgan tuproq; pushta/marza','Alami, Gulbog‘',98,'Ariq','Suv oqadigan o‘zan deb almashtirish mumkin emas.'),
 ('taqläm / ta:läm','taxlam','Mingbuloq y-lovchi: taqläm; j-lovchi: ta:läm',98,'Taqlam','99-betda qishloq kesimida kengroq variantlar sanalgan.'),
 ('täpt / tävt','kaftning ichki qismi','Mingbuloq',98,'Tapt','Taft=issiq ma’nosi bilan teng emas; manbadagi adabiy boshso‘z taft izohi bahsli.'),
 ('qallämä','qatlama','Alami; Mingbuloq',98,'Qallama','t+l→ll regressiv assimilyatsiya; maqoladagi l ni sirg‘aluvchi deyish terminologik xato.'),
 ('hălväjtäl','holvaytar','Rakasovitskiy (manbadagi yozuv)',98,'Holvaytal','99-bet hududiy taqsimotga qarang.'),
 ('älväli','olcha (maqola ta’rifi)','Mingbuloq',99,'Alvali','Peshqo‘rg‘onda olvali boshqa meva sifatida ta’riflangan; butun viloyatga bir ma’no berilmaydi.'),
 ('bărmăvüč / bărmăvöč','bormaydigan','Dovduq, Gurtepa, Ingichka, Terak, Tolliovul, Uzuntepa, Mulkobod, Sho‘rsuv',99,'bărmăvöč','96-betdagi kelishuv vaziyati ham hisobga olinadi.'),
 ('bărmiydigän / bărmiydiγän','bormaydigan','Yangi Gulbog‘, Tegirmon, Momoxon, Qorashahar, Qolg‘andaryo, Jomoshov, Jiydaqishloq, Gulbog‘, Alami',99,'bărmiydigän','Shahar -ut shakllari bilan aralashtirilmaydi.'),
 ('hălvätär','holvaytar','Yangi Gulbog‘, Tegirmon, Momoxon, Qorashahar, Qolg‘andaryo, Jomoshov, Jiydaqishloq, Gulbog‘, Alami',99,'hălvätär',''),
 ('ăγil','molxona','Alami, Gulbog‘ va maqolada sanalgan Mingbuloq qishloqlari',99,'Molxona','Xuddi shu betda oxir bilan o‘t solish joyi sifatida ham sanaladi; ma’no vaziyatda aniqlanadi.'),
 ('opä / aya / ϵnä','ona','Yangi Gulbog‘, Tegirmon, Yakkatol, Momoxon, Qorashahar, Qolg‘andaryo, Jiydaqishloq, Alami',100,'Ona –',''),
 ('ǯojak / ariq / mărzä','pushta, marza, jo‘yak','Alami, Gulbog‘: ariq; Mingbuloq',100,'Pushta','')
]
for f,m,a,p,anchor,n in ming: word(f,m,'Namangan / '+a,'N1',p,anchor,n)
for f,m,p,a,n in [
 ('olvali','pishgan mevasi qizil-qora rangli daraxt/meva; muallif olcha va olxo‘ridan farqlaydi',197,'olvali – olcha','Botda Mingbuloq olcha ekvivalenti bilan qo‘shilmaydi; botanik turi tashqi tasdiqlanmagan.'),
 ('cho‘g‘oloq','makkajo‘xori so‘tasining donsiz o‘zagi',197,'cho‘g‘oloq','Kalit so‘zlarda cho‘g‘aloq, asosiy matnda cho‘g‘oloq; asosiy matn saqlandi.'),
 ('o‘ngar','choponning etak qismi',198,'o‘ngar','Tarixiy she’rda o‘ngur; mahalliy hozirgi shakl bilan tarixiy variant farq qiladi.'),
 ('tirja','o‘qariqdan egatlarga suv taqsimlovchi kichik ariq',198,'tirja','Oddiy barcha ariq bilan teng emas.')]:
    word(f,m,'Namangan / Chortoq / Peshqo‘rg‘on','N1',p,a,n)

for f,m in [('šejde','shu yerda'),('čorqi','osh solinadigan lagan'),('öγȉl','og‘ilxona'),('qoγa','qamish'),('satȉl','temir tovoq/jom')]:
    word(f,m,'Janubi-g‘arbiy Namangan; N3 aniq qishloqni har so‘zga bog‘lamaydi','N3',7,f,'Darveshov 2019 asaridan ikkilamchi iqtibos; monografiyaning o‘zi ushbu bosqichda berilmagan.')
for f,m,a,n in [('čïmälïq','chumoli','CHimaliq',''),('löxrà(k)','chuvalchang',"Lo‘xrak".replace('‘',"'"),'Transkripsiya r ustidagi belgisi matn ajratmasida farqlanishi mumkin.'),('šötï','narvon','Shoti','Norin va Uychi ham sanalgan; faqat shaharga xos emas.'),("Mishig‘ / mыčиý",'mushuk',"Mishig'",'Boshso‘z va aralash alifbodagi transkripsiya mos emas; sh/ch/g talaffuzi mahalliy tasdiq talab qiladi.'),('opodda','bobo','opodda',''),('katta dada','otaning akasi','akasini','Navkent tog‘a ekvivalenti bilan aralashtirilmaydi.')]:
    word(f,m,'Namangan shahar','N6',2,a,n,'tekshirish_talab' if m=='mushuk' else 'manbada_qayd_etilgan',True)
for f,m in [('katta aba','katta amakining xotini'),('acha','buvi'),('aba','ona')]: word(f,m,'Namangan shahar','N6',3,f)
for f,m,p,a,st in [('oka','aka',5,'oka','manbada_qayd_etilgan'),('o‘g‘ul','o‘g‘il',5,'oʻgʻul','manbada_qayd_etilgan'),('yomir','yomg‘ir',5,'yomir','manbada_qayd_etilgan'),('chayla','kichik uy/kulba',6,'chayla','umumiy_so‘z'),('tandirxona','tandir joylashgan xona',6,'tandirxona','umumiy_so‘z'),('tappak','tez/shoshilinch (maqola izohi)',6,'tappak','tekshirish_talab'),('sergap','ko‘p gapiradigan',6,'sergap','umumiy_so‘z'),('g‘o‘r','hali pishmagan meva',6,'gʻoʻr','umumiy_so‘z'),('ariqcha','kichik sug‘orish yo‘li',6,'ariqcha','umumiy_so‘z'),('mashna','mashina',6,'mashna','manbada_qayd_etilgan')]:
    word(f,m,'Namangan / Uychi; ichki qishloq taqsimoti berilmagan','N7',p,a,'Umumiy so‘zlar Uychi uchun eksklyuziv belgi emas. Maqolada respondent, suhbat sanasi va audio yo‘q.',st)
for f,m,area,p,a,raw in [('əpədə','bobo','Toshkent va Namangan / Chortoq',80,'3pada','əpədə'),('ləyorak','chuvalchang','Namangan / Chortoq',80,'tayxorak','ləyorak'),('og‘ur','havoncha','Namangan / Chortoq',80,'havoncha','og‘ur'),('əchqich','kalit','Namangan; aniq aholi punkti berilmagan',80,'achqich','əchqich'),('gindjelek','jingalak','Namangan / Uychi',83,'gindjelek','gindjelek'),('kesh','kalish','Namangan; aniq aholi punkti berilmagan',83,'kesh','kesh'),('e:de','ana u yerda','Namangan / Uycha (manbadagi yozuv)',83,'e:de','e:de')]:
    r=word(f,m,area,'N8',p,a,'OCR o‘qilishi sahifa rasmi bilan tekshirildi; oddiy lotin talaffuz uchun aniq audio o‘rnini bosmaydi.',visual=True)
    r['refs'][0]['visual_transcription']=raw
save('LUGAT.json',lex)

phon=[]
def sound(inp,out,process,area,s,p,a,n='',visual=False,st='manbada_qayd_etilgan'):
    phon.append(dict(id=f'NF{len(phon)+1:03}',literary_form=inp,form_source=out,process=process,area=area,
                     notes=n,evidence_status=st,refs=[ref(s,p,a,visual)],**common()))
for i,o,a in [('mol → molim','māl → mälim','molim'),('sol → solish','sāl → säliš','solish'),('nok → noki','nāk → näki','noki'),('toy → toying','tāj → täjiŋ','toying')]:
    sound(i,o,'umlaut: affiks unlisining asos unlisiga regressiv ta’siri','Namangan tip shevalari','N2',23,a,'Rasmda asl transkripsiya tekshirildi. Asos va affiks shartiga bog‘liq; barcha o/a unlilarini e ga aylantirish qoidasi emas.',True)
for i,o,p,a,proc in [('bo‘libdi','boluptu',22,'болупту','lab garmoniyasi'),('ko‘ribdi','körüptü',22,'кор%пту_','lab garmoniyasi; transkripsiyani vizual qayta tekshirish kerak'),('suyak','süyäg',24,'suyak','k → g jaranglashishi'),('tegmas','te:mas',26,'tegmas','undosh tushishi va ikkilamchi cho‘ziqlik'),('laylak','lā:lā:',26,'laylak','undosh tushishi va ikkilamchi cho‘ziqlik')]:
    sound(i,o,proc,'Namangan; muallif ko‘rsatgan doira','N2',p,a,visual=(p in [22,24,26]))
for i,o,proc,a in [('xaridor','xaddā:','undosh moslashuvi va qisqarish','xaddā:'),('yurdi','yuddi','r+d → dd','yuddi'),('bersa','bessa','r+s → ss','bessa'),('o‘rnim','o‘nnim','r+n → nn','o‘nnim'),('chaqirdi','chaqiddi','r+d → dd','chaqiddi'),('ichsa','issa','ch+s → ss','issa'),('yaqinlashyapti','yaqinleshutti','asos unlisi va davom zamon shakli','yaqinleshutti')]:
    sound(i,o,proc,'Namangan shahar','N3',7,a,'Zamon/shaxsga doir to‘liq gaplar alohida saqlanadi; xaridor gapida keldi/kelűtti teng emas.')
for i,o,proc,a in [('taxlam','taqläm / ta:läm','x→q yoki x tushishi; y/j-lovchi farqi','Taqlam'),('qatlama','qallämä','t+l → ll regressiv assimilyatsiya','Qallama'),('holvaytar','hălväjtäl','oxirgi r → l','Holvaytal'),('taft (boshso‘z bahsli)','täpt / tävt','f→p/v; kaft ma’nosini alohida tekshirish','Tapt')]:
    sound(i,o,proc,'Mingbuloq; N1 qishloq taqsimoti','N1',98,a,'Hodisa tasviri butun viloyatga yoyilmaydi.')
for inp in ['telefon','moshina','devor','tarnov','ko‘ylak','tirnoq','burnim','soch','mushuk','chumoli','shaftoli','go‘sht','qo‘rqaman']:
    for row in nav:
        if row['meaning_uz']==inp:
            sound(inp,row['form_source'],'manbada qayd etilgan fonetik variant; muhit va qoida chegarasi tekshiriladi',row['area'],'N4',row['refs'][0]['pdf_page'],row['refs'][0]['anchor_extracted'],'ð, ï, ä, ā, ö, : belgilari asl holda saqlanadi; chat uchun taxminiy yozuv asl transkripsiyaga teng emas.',True)
for i,o,p in [('aka','oka',5),('o‘g‘il','oʻgʻul',5),('yomg‘ir','yomir',5),('mashina','mashna',6)]: sound(i,o,'muallif sanagan talaffuz varianti','Uychi','N7',p,o)
sound('tuproq','turpoq','metateza','Namangan shahar','N6',3,'Tuproq','Manba buni dissimilatsiya deb ataydi; aslida undoshlar o‘rin almashgan.')
sound('to‘rg‘amoq','to‘rg‘amoq','ikki tomoni bir xil; o‘zgarish chiqarib bo‘lmaydi','Namangan shahar','N6',3,"To'rg'amoq",'Avtomatik tuzatib to‘g‘ramoq deb berilmadi.',st='tekshirish_talab')
sound('jingalak','gindjelek','metateza misoli','Uychi','N8',83,'gindjelek','OCR va sahifa rasmi qiyoslandi.',True)
sound('olma / bobom','ulma / bubom','muallifning o→u da’vosi','Namangan; aniq punkt yo‘q','N5',2,'ulma','Dala kuzatuvi va fonetik muhit berilmagan; umumiy almashtirishga asos bo‘lmaydi.',st='tekshirish_talab')
save('FONETIKA.json',phon)

gram=[]
def grammar(label,meaning,forms,area,s,p,a,n='',status='manbada_qayd_etilgan'):
    gram.append(dict(id=f'NG{len(gram)+1:03}',label=label,meaning_uz=meaning,forms_source=forms,area=area,
                     notes=n,evidence_status=status,refs=[ref(s,p,a)],**common()))
for person,forms,p,a in [
 ('I birlik',['kelűtt(ȉ)ma:','ketűtt(ȉ)ma:','borűtt(ȉ)ma:'],5,'kelűtt(ȉ)ma:'),
 ('II birlik',['kelűssa:','ketűssa:','borűssa:'],5,'kelűssa:'),
 ('III birlik',['kelűttȉ','ketűttȉ','borűttȉ'],5,'kelyapti, ketyapti'),
 ('I ko‘plik',['kelűtt(ȉ)mȉz','ketűtt(ȉ)mȉz','borűtt(ȉ)mȉz'],6,'kelűtt(ȉ)mȉz'),
 ('II ko‘plik',['kelűss(ȉ)z','ketűss(ȉ)z','borűss(ȉ)z'],6,'kelűss(ȉ)z'),
 ('III ko‘plik',['kelűtt(ȉ)la:','borűtt(ȉ)la:'],6,'kelűtt(ȉ)la:')]:
    grammar('Hozirgi davom zamoni / '+person,'kel-/ket-/bor- harakatining hozir davom etishi',forms,'Namangan shahar; Uychi va Chortoqning ayrim hududlari','N3',p,a,'Asl paradigmadagi takror, son va tartib xatosi tuzatilgan dalil sifatida yashirilmaydi. Har fe’l ildizi bo‘yicha ma’no moslanadi; hurmat va ko‘plik kontekstda farqlanadi.')
for person,forms,a in [('I birlik',['qȉlműtt(ȉ)ma:','ajtműtt(ȉ)ma:'],'qȉlműtt(ȉ)ma:'),('II birlik',['qȉlműtt(ȉ)sa:','ajtműtt(ȉ)sa:'],'qȉlműtt(ȉ)sa:'),('III birlik',['qȉlműtt(ȉ)','ajtműtt(ȉ)'],'qȉlműtt(ȉ)'),('III ko‘plik',['ketműtt(ȉ)la:','korműtt(ȉ)la:','kelműtt(ȉ)la:','ešȉtműtt(ȉ)la:','borműtt(ȉ)la:','čıqműtt(ȉ)la:'],'ketműtt(ȉ)la:')]:
    grammar('Hozirgi davom zamoni inkori / '+person,'qil-/ayt- yoki sanalgan harakat hozir davom etmayapti',forms,'Namangan shahar; Uychi va Chortoqning ayrim hududlari','N3',6,a,'Inkordagi m saqlanadi; kelműttȉ ni kelűttȉ bilan tenglashtirmaslik zarur.')
grammar('Bo‘lishsiz III birlikdagi l reduksiyasi','qilmayapti',['qȉlműttȉ','qȉműttȉ'],'Namangan shahar va N3 ko‘rsatgan ayrim hududlar','N3',6,'qȉlműttȉ~qȉműttȉ','Variantni alohida zamon yoki boshqa mustaqil fe’l deb hisoblamaslik kerak.')
grammar('Hozirgi-kelasi zamon inkori va emfatik cho‘ziqlik','bilmayman/bo‘lmaydi; davom zamoni paradigmasidan boshqa shakl',['bi:lmā:(j)mā:','bomā:(j)di'],'Namangan shahar','N2',26,'bilmayman','PDF rasmida transkripsiya tekshirildi; uzoq unli va (j) ixtiyoriy qisqarishi; ASCII yozuv talaffuzni to‘liq bermaydi.')
grammar('Ko‘plik/hurmat shakli -nä','uyinglar, qo‘yinglar shakllari',['ujijnä','qojijnä'],'Namangan tip shevalari','N2',31,'-нэ','PDF rasmida -nä ko‘rildi; manbadagi ega/hurmat/buyruq vazifalarini kontekstsiz aralashtirmaslik kerak.')
grammar('I ko‘plik buyruq-istak','ishlaylik / boraylik',['islajnu','barajnuk'],'Namangan; barajnuk Xo‘jandda ham','N2',41,'islajnu','Ishlaylik misolining Namangan belgisi 42-betga ko‘chgan; ikki sahifa birga o‘qildi.')
gram[-1]['refs'].append(ref('N2',42,'barajnuk'))
grammar('III shaxs buyruq-istak -sun','ko‘rsin / bilsin',['körsun','bilsun'],'Namangan','N2',42,'bilsun','Asl sahifa rasmi ham ko‘rildi; matn qatlamidagi diakritika to‘liq ajralmagan.')
grammar('Qaratqich/tushum shakli','qaratqich va tushum vazifasida -ni va fonetik variantlari',['-ni'],'Toshkent, Namangan, Andijon, Marg‘ilon, Qo‘qon','N8',16,'qaratqich','Umumiy guruh belgisi; Namangan uchungina xos emas. N3 -di/-ti da’vosi Namangan uchun mustaqil kontekst bermaydi.')
grammar('Uychi davom zamoni varianti','tarixiy qo‘llanmada Uychi -vat, Namangan -ut farqi',['Uychi -vat','Namangan -ut'],'qo‘llanma ko‘rsatgan hududlar','N8',16,'Uychi - vat','N3 Uychi ayrim hududlarini -ut bilan beradi. Vaqt, qishloq va variantni aniqlamasdan birini noto‘g‘ri deb o‘chirmaslik kerak.')
grammar('Qo‘sh ko‘plik -larlar da’vosi','kitoblar → kitoblarlar (muallif misoli)',['kitoblarlar'],'Namangan; aniq punkt yo‘q','N5',2,'kitoblarlar','N2 qo‘sh ko‘plikni Qorabuloq/Iqon bulalar/shulalar bilan qayd etgan; bu kitoblarlar Namangan uchun tasdiq emas.','tekshirish_talab')
grammar('Infinitiv/niyat chalkash juftligi','yurmoq va yurmoqchi ma’nosi grammatik jihatdan farq qiladi',['yurmoqchi','yuruvmoq'],'Namangan; aniq punkt yo‘q','N5',2,'yuruvmoq','Niyat qo‘shimchasini infinitivning shevaviy tarjimasi sifatida qo‘llash ma’noni o‘zgartiradi.','tekshirish_talab')
save('GRAMMATIKA.json',gram)

speech=[]
def utterance(original,meaning,area,s,p,a=None,n='',genre='muallif keltirgan nutq misoli',usable=True):
    if a=='mā őnnummi': a='őnnummi'
    speech.append(dict(id=f'NN{len(speech)+1:03}',text_source=original,meaning_uz=meaning,area=area,genre=genre,
                       meaning_preserving_pair=usable,notes=n,refs=[ref(s,p,a or original,s=='N2')],**common()))
for row in nav:
    if row['table'] in [8,9]:
        utterance(row['form_source'],row['meaning_uz'],row['area'],'N4',row['refs'][0]['pdf_page'],row['refs'][0]['anchor_extracted'],row['notes'],'maqoladagi jadval ifodasi; mustaqil yozib olingan dialog emas')
for a,m in [('ТУЗУМЪСЪЗ','Yaxshimisiz? / sog‘lig‘ingiz joyidami?'),('Х,э, ендъ тузумэн','Ha, endi yaxshiman.'),('келуттъмъ','... kelyaptimi? (o‘g‘ildan xat haqidagi gap)'),('Сэломэт болуссун','Salomat bo‘lsin(lar).'),('ъшлэ джудэ коп','Ishlar juda ko‘p.'),('турэйлук','Endi biz turaylik / ketishga ruxsat so‘rash.'),('Хэммэлэръ йэхшъ','Hammalari yaxshi.')]:
    # preserve original casing/spelling from the page, including OCR/text-layer noise.
    t=pages['N2'][92]; match=re.search(re.escape(a),t,re.I)
    if match:
        actual=match.group(); pos=t.rfind('\n',0,match.start()); end=t.find('\n',match.end())
        text=t[max(0,pos+1):end if end!=-1 else len(t)].strip()
        utterance(text,m,'Namangan; kitobda faqat sheva sarlavhasi bor','N2',93,actual,'Bosma dialogning parchasi. Respondent, mahalla, yozib olish sanasi va audio bu yerda ko‘rsatilmagan.','darslikdagi Suhbat; PDF 92 oxiri–94 boshi')
utterance('Хэй... дэрэп кетуссълэйэ, тэбэ, бэшкэ келъйнэ, бомэсэ.','Tez ketayapsizlar-a; boshqa safar kelinglar.','Namangan','N2',94,'бэшкэ келъйнэ','So‘zma-so‘z normallashtirish emas, vaziyat mazmuni.','darslikdagi Suhbat')
utterance('Ovxirga o‘t tashladim.','Chorvaning o‘t/hashak joyiga o‘t tashladim.','Mingbuloq','N1',96,'Ovxirga o‘t tashladim.')
utterance('Tavtingni peshonasiga bos-chi?','Kaftingni peshonasiga bos-chi?','Mingbuloq','N1',98,'Tavtingni peshonasiga')
for o,m,a,n,ok in [('Öka dokonga xaddā: kϵlűtti','Aka, do‘konga xaridor keldi (manbadagi adabiy gap)','Öka dokonga','Keldi o‘tgan zamon, kϵlűtti hozirgi davom. Bu juftlik ma’noni to‘liq saqlamaydi.',False),('Narxini āzzonlatb bessalā','Narxini arzonlatib bersalar.','Narxini āzzonlatb','',True),('mā őnnummi biroplāga berib qojϵdiganlādänmasmä','Men o‘rnimni boshqalarga berib qo‘yadiganlardan emasman.','mā őnnummi','',True),('Čaqiddi soat nϵččiga bolűtti','Chaqirdi soat nechaga bo‘lyapti (manba)','Čaqiddi soat','Gap tuzilishi noaniq; toza dialog namunasi qilib qo‘llanmaydi.',False),('Dedamlar issalar deb sut opkeluttimaan','Dadamlar ichsalar deb sut olib kelyapman.','Dedamlar','Hurmat ko‘pligi; otaning shaxs-son ma’nosi saqlanadi.',True),('Opodda sizga itlar yaqinleshutti','Bobo, sizga itlar yaqinlashyapti.','Opodda','',True)]:
    utterance(o,m,'Namangan shahar','N3',7,a,n,usable=ok)
save('NUTQ_NAMUNALARI.json',speech)
dialogue=[]
for p in [92,93,94]:
    t=pages['N2'][p-1]
    if p==92: t=t[t.index('Namangan shevasi'):]
    if p==94: t=t[:t.index('Kitob tumani Ayronchi')]
    dialogue.append(dict(pdf_page=p,printed_page=p-1,text_extracted=t.strip(),visual_checked=True))
save('NAMANGAN_SUHBAT_ASL.json',dict(source='N2',title='Namangan shevasi — Suhbat',pages=dialogue,
     genre='darslikdagi bosma suhbat; zamonaviy audio yoki mustaqil respondent yozuvi emas',
     notes='Matn qatlamidagi transkripsiya belgilari va ajratish xatolari saqlangan; asl rasm tekshiruv/N2_092.png–N2_094.png. Keyingi Ayronchi matni kiritilmadi.',**common()))

claims=[]
def claim(title,s,p,a,reason,decision='botning avtomatik almashtirish qoidasi uchun ishlatilmaydi'):
    claims.append(dict(id=f'NT{len(claims)+1:03}',claim=title,reason=reason,decision=decision,refs=[ref(s,p,a)],**common()))
for title,s,p,a,reason in [
 ('Namangan viloyati = bitta umlautli sheva','N1',39,'qo‘shilib bo‘lmaydi','Darvishov shahar belgisini barcha viloyatga yoyish tasnifini tanqid qiladi; qipchoq areallari bor.'),
 ('Shahandni qarluq umlautli tipga kiritish','N1',39,'Shahand','Muallif uni y/j-lovchi qipchoq urug‘lari yashaydigan qishloq sifatida munozarali deydi; bir tasnifni yagona haqiqat deb olmaymiz.'),
 ('N3 umlaut misollarining yozuvi','N3',5,'nok ~ näk','N2 rasmida nāk→näki va tāj→täjiŋ; N3 nok~näk, toying~tājȉŋ yozadi. Variant/ko‘chirish xatosi aniqlashtirilishi kerak.'),
 ('N3 paradigmasidagi tartib/takror','N3',5,'ketűttȉsā:','II shaxsda ket/kel tartibi va takror; III shaxsda ikki adabiy fe’lga uch sheva fe’li. Ro‘yxatlar indeks bo‘yicha zip qilinmaydi.'),
 ('O‘tgan zamon va davom zamoni tenglashtirilgan gap','N3',7,'xaddā:','Adabiy keldi va sheva kelűtti zamon jihatdan teng emas.'),
 ('Keloman hozirgi davomning avtomatik ekvivalenti','N3',7,'keloman','Zamon/aspekt va vaziyat tekshirilmagan.'),
 ('Namangan tushumining hammasi -di/-ti','N3',8,'–di,-ti','Aniq Namangan punktidagi kontekstli misol yo‘q; N2 -di/-ti ni Andijon/Marg‘ilon/Qo‘qon bilan bog‘laydi.'),
 ('Namangan vodiyning janubida','N5',2,'janubiy qismida','Geografik xato; viloyat vodiyning shimoliy qismida. Maqolaning umumlashtirishlari ehtiyotkor baholanadi.'),
 ('Yurmoq = yurmoqchi','N5',2,'yurmoqchi','Infinitiv va niyat shakli semantik teng emas.'),
 ('Qish = qishda','N5',2,'qishda','Ot va o‘rin-payt shakli bir xil leksik ekvivalent emas.'),
 ('Kitoblarlar Namangan ko‘pligi','N5',2,'kitoblarlar','Respondent, mahalla va aniq qo‘llanish yo‘q. N2 Qorabuloq/Iqonning qo‘sh ko‘pligi buni tasdiqlamaydi.'),
 ('Xudohafizning barchasi arabcha','N5',3,'Xudohafiz','Xudo komponenti forscha; umumiy ibora Namangan uchun eksklyuziv dalil emas.'),
 ('Shahar aholisi doimo adabiyroq gapiradi','N5',2,'markaziy o‘zbek','Yosh, vaziyat, ta’lim, respondentlar kesimidagi empirik tekshiruv yo‘q. N1/N3 shahar o‘ziga xosligini ko‘rsatadi.'),
 ('Bülä = turmush o‘rtoq','N4',1,'Bülä','Qarindoshlik darajasi va nikoh atamasining ma’nosi mahalliy kontekst bilan tekshiriladi.'),
 ('Pätïnǯān = pomidor','N4',2,'pätïnǯān','Predmet turi mustaqil tasdiqlanmagan; shahar yoki barcha viloyatga yoyilmaydi.'),
 ('Rām = ayvon va Güðär = bozor','N4',2,'Rām','Qurilma qismi va joyning ijtimoiy vazifasi kontekstda aniqlanishi kerak.'),
 ('Mishig‘ transkripsiyasi','N6',2,"Mishig'",'Boshso‘z va mыčиý aralash yozuvi farq qiladi; rasm ko‘rildi, ammo talaffuz audio bilan tasdiqlanmagan.'),
 ('Tuproq→turpoq dissimilatsiya','N6',3,'Tuproq','Undoshlarning o‘rin almashishi metateza; tovush tasnifi tuzatildi, misol saqlandi.'),
 ('To‘rg‘amoq→to‘rg‘amoq','N6',3,"To'rg'amoq",'Ikki tomon bir xil; asl niyat to‘g‘ramoq bo‘lishi mumkin, ammo dalilsiz tiklanmadi.'),
 ('Mehnatni fors-tojik o‘zlashma deyish','N7',6,'mehnat','Etimologik qatlam xatosi: mehnat arabcha; bu Uychi uchun alohida nutq belgisi emas.'),
 ('Tappak = tez/shoshilinch','N7',6,'tappak','Bir dona yalang ta’rif; kontekstli mahalliy nutq bilan tekshirish kerak.'),
 ('Alvali/olvali har joyda olcha','N1',197,'mutlaqo farqlanuvchi','Mingbuloq maqolasi olcha deydi, Peshqo‘rg‘on maqolasi olcha va olxo‘ridan ajratadi. Hududiy ma’nolar birlashtirilmaydi.'),
 ('N8ning barcha viloyatni Namangan dialektiga kiritishi','N8',16,'Namangan dialekti','N2 PDF86 qipchoq shevalarini ochiq chiqaradi; N1 PDF39 ham viloyat ichki farqini asoslaydi.'),
 ('Uychi -vat va ayrim Uychi -ut farqi','N8',16,'Uychi - vat','Eski qo‘llanma va N3ning ayrim-hudud ta’rifi bir xil qamrov emas; zamon, joy va variant aniqlanadi.'),
 ('Mingbuloq taft/tapt/tavt boshso‘zi','N1',98,'Tapt','Manbada kaft ichi ta’riflanadi, adabiy taft esa issiqlik. Ta’rif va fonetik etimologiya farqlanadi.'),
 ('Mingbuloq joy nomlari','N1',96,'Rakasoviskiy','96-bet Rakasoviskiy, 99-bet Rakasovitskiy va Dehqonobod ishlatilgan. Ularning bir joy ekanligi manbada izohlanmagan.')]: claim(title,s,p,a,reason)
save('TEKSHIRILADIGAN_DAVOLAR.json',claims)

profiles=[
 dict(id='namangan_shahar',name='Namangan shahar',evidence=['N2 PDF26,86,92–94','N3 PDF5–7','N6 PDF2–3'],traits=['-ut davom zamoni','umlautning shartli ko‘rinishlari','emfatik cho‘ziqlik','opodda/acha/aba; shoti'],scope='Shahar nomi ostidagi dalil mahalla va barcha yosh guruhiga avtomatik umumlashtirilmaydi.'),
 dict(id='navkent',name='Yangiqo‘rg‘on / Navkent',evidence=['N4 PDF1–2'],traits=['127 jadval juftligi','yo‘nalish va savol ifodalari','kättä dedä=tog‘a; üka=singil'],scope='Bir qishloq; butun Yangiqo‘rg‘on yoki shahar bilan teng emas.'),
 dict(id='uychi',name='Uychi',evidence=['N7 PDF4–6','N8 PDF16,83','N3 PDF6'],traits=['mikro-shevalar','oka/o‘g‘ul/yomir/mashna','gindjelek; -vat va ayrim -ut manba farqi'],scope='Qishloq va zamon bo‘yicha variantlar aniqlanmaguncha bitta qat’iy paradigma berilmaydi.'),
 dict(id='peshqorgon',name='Chortoq / Peshqo‘rg‘on',evidence=['N1 PDF196–199'],traits=['olvali/olcha/olxo‘ri farqi','cho‘g‘oloq','o‘ngar','tirja'],scope='Chortoqning barcha hududi qarluq yoki -ut degan taxmin qilinmaydi.'),
 dict(id='mingbuloq_y_j',name='Mingbuloqning y/j-lovchi hamda aralash hududlari',evidence=['N1 PDF95–100','N3 PDF6–7 ikkilamchi iqtibos'],traits=['qishloq kesimidagi leksik farqlar','bărmăvüč/bărmiydigän','lagan chuqur/sayoz','ariq=pushta'],scope='Qishloq taqsimoti har so‘z uchun alohida; j-lovchi deb berilgan hududda barcha y ni j ga aylantirish yo‘q.'),
 dict(id='chust_and_uncovered',name='Chust, Shahand va kam yoritilgan boshqa areallar',evidence=['N1 PDF38–40','N2 PDF87'],traits=['Chust ayrim tasnifda Samarqand–Buxoro guruhida','Qilich/Uzun tarixiy tadqiqoti ikkilamchi eslatilgan','Shahand tasnifi munozarasi'],scope='Mavjud parchalar to‘liq zamonaviy Chust/Shahand nutq profili yaratish uchun yetmaydi.')]
save('HUDUDIY_PROFILLAR.json',profiles)
comparison=[
 dict(topic='Qarindoshlik',finding='Farg‘ona materiallarida buvi=ona misollari bor; Namangan shahar acha=buvi, aba=ona; Mingbuloq opa=ona. Bir hudud lug‘ati boshqasiga ko‘chirilmaydi.',current_refs=[ref('N6',3,'acha'),ref('N1',98,'Opa')],previous_file='../fargona/LUGAT.json'),
 dict(topic='Idish va meva',finding='Mingbuloq lagan ikki hududda chuqur/sayoz; Peshqo‘rg‘on olvali olcha/olxo‘ridan ajratilgan. “Viloyat lug‘ati” bitta ma’noga qisqartirilmaydi.',current_refs=[ref('N1',97,'Lagan'),ref('N1',197,'mutlaqo farqlanuvchi')]),
 dict(topic='Davom zamoni',finding='Farg‘ona Oltiariq/Uchko‘prik misollaridan Namangan -ut farq qiladi; N3 faqat shahar va Uychi/Chortoq ayrim joylarini ko‘rsatadi.',current_refs=[ref('N3',6,'faqatgina Namangan shahar')],previous_file='../fargona/GRAMMATIKA.json'),
 dict(topic='Umumiy vodiy leksikasi',finding='Shoti=narvon Namangan, Norin, Uychi va oldingi Farg‘ona manbalarida ham bor; bu eksklyuziv viloyat belgisi emas.',current_refs=[ref('N6',2,'Shoti')],previous_file='../fargona/LUGAT.json'),
 dict(topic='Umlaut',finding='Namangan tipidagi umlaut affiks ta’siriga bog‘liq. Surxondaryo/Qashqadaryo/Jizzax qipchoq shakllari bilan bitta tovush almashtirish tizimiga keltirilmaydi.',current_refs=[ref('N2',23,'affiksdagi')]),
 dict(topic='Umumiy kitoblar',finding='N1, N2 va N8ning oldingi yuborilgan aynan nusxalari SHA-256 bilan ajratildi. Bir manbaning ko‘p marta yuborilishi mustaqil tasdiq sanalmaydi.',current_refs=[])]
save('OLDINGI_HUDUDLAR_QIYOS.json',comparison)

coverage={
 'N1':dict(full_document_read=False,articles_read_complete=[[37,40],[95,100],[196,199]],selected_pages_read=[74],search_hits_context_checked=[36,177,178,179,211,212,213],note='216 betli to‘plamning Namangan bo‘yicha uch maqolasi to‘liq o‘qildi; toponim/affiliatsiya/bibliografiya natijalari nutq dalili emas.'),
 'N2':dict(full_document_read=False,selected_pages_read=[9,16,17,22,23,24,26,31,41,42,59,60,81,82,83,85,86,87,92,93,94],visual_checked_pages=[22,23,24,26,31,42,92,93,94],note='Namangan sarlavhali Suhbat PDF92 oxiri–94 boshi to‘liq o‘qildi. PDF94 qolgan qism Kitob tumani Ayronchi shevasi; Namangan deb olinmadi. Test savollari javoblari nutq dalili sifatida olinmadi.'),
 'N3':dict(full_document_read=True,pdf_pages_read=list(range(1,10))),
 'N4':dict(full_document_read=True,pdf_pages_read=[1,2,3],visual_checked_pages=[1,2],table_pairs=127,note='Ikki ustunli matn qatlamini vizual jadval juftlash bilan tekshirish; Compiled on sanasi respondent yozib olish sanasi emas.'),
 'N5':dict(full_document_read=True,pdf_pages_read=[1,2,3,4],note='Umumlashtirish va grammatik ma’no kamchiliklari alohida qayd etildi.'),
 'N6':dict(full_document_read=True,pdf_pages_read=[1,2,3],visual_checked_pages=[2],note='Nashrning aniq yili ushbu faylda topilmadi; taxminiy sana kiritilmadi.'),
 'N7':dict(full_document_read=True,pdf_pages_read=[1,2,3,4,5,6],note='PDF1 muqova, PDF2 nashr ma’lumoti, PDF3 mundarija (bosma771). Maqola PDF4–6 / bosma640–642. Mundarijadagi Norin maqolasi bu parchaga kirmaydi.'),
 'N8':dict(full_document_read=False,selected_pages_read=[15,16,17,80,81,82,83],visual_checked_pages=[15,16,80,81,82,83],note='97 skan PDF sahifa; OCR avvalgi bir xil nusxadan qayta ishlatildi. PDF1 bo‘sh; OCR sahifa raqamlari vizual tekshirildi. OCR bilan qidirish butun kitobni o‘qish degani emas.')}
save('OQISH_QAMROVI.json',coverage)
page_rows=[]
for s in sources:
    for n,t in enumerate(pages[s['id']],1): page_rows.append(dict(source=s['id'],pdf_page=n,text=t,extraction='cached_ocr' if s['id']=='N8' else 'native_pdf_text'))
assert len(page_rows)==477
(ROOT/'SAHIFALAR.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in page_rows))
stats=dict(uploaded_files=8,pdf_pages=477,fully_read_short_files=['N3','N4','N5','N6','N7'],fully_read_namangan_articles_in_N1=3,
           lexicon_records=len(lex),navkent_table_pairs=len(nav),phonetics_records=len(phon),grammar_records=len(gram),speech_records=len(speech),claims_to_verify=len(claims),area_profiles=len(profiles),model_training_performed=False)
save('HISOBOT_STATISTIKASI.json',stats)

checked=0
def validate(obj):
    global checked
    if isinstance(obj,dict):
        if 'anchor_extracted' in obj:
            assert obj['anchor_extracted'] in pages[obj['source']][obj['pdf_page']-1]
            checked+=1
        for v in obj.values(): validate(v)
    elif isinstance(obj,list):
        for x in obj: validate(x)
for f in ROOT.glob('*.json'):
    if f.name!='TEKSHIRUV_NATIJASI.json': validate(json.loads(f.read_text()))
for s in sources:
    assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
assert len({r['id'] for r in lex})==len(lex)
save('TEKSHIRUV_NATIJASI.json',dict(exact_page_anchors_checked=checked,source_file_hashes_checked=8,pdf_page_text_records=477,navkent_pairs_checked=127,all_checks_passed=True,scope='Dalilning fayl/sahifaga mosligi; ilmiy da’voning haqiqatligi yoki zamonaviy mahalliy qo‘llanish tasdig‘i emas.'))
print(json.dumps(stats,ensure_ascii=False,indent=2))
