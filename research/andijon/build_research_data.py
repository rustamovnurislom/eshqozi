"""Andijon: yozma dalillar, kichik hududlar va ma’no chegaralari."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
manifest = json.loads((ROOT / 'download_manifest.json').read_text())
texts = {x['id']: (ROOT / (x['id'] + '.txt')).read_text().split('\f') for x in manifest}
texts['A6'] = (ROOT / 'A6_ocr.txt').read_text().split('\f')

def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def printed(source, page):
    if source == 'A6':
        return {15: [26, 27], 82: [160, 161], 83: [162, 163]}.get(page, [])
    if source == 'A4':
        return [page + 21]
    match = re.search(r'\n\s*(\d{1,4})\s*$', texts[source][page - 1])
    return [int(match[1])] if match and int(match[1]) == page else []

def ref(source, page, anchor):
    text = texts[source][page - 1]
    assert anchor in text, (source, page, anchor)
    lines = text.splitlines()
    index = next(i for i, line in enumerate(lines) if anchor.splitlines()[0] in line)
    return {'source': source, 'pdf_page': page, 'printed_pages': printed(source, page),
            'anchor_extracted': anchor, 'evidence_extracted': '\n'.join(lines[max(0,index-1):index+6]),
            'extraction': 'reused_ocr' if source == 'A6' else 'pdf_text'}

articles = [
    {'id': 'A3-D', 'source': 'A3', 'title': 'Dardoq shevasida unlilarning cho‘ziq talaffuz qilinishi', 'author': 'Alimbekova Vazira Xalimjon qizi', 'pdf_pages': list(range(73,77)), 'read': 'to‘liq'},
    {'id': 'A3-L', 'source': 'A3', 'title': 'Insonlarning tashqi qiyofasini va sifatlarini ifodalovchi leksemalar', 'author': 'Alimbekova Vazira Xalimjon qizi', 'pdf_pages': list(range(170,176)), 'read': 'to‘liq; Dardoq'},
    {'id': 'A3-B', 'source': 'A3', 'title': 'Lisoniy shaxsni belgilashda dialektal omil', 'author': 'Umurzoqova Marhabo Egamberdiyevna', 'pdf_pages': [193,194,195], 'read': 'to‘liq; Andijon va Toshkent badiiy dialoglari ajratildi'},
    {'id': 'A7-Z', 'source': 'A7', 'title': 'Andijon dialektal zonasi haqida ba’zi bir mulohazalar', 'author': 'Sobirov Abdulhay Shukurovich', 'pdf_pages': [31,32,33,34,35], 'read': 'maqola boshlanishidan oxirgi bibliografiyasigacha'},
    {'id': 'A7-C', 'source': 'A7', 'title': 'Bolalar nutqining hududiy xoslanishi', 'author': 'Qurbonova Munavvara Abdujabborovna', 'pdf_pages': [119,120,121], 'read': 'maqola to‘liq; Andijon/Qo‘qonning papa so‘zi ajratildi'},
    {'id': 'A7-F', 'source': 'A7', 'title': 'Janubi-sharqiy Andijon shevalarining o‘ziga xos leksik xususiyatlari', 'author': 'Vazira Alimbekova', 'pdf_pages': list(range(327,333)), 'read': 'to‘liq', 'scope': 'Jalaquduq, Xo‘jaobod, Qo‘rg‘ontepa; 327-sahifa izohida berilgan'},
    {'id': 'A7-Q', 'source': 'A7', 'title': 'Andijon viloyatida qoraqalpoq shevasining lingvistik tadqiqi', 'author': 'Eraliyeva Naimaxon Raxmonjon qizi', 'pdf_pages': [472,473,474], 'read': 'maqola boshlanishidan bibliografiyasigacha', 'scope': 'Andijon tumanidagi qoraqalpoq kelib chiqishli aholi nutqi; aniq suhbatdosh va qishloq bo‘yicha misollar taqsimlanmagan'},
    {'id': 'A7-K', 'source': 'A7', 'title': 'Andijon viloyati kontinuumlari', 'author': 'Abdusalomova Ozoda Abduxalil qizi', 'pdf_pages': [477,478], 'read': 'to‘liq'}]
metadata = {
    'A1': {'title': 'O‘zbek dialektologiyasi', 'author': 'Ashirboev Samixon', 'year': 2011, 'institution': 'Nizomiy nomidagi Toshkent davlat pedagogika universiteti', 'duplicate_of': ['buxoro/B1'], 'read_pages': [1,22,35,36,37,38,39], 'reading_limit': 'Tasnif va Andijonga tegishli shakllar ko‘rildi. Butun 80 sahifa o‘qilgan emas. Buzilgan transkripsiya sahifa rasmlari bilan qiyoslandi.'},
    'A2': {'title': 'O‘zbek dialektologiyasi fanidan o‘quv-uslubiy majmua', 'author': 'Sh. Xudoyqulova', 'year': 2008, 'institution': 'Guliston davlat universiteti', 'duplicate_of': ['qashqadaryo/Q2','samarqand/M2','jizzax/J2'], 'read_pages': [1,34,38,39,40,41,42,43], 'reading_limit': 'Andijon tasnifi va aniq belgilangan misollar. O‘quv savollari/topshiriqlari foydalanuvchining topshirig‘i sifatida bajarilmadi.'},
    'A3': {'title': 'O‘zbek shevalari tadqiqotlari: amaliyot, metodologiya va yangicha yondashuv', 'editor': 'Sh. Sirojiddinov', 'year': 2022, 'conference_date': '2022-05-21', 'publisher': 'Donishmand ziyosi, Toshkent', 'duplicate_of': ['samarqand/M4','jizzax/J1'], 'read_pages': list(range(73,77))+list(range(170,176))+[87,193,194,195], 'reading_limit': 'Uch tegishli maqola to‘liq, 87-sahifadagi Andijon sifat yasovchilari qiyosi o‘qildi. Boshqa hududlarning misollari to‘liq Andijonniki deb olinmadi.'},
    'A4': {'title': 'O‘zbek shevalari lug‘atlarining qiyosiy tavsifi', 'authors': ['Turdaliyeva Sayyora Mamatali qizi','Abduraxmonov Abduvali Abdumalik o‘g‘li'], 'year': None, 'doi': '10.5281/zenodo.15332055', 'publication': 'Models and Methods in Modern Science, international scientific-online conference', 'read_pages': [1,2,3,4,5], 'reading_limit': 'To‘liq o‘qildi. Umumiy lug‘atchilik maqolasi, mustaqil Andijon so‘zlashuvi dalili emas. 1971-yil lug‘atida Jizzax yo‘qligi haqidagi da’vo oldingi tekshirilgan qaydlar bilan mos kelmaydi.'},
    'A5': {'title': 'Farg‘ona (Oltiariq) guruhi shevalarining fonetik tahliliga doir', 'authors': ['G. Jo‘raboyeva','M. Tursunboyeva'], 'year': None, 'read_pages': [1,2,3], 'reading_limit': 'To‘liq o‘qildi. Andijon dalili qilib olinmadi; Farg‘ona/Oltiariq bosqichiga hududi bilan saqlandi. Ba’zi fonetik jarayon izohlari chalkash.'},
    'A6': {'title': 'O‘zbek shevashunosligi', 'authors': ['T. J. Enazarov','V. A. Karimjonova','M. S. Enazarova','Sh. S. Mahmadiyev','K. G‘. Rixsiyeva'], 'year': 2012, 'publisher': 'Universitet, Toshkent', 'duplicate_of': ['samarqand/M5','buxoro/B2'], 'ocr_text_path': str(ROOT/'A6_ocr.txt'), 'read_pages': [15,82,83], 'visual_checked_pages': [15,82,83], 'reading_limit': 'Skan. Oldingi aynan bir faylning OCRi qayta ishlatildi; tegishli sahifalar tasvirda tekshirildi. Ko‘p PDF sahifalarida ikkita bosma sahifa bor. Barcha 97 sahifa qayta to‘liq o‘qilmadi.'},
    'A7': {'title': 'O‘zbek folklori va shevalari tadqiqotlari: amaliyot, metodologiya, yangicha yondashuv', 'editor': 'Shuhrat Sirojiddinov', 'year': 2024, 'conference_date': '2024-05-25', 'publisher': 'Toshkent', 'read_pages': [1,2]+list(range(31,36))+[119,120,121]+list(range(327,333))+[472,473,474,477,478], 'reading_limit': 'Besh tegishli maqola o‘qildi. 640 sahifaning barchasi to‘liq o‘qilgan emas. Hududiy qidiruvdagi boshqa mosliklar kontekst asosida saralandi.'},
    'A8': {'title': 'Tilshunoslikka kirish', 'authors': ['M. Abuzalova','D. Yo‘ldosheva'], 'year': 2005, 'publisher': 'Universitet, Toshkent', 'read_pages': [1,2], 'context_checked_pages': [87,94,99,157], 'reading_limit': 'Umumiy tilshunoslik qo‘llanmasi. Qidiruvdagi Andijon asosan bibliografiyadagi nashr joyi. Mustaqil hududiy nutq dalili aniqlanmadi; butun kitob o‘qilmadi.'},
    'A9': {'title': 'O‘zbek tilini dunyo miqyosida keng targ‘ib qilish bo‘yicha hamkorlik istiqbollari', 'year': 2020, 'conference_date': '2020-10-19/2020-10-20', 'publisher': 'Toshkent', 'context_checked_pages': [51,52,53,55,141,142,143], 'reading_limit': 'Hududiy qidiruv va kontekst ko‘rildi. 51–55-sahifalardagi Iqon maqolasi Andijon kitobini bibliografiyada keltiradi; Iqon misollari Andijonniki qilib olinmadi. Boburnoma gidronimlari bugungi suhbat dalili emas. Butun 550 sahifa o‘qilmadi.'}}
for x in manifest:
    x.update(metadata[x['id']]); x['text_path'] = str(ROOT/(x['id']+'.txt'))
save('MANBALAR.json', {'uploaded_sources': manifest, 'articles_read': articles,
    'read_claim': 'Sahifali matn ajratish va hududiy qidirish barcha kitoblarni to‘liq o‘qish degani emas.',
    'transcription_policy': 'Manba yozuvi dalillarda saqlanadi. Latincha display shakllari soddalashtirilgan, audio/IPA tekshiruvi emas. Muallif tarjimasi va tahririy talqin farqlanadi.',
    'independence_limit': 'Takror fayllar, bir muallifning 2022/2024 maqolalari va 1967-yil kitobidan ikkilamchi iqtiboslar alohida mustaqil dala tasdiqlari deb sanalmaydi.'})
with (ROOT/'SAHIFALAR.jsonl').open('w') as out:
    for x in manifest:
        for n in range(1,x['pages']+1):
            out.write(json.dumps({'source': x['id'], 'pdf_page': n, 'printed_pages': printed(x['id'],n),
                'extraction': 'reused_ocr' if x['id']=='A6' else 'pdf_text',
                'text_extracted': texts[x['id']][n-1]},ensure_ascii=False)+'\n')

lexicon=[]
def word(form, meanings, region, source, page, anchor, tone='betaraf', note='', variants=None, domain='kundalik nutq'):
    lexicon.append({'id': f'AL{len(lexicon)+1:03}', 'display_form': form, 'meanings': meanings.split(' | '),
        'region': region, 'domain': domain, 'tone': tone, 'variants': variants or [],
        'exclusive_to_region': None, 'independent_modern_usage_verified': False, 'audio_verified': False,
        'evidence_type': 'yozma manbada hududga nisbat berilgan; dala suhbatiga mustaqil kirish yo‘q',
        'usage_note': note, 'source_refs': [ref(source,page,anchor)]})

for form, meaning, page, anchor, tone, note, variants in [
    ('hilvaligim','xushbichim, xipcha bel, nozik va chiroyli qomat haqidagi shakl',170,'hilvaligim','ijobiy','Manbada egalik qo‘shimchali shakl. Mustaqil hilva lemma taxmin qilinmadi.',[]),
    ('chayir','jussasi kichik bo‘lsa ham chaqqon, chapdast kishi',170,'chayir degan','ijobiy','Yog‘ochning chayirligi ma’nosidan ajratiladi.',[]),
    ('chikalak','tengdoshlariga nisbatan bo‘yi past, jussasi kichik bola',171,'chikalak leksemasi','ko‘rinishni baholash','Har bir bola uchun betaraf murojaat emas.',[]),
    ('pechal','rangi so‘lg‘in, nosog‘lom ko‘rinadigan bola',171,'pechal,','baholovchi','Muallifning tashqi ko‘rinish tavsifi; klinik tashxis emas. Misoldagi ovqat berish gapi tibbiy tavsiya sifatida olinmadi.',['majik']),
    ('nakas','yebto‘ymas, ochko‘z | ayrim kontekstlarda ziqna, xasis',171,'nakas so‘zi','salbiy','Adabiy nokasning barcha ma’nolari bilan avtomatik tenglashtirilmaydi.',[]),
    ('piska','ko‘zi qisiq haqida aytiladigan sifat',171,'piska leksemasi','ko‘rinishni baholash','Muallif etnik o‘xshatish ham ishlatadi; u aholiga umumiy belgi yoki botning murojaat odati qilinmaydi.',[]),
    ('uziqara','urishqoq, aytishadigan kishi',171,'uziqara so‘zi','salbiy','Shaxsni tanqid qilish konteksti.',[]),
    ('tulos','uy tutumi saranjom bo‘lmagan kishi',172,'Tülӓsgә','tanbeh','Tulos/polpis manba yozuvida tülas/palpis shakllari bilan ham berilgan.',['polpis']),
    ('danak','kichkina bo‘lsa ham gapga chechan yosh qizcha',172,'Danak, daqqi','baholovchi','Danakning meva urug‘i ma’nosi bilan aralashtirilmaydi. Manba yosh qizchalar haqida.',['daqqi']),
    ('mamadana','ko‘p gapiradigan, gap talashadigan qiz; mahmadona',172,'Mamadana','salbiy','Manbadagi yosh/jins konteksti saqlanadi.',[]),
    ('shaldir-shuldir','kirishimli, sodda, hamma bilan chiqishadigan, ko‘nglida kiri yo‘q odam',172,'shaldir-shuldir so‘zi','ijobiy','Bu qaydda shovqin-suron emas, kishining fe’li nazarda tutilgan.',[]),
    ('gajir','aytganini qildiradigan, qaysar, jangari',172,'Gajir –','salbiy','Insonga ham, bo‘ysundirish qiyin otga ham ishlatilishi qayd etilgan.',[]),
    ('juda-','ish ko‘pligidan ulgurolmay, o‘zini eplay olmay qolish',172,'ishlarga ulgurmaslik','holat tavsifi','Misolda judadim. Juda ravishi bilan bir xil tarjima qilinmaydi; fe’lning to‘liq paradigmasi berilmagan.',[]),
    ('biram','rosa; juda; juda ham',172,'Biram leksemasi','kuchaytirish','Kuchaytiruvchi ma’no.',[]),
    ('olako‘tan','ko‘ngli toza, g‘araz niyati yo‘q kishi',172,'olako‘tan','ijobiy','Muallif ko‘proq yoshi ulug‘ kishilar nutqida uchrashini aytadi.',[]),
    ('tosbet','gap ta’sir qilmaydigan, bezbet kishi',173,'tosbet).','salbiy; tanbeh','Tosray- fe’li bilan yonma-yon berilgan; uni bir xil so‘z turkumi deb olmadim.',[]),
    ('tulak','ayyor',173,'tulak','salbiy','Manbada tulay varianti ham bor.',['tulay']),
    ('poyipaytava','laganbardor; manfaat uchun xushomad qiladigan kishi',173,'poyipaytava leksemasi','salbiy','Tanqidiy atama.',[]),
    ('genamas','e’tiborsiz, boshqalarga past nazar bilan qaraydigan',173,'Genämäs','salbiy','Yonidagi toɣat shaklining mustaqil ma’nosi aniqlashtirilmagan.',[]),
    ('qo‘ramas','dangasa, ishyoqmas, tanbal',173,'qo‘ramas','salbiy','Shaxsni malomat qilish konteksti.',[]),
    ('arjay','bo‘lar-bo‘lmasga kuladigan, o‘rinsiz hazil qiladigan kishi',173,'arjay deb','salbiy','Kulgining har bir holatini bu so‘z bilan atash o‘rinli emas.',[]),
    ('avirli','obro‘li odam | ish, joy, kiyim, taom haqida ham hurmat/munosiblik bahosi',173,'avirli so‘zi','ijobiy','Ikkinchi ma’no tahririy mazmuniy umumlashtirish; muallif avirli ish/joy/kiyim/taom birikmalarini sanaydi.',[]),
    ('chimxo‘r','ovqatni tanlab, oz-oz yeydigan kishi',174,'chimxo‘r atamasi','baholovchi','Insonga nisbatan ishlatilishi qayd etilgan; boshqa shevalarda hayvon haqida ham deyiladi.',[])]:
    word(form,meaning,'Andijon, Dardoq qishlog‘i; aniq tuman bu maqolada belgilanmagan','A3',page,anchor,tone,note,variants)

SE='Janubi-sharqiy Andijon: Jalaquduq, Xo‘jaobod, Qo‘rg‘ontepa; har birlik qishloq bo‘yicha ajratilmagan'
for form, meaning, page, anchor, note, variants in [
    ('xunon','yoyilgan xamir ichiga qiyma solib pishiriladigan taom; xonim',327,'(xunon)','O‘rama varianti Abdullabiy, Progress, Qizilto‘qay qishloqlari uchun berilgan. Adabiy o‘rama izohi boshqacha bo‘lishi mumkin.',['o‘rama']),
    ('po‘shkal','yupqa yoyilib qozonda pishiriladigan, qatlamaga o‘xshash taom',328,'(po‘shkal)','Hozirgi izohida ozroq masalliq bor; I. Farmonovdan keltirilgan izoh yog‘siz non turi. Ta’riflar farqi saqlanadi.',[]),
    ('qoqirim','qatiq, piyoz, murch, sariyog‘ va qaynagan suvdan tayyorlanadigan taom',328,'(qoqirim)','Maqoladagi shamollash haqidagi ta’rif davolash samarasi isbotiga aylantirilmaydi. Qaqurum boshqa lug‘atdan keltirilgan shakl.',['qaqurum']),
    ('laz','qizil bulg‘or qalampiridan qishga konservalanadigan mahsulot',328,'Laz (laz)','Lazi varianti Baliqchi va Ulug‘nor uchun alohida qayd etilgan.',['lazi']),
    ('shakarob','pomidor va piyozdan tayyorlanib osh bilan yeyiladigan salat',328,'(shakarob)','Toshkentdagi achchiq-chuchuk bilan qiyoslangan; eksklyuziv Andijon so‘zi emas.',[]),
    ('xomshakarop','qishga tayyorlanadigan yog‘siz sabzavot konservasi',328,'(xomshakarop)','Shakarobning salat ma’nosidan alohida.',[]),
    ('qo‘urma shakarob','qishga tayyorlanadigan sabzavot konservasi turi',328,'(qo‘urma shakarob)','Manba bu turga alohida to‘liq retsept bermaydi; qovurish usuli dalilsiz batafsillashtirilmadi.',[]),
    ('ko‘mach','qozonda yoki o‘tda pishirilgan non',328,'(ko‘mach)','Muallif Mushkulkushot/Buseshanbi marosim kontekstini ham beradi; marosimdagi cheklovlar barcha ko‘machga universal qoida emas.',[]),
    ('chirik non','piyoz, yog‘ va ziravor solib pishirilgan non',328,'(chirik non)','Piyoz non bilan qiyoslanadi; buzilgan non ma’nosi emas.',[]),
    ('g‘o‘r-sho‘r','ho‘l meva va sabzavotlar',328,'(g‘o‘r-sho‘r)','Muallifning hududiy semantik qaydi.',[]),
    ('bulamiq','un sariyog‘da qovurilib sut bilan qaynatilgan suyuq taom',328,'(bulamiq)','Muallif bolalar ovqati deydi. Jizzaxdagi tuxum-un aralashmasi haqidagi qiyos aynan shu retsept emas.',[]),
    ('ko‘ptirgi','xamir oshirish uchun solinadigan achitqi',328,'(ko‘ptirgi)','Kelasi xamir uchun oshgan xamirdan olib qo‘yish jarayoni bilan izohlangan.',['xamir turish']),
    ('umoch osh','un va sutdan tayyorlanadigan suyuq marosim taomi',329,'umoch osh','Qashqadaryoning imach osh shakli qiyos; Andijonning o‘z varianti deb olinmadi.',[]),
    ('sutosh','sutga kesilgan xamir yoki guruch solib tayyorlanadigan suyuq taom',329,'(sutosh)','Ayrim joylarda oshqovoq ham qo‘shilishi aytilgan.',[]),
    ('so‘l','ovqatning suvi ko‘proq holati | qovurilgan go‘sht',329,'(so‘l)','Ikki ma’no muallifda alohida berilgan. Chap tomon ma’nosidagi adabiy so‘l bilan tenglashtirilmaydi.',[]),
    ('suyg‘osh','mayda kesilgan xamir solib mastavaga o‘xshatib pishiriladigan taom',329,'(suyg‘osh)','Guruch o‘rniga xamir; kesilgan xamir zaxiraga quritilishi ham aytilgan.',[]),
    ('kesgan osh','kesilib quritilgan xamirni qovurib ovqatga solib damlab tayyorlanadigan taom',329,'(kesgan osh)','Manba kesgan deb yozadi; keskan transkripsiyasi ham berilgan.',['uzma osh']),
    ('nompalov','qotgan yoki suvi qochgan non bilan tayyorlanadigan taom',329,'(nompalov)','Nonpalov → nompalov izohi muallifniki.',[]),
    ('kalpatir','qaymoq surilgan achitqisiz xamirdan tandirda yopiladigan non',329,'(kalpatir)','Sho‘rva bilan yeyish konteksti ham bor.',[]),
    ('uvuz','sigir yangi tug‘ganda birinchi sog‘ilgan sutini qaynatib tayyorlangan taom',329,'(uvuz)','Bu qayd tayyor mahsulotni ta’riflaydi. Og‘iz suti ayrim Andijon hududlarida variant sifatida berilgan.',['og‘iz suti']),
    ('sut tortmoq','sutdan qaymoq olish',329,'(sut tortmoq)','Tortmoqning barcha ma’nolariga tatbiq qilinmaydi.',[]),
    ('sizg‘irmoq','qaymoqni olovda qizdirib sariyog‘ olish',330,'(sizg‘irmoq)','Sariyog‘ bilan birga qo‘llanishi qayd etilgan.',[]),
    ('yashang','ho‘l meva yoki rezavorning yangi uzilgani haqida belgi',330,'(yashang)','Murojaatdagi Yashang! bilan bir xil ma’no emas.',[]),
    ('nasvi','to‘y yoki marosim qatnashchisiga atalgan tuguncha',330,'(nasvi)','Nasiba bilan etimologik bog‘liqligi muallif taxmini; qat’iy fakt sifatida olinmadi.',[]),
    ('to‘qsi tovoq','bo‘laklarga ajratilgan taqsimchalar jamlanmasi',330,'(to‘qsi tovoq)','Shirinlik/chaq-chuq uchun. Taksiga aloqador shakl deb olinmaydi.',[]),
    ('oqsoqoltovoq','keksalarga maxsus osh solingan lagan',330,'(oqsoqoltovoq)','Marosimdan keksaga yuborish misoli bor.',[]),
    ('mazar','to‘ydan avval sovg‘a-salom yuboriladigan marosim | kelin qarindoshlari to‘ydan keyingi qirq kunda olib boradigan ovqat',330,'Mäzär\\mazar','Mozor ma’nosiga avtomatik bog‘lanmaydi; ikkala ma’no saqlandi.',[]),
    ('peshdasturxon','mehmon oldiga alohida patnisda yasatib keltiriladigan noz-ne’matlar',330,'(peshdasturxan)','Mehmon ketayotganda tugib berilishi qayd etilgan; oddiy dasturxon matosi emas.',['peshdasturxan']),
    ('irimoq','sut mahsulotining aynishi',331,'(irimoq)','Muallif bu hududda faqat sut mahsulotiga tegishli deydi; barcha ovqatga kengaytirilmadi.',[]),
    ('po‘panak bosdi','nonni mog‘or bosishi',331,'(po‘panak bosdi)','Manbada fe’l shakli bilan; barcha suv o‘tlari ma’nosiga tenglashtirilmaydi.',['pangladi']),
    ('qaqirmachak','oshning tagiga olgan qismi | tandirda qolib qattiq pishgan non qismi',331,'(qaqirmachak)','To‘yda yomg‘ir haqidagi irim alohida folklor mazmuni, bashorat qoidasi emas.',[]),
    ('keshik','kosada yeyishdan ortgan ovqat | marosimdan mehmonlar ketgach qolgan noz-ne’matlar',331,'(keshik)','Ikki ko‘rinishli qoldiq ovqat ma’nosi.',[]),
    ('kavartak','uzum bargiga qiyma o‘ralib osh zirvagida pishiriladigan taom',331,'(kavartak)','Tokoshi bilan qiyoslangan.',[]),
    ('do‘lta','qaymoqdan sariyog‘ olishda tagiga cho‘kadigan qora quyqa',331,'(do‘lta)','Adabiy durda va Qashqadaryodagi to‘rta bilan qiyoslangan.',[]),
    ('hamak','pishmagan qovun; sapcha',331,'(hamak)','Manbada xomek varianti ham bor.',['xomek']),
    ('chalop','qatiqqa suv va tuz solib tayyorlangan yaxna ichimlik',331,'(chalop)','Ayron bilan qiyoslangan; faqat bu hududga xosligi tasdiqlanmagan.',[]),
    ('qurtop','tuzlangan suzmani yumaloqlab oftobda quritilgan mahsulot; qurut',331,'(qurtop)','Fonetik ko‘rinish qurtap sifatida ham yozilgan.',[]),
    ('to‘qoch','kichkina non; kulcha',331,'(to‘qoch)','Bolali xonadonda non bilan qo‘shib yopilishi aytilgan.',[]),
    ('moy to‘qoch','yupqa xamirni yog‘da pishiriladigan cho‘zma-chalpak',331,'(moy to‘qoch)','Is chiqarish marosimi kontekstida xolvaytar bilan tarqatilishi tasvirlangan.',[]),
    ('uyitqi','qatiq qilish uchun sutga solinadigan ozgina qatiq; tomizg‘i',332,'(uyitqi)','Quramaning ujutqï shakli qiyos sifatida qoladi.',[]),
    ('chuli','turshakni qaynatib yoki issiq suvda ivitib tayyorlangan ichimlik',332,'(chuli)','Yangi o‘rikning oddiy siqilgan sharbati emas. Maqolada 1971-yil lug‘atiga ishora bor.',[]),
    ('oxyog‘','chigitdan olingan paxta yog‘i',332,'(oxyog‘)','Har qanday yog‘ga qo‘llanmaydi.',['oxmoy']),
    ('doxsu','qaynatilgan suv',332,'(doxsu)','Objo‘sh bilan boshqa hudud qiyosi bor; bir xil yozuv varianti deb olinmaydi.',[])]:
    word(form,meaning,SE,'A7',page,anchor,note=note,variants=variants,domain='oziq-ovqat, uy-ro‘zg‘or yoki marosim')

for form, meaning, region, anchor, note, variants in [
    ('so‘rtak','ishkom; toklarni ko‘tarib yoyish uchun qurilgan so‘ri','Andijon va Baliqchi tumanlari','so‘rtak','Dam olish uchun oddiy so‘ri ma’nosi bu qaydda berilmagan.',[]),
    ('so‘kichak','ishkom','Paxtaobod, Ulug‘nor, Shahrixon, Oltinko‘l, Jalaquduq','so‘kichak','Muallif tumanlar kesimida qayd etgan, barcha so‘zlovchiga universal emas.',[]),
    ('valish','ishkom','Izboskan va Qo‘rg‘ontepa tumanlari','valish','Yostiq ma’nosidagi boshqa shakl bilan dalilsiz tenglashtirilmaydi.',[]),
    ('qallama','qatlama','Shahrixon va Qo‘rg‘ontepa','qallama','Taomning qatlamli ekanligi aytilgan.',[]),
    ('malda','qatlama','Baliqchi','malda','Taom kontekstida.',[]),
    ('qahlama','qatlama','Andijon tumani va yondosh qishloqlar','qahlama','Pahlava ayrim joylarda deyiladi, ammo aniq hududi belgilanmagan.',[]),
    ('dastkalla','go‘sht yoki sabzavot to‘g‘rash uchun chopqi','Shahrixon','dastkalla','Buyum ma’nosi.',[]),
    ('gupsi','ombur','Shahrixon','gupsi','Muallifning ombur vazifasi tavsifi batafsil mustaqil tekshirilmagan.',[]),
    ('otqi','xaskash','Paxtaobod','otqi','Xashak/xas-cho‘p yig‘ish va yer tekislash quroli.',[]),
    ('grabil','xaskash','Andijon tumani va boshqa hududlar; kengroq chegara aniq emas','grabil','Yertaroq ham shu ma’noda berilgan.',['yertaroq']),
    ('xo‘pitmoq','suv havzasida cho‘milmoq','Baliqchi va atrofi','xo‘pitmoq','Muallif asosan katta avlod tilida ishlatilishini ta’kidlaydi.',[]),
    ('hayat','uyning orqa tarafi; hovli haqidagi qayd','Baliqchi','hayat','Kontekstdagi uy/hovli ma’nosi; hayot so‘zini almashtirish qoidasi emas.',[])]:
    word(form,meaning,region,'A7',478,anchor,note=note,variants=variants)

for form, meaning, anchor, note in [
    ('jezda','pochcha','Jezda (pochcha)','Qoraqalpoq kelib chiqishli aholi nutqiga nisbat berilgan.'),
    ('echeyen jezda','oddiy pochcha','echeyen jezda','Muallifning ayni izohi; qarindoshlik turini aniqroq taxmin qilmadim.'),
    ('karsang','tog‘ora','karsang (','Uy-ro‘zg‘or atamasi.'),
    ('boldiz','kelinning opa-singlisi','boldiz (','Manbaning ayni ta’rifi; boshqa tillardagi qarindoshlik izohlari qo‘shilmadi.'),
    ('chavgon','qumg‘on','chavgon (','Ushbu mahalliy qaydda idish; ot o‘yini ma’nosi bilan bir xil emas.'),
    ('manglay','peshona','manglay','Boshqa hududlarda ham uchrashi mumkin.'),
    ('bo‘rk','telpak','bo‘rk','Bosh kiyim.'),
    ('emgak','mehnat','emgak','Samarqand/Forish tarixiy so‘z maqolalaridagi har bir ma’no shu mahalliy qaydga ko‘chirilmaydi.'),
    ('ko‘lik','transport','ko‘lik','Muallif izohi keng transport ma’nosida.'),
    ('mo‘ncha','hammom','mo‘ncha','Muallif yozuvi.'),
    ('qangli','ikki g‘ildirakli arava','qangli','Bu qaydda buyum nomi; urug‘ nomi ma’nosida emas.')]:
    word(form,meaning,'Andijon tumanidagi qoraqalpoq kelib chiqishli aholi nutqi; A7-Q','A7',473,anchor,note=note)
word('kette:', 'bobo', 'Andijon; umumiy qo‘llanmadagi qayd','A2',41,'kette:',note='Katta ota bilan bog‘langan shakl; Toshkent buva shakli bilan qiyoslangan.',variants=['kette ete'])
word('evere', 'arava', 'Andijon; umumiy qo‘llanmadagi qayd','A6',83,'evere (Andijon)',note='Bosma 162-sahifa vizual tekshirildi. Muallif metateza guruhida sanaydi, lekin bu juftlikdan undosh o‘rin almashinuvi qoidasi chiqarilmadi.')
word('peshe', 'chivin (ruscha komar)', 'Andijon; Sayram, Chimkent, Forish bilan birga','A6',82,'peshe (Sayram',note='Bosma 160-sahifa vizual tekshirildi. Shu nomning boshqa hududlarda pashsha ma’nosi bilan kelishi alohida qiyoslangan.')
word('papa', 'harorat; issiqlik', 'Andijon va Qo‘qon, kichik yoshdagi bolalar nutqi','A7',119,'harorat (issiqlik)',note='Bolalar va ular bilan muloqot qiluvchi kattalar registri. Oddiy kattalar suhbati uchun universal so‘z emas.',domain='bolalar nutqi')
save('LUGAT.json',lexicon)

idioms=[]
for form, meaning, literal, page, anchor, tone, note, variants in [
    ('Chopmagan devasi yo‘q','buzg‘unchi, urishqoq, janjalkash odam haqida','Manba deva so‘zini muqaddas tepalik deb izohlaydi; alohida mustaqil lug‘aviy tasdiq olinmagan.',174,'Chopmagan devasi yo‘q','salbiy','Manbadagi deva shakli tuya ma’nosida deb tarjima qilinmadi.',[]),
    ('Jerdi kinnigini uzmoq','tinim bilmay ishlaydigan, qiyin yumushlarni ham bajaradigan kishini ifodalash','Yerning kindigini uzmoq.',174,'jerdi kinnigini üzmoq','maqtov','Muallif asosan ayollarga nisbatan qo‘llanishini qayd etadi; bu hamma ayolga xos xarakter degani emas.',[]),
    ('Lakatri kuchli','gap poylab, boshqalarning gapini eshitib olish haqidagi ifoda',None,174,'lӓkӓtri küčli','tanqid yoki hazil; kontekstga bog‘liq','Eshitishning klinik kuchliligi ma’nosiga tenglashtirilmaydi.',[]),
    ('Qulog‘i ding','boshqalarning gapini poylab eshitadigan kishi haqida',None,174,'qulāɣї diɳ','tanqid yoki hazil','Manbada ding quloq shakli ham shu kontekstda berilgan.',['ding quloq']),
    ('Chimxo‘r ho‘kiz ochdan o‘lar','ovqatni ortiqcha tanlashni tanqid qiluvchi maqol','Chimxo‘r ho‘kiz ochdan o‘lar.',174,'čïmxor hokïz','tanbeh','Maqolni o‘quvchiga tibbiy xulosa yoki betaraf maqtov qilib ishlatmaslik kerak.',[])]:
    idioms.append({'id':f'AI{len(idioms)+1:02}','display_form':form,'meaning':meaning,'literal':literal,
        'region':'Andijon, Dardoq qishlog‘i','genre':'maqol' if 'ho‘kiz' in form else 'ibora yoki obrazli birikma',
        'tone':tone,'usage_note':note,'variants':variants,'exclusive_to_region':None,'source_refs':[ref('A3',page,anchor)]})
for form, meaning, anchor in [
    ('ushug urmoq','meva-sabzavotni sovuq urishi','(ushug urmoq)'),
    ('non push tashlamoq','tandirga yopilgan non pishmasdan tushib ketishi','(non push tashlamoq)'),
    ('non gullamoq','yaxshi oshmagan xamirdan yopilgan nonning ayrim joylari qavarishi','(non gullamoq)')]:
    page=329 if form=='ushug urmoq' else 330
    idioms.append({'id':f'AI{len(idioms)+1:02}','display_form':form,'meaning':meaning,'region':SE,
        'genre':'oziq-ovqat jarayonini ifodalovchi birikma','tone':'betaraf',
        'usage_note':'Ko‘chma shaxs tavsifiga dalilsiz aylantirilmaydi. Push/pusht haqidagi etimologik izoh mustaqil tekshirilmagan.',
        'source_refs':[ref('A7',page,anchor)]})
save('IBORALAR.json',idioms)

grammar=[]
def observation(form, standard, region, source, page, anchor, note):
    grammar.append({'id':f'AG{len(grammar)+1:02}','attested_form_display':form,'standard_context_form':standard,
        'region':region,'evidence_level':'yozma misol yoki aniq guruhga nisbat berilgan tavsif',
        'automatic_global_replacement':False,'note':note,'source_refs':[ref(source,page,anchor)]})
for form, standard, anchor in [
    ('qä:dä','qayerda','Qä:dä (qayerda)'),('mä:da','mana bu yerda','mä:da (mana'),
    ('qïpqä:man','qilib qo‘yaman','qïpqä:man'),('jāzā:raman','yozaveraman','jāzā:raman'),
    ('do::rmä','deyaverma','do::rmä'),('to:rïsï','to‘g‘risi','to:rïsï'),
    ('qäjmä:','qaymoq','qäjmä:'),('qïšlä:','qishloq','qïšlä:'),
    ('de:mїz / di:miz','deymiz','pӓrmӓ de:mїz'),('go:…go:','goh…goh','go:…go:')]:
    observation(form,standard,'Dardoq','A3',75,anchor,'Cho‘ziqlik belgisi manbadagi yozuvga bog‘langan; audio o‘lchovi va har so‘z uchun umumiy tushirish qoidasi yo‘q.')
observation('ga:gi / ga:gida','gohi / gohida','Dardoq','A3',76,'ga:gi, ga:gida','Muallif ma’nodosh bog‘lovchi/ravish shakllarini qiyoslagan.')
observation('-ni oilasining -n/-d/-t variantlari','qaratqich va tushum kelishigi','Andijon, Marg‘ilon, Qo‘qon guruh shevalari','A1',38,'Tushum-qaratqich affiksidagi','Fonetik guruh tavsifi; hamma so‘z uchun bir xil variant tayinlanmaydi.')
observation('-yap / -yoyap; kelayapman','hozirgi zamon davom fe’li','Andijon shahar shevasi, tasnifdagi qayd','A6',15,'kelayapman','Bosma 26-sahifa rasmdan tekshirildi. A1 PDF39 paradigmasi ham qiyoslandi; OCRdagi -йэр yozuvi umumiy -yar qoidasi qilib olinmadi.')
observation('aq’ll’g, ch’rͻ:l’k','aqlli, chiroyli','Andijon; 1967-yilgi kitobdan ikkilamchi iqtibos','A3',87,'And. aq’ll’g','Sifat yasovchi -li va -lik variantlari haqida qiyos; Navoiy maqolasining barcha misollari Andijonniki emas.')
for form,standard,region,anchor in [
    ('sövzï','sabzi','Shahrixon, Segaza','sövzï'),('sövdogar / Shövkat / Rövshan','savdogar / Shavkat / Ravshan','Shahrixon, Segaza','sövdogar'),
    ('tag‘a / yang‘aq / bala','tog‘a / yong‘oq / bola','Izboskan, Gurkirov MFY','tog‘a (tag‘a)')]:
    observation(form,standard,region,'A7',477,anchor,'Bir maqoladagi mahalliy misollar. Manbaning unli qatori haqidagi terminlari bahsli; kuzatilgan shakl saqlanadi.')
for form,standard,anchor in [('akamdi kitobi','akamning kitobi','akamdi kitobi'),('guldi uzmoq','gulni uzmoq','guldi uzmoq'),('bayda / bayga / shayda / shetka','bu/shu yerga va yerda shakllari','bayda, bayga')]:
    observation(form,standard,'Baliqchi','A7',478,anchor,'Muallif qaratqich/tushum yoki ko‘rsatish shaklini birgalikda qayd etgan. Har bir ko‘rsatish shaklining aniq muhitini dalilsiz to‘liq paradigmaga yoymadim.')
observation('uyaq / buyaq / mashi / ashi','u/bu yoq; mana/ana shu','Xo‘jaobod, Jalaquduq, Qo‘rg‘ontepa','A7',478,'buyaq, mashi','Muallif guruhli qiyosi; mashi va ashi kundalik gapdagi alohida ko‘rsatish vazifasiga bog‘lanadi.')
for form, standard, anchor, note in [
    ('jazdi / jüldüz / jantaq','yozdi / yulduz / yantoq','yozdi – jazdi','So‘z boshidagi y/j muvofiqligi; hamma y tovushi almashtirilmaydi.'),
    ('kichi / sari / tari','kichik / sariq / tariq','kichik – kichi','Oxirgi q/k tushishi ayni misollarda.'),
    ('iechki / uo‘rdak','echki / o‘rdak','iechki','Diftong sifatida tavsiflangan yozma shakllar; audio yo‘q.'),
    ('hari / harra','ari / arra','ari – hari','So‘z boshida h ortishi shu juftliklarda.'),
    ('ul / bul / shul','u / bu / shu','ul, bul, shul','Ko‘rsatish olmoshlari.'),
    ('mag‘an / sag‘an / ug‘an','menga / senga / unga','mag‘an (menga)','Olmoshlarning jo‘nalish shakllari.'),
    ('keläjätïr / kelävätïr / kepjätïr','kelayotganlikni ifodalovchi shakllar','keläjätïr','Hozirgi zamon davom shakllari; Andijon shahar -yap bilan aralashtirilmaydi.'),
    ('jazatig‘an / kelätïgan','yozadigan / keladigan','jazatig‘an','Muallif kelasi zamon sifatdoshi deb izohlagan.')]:
    observation(form,standard,'Andijon tumanidagi qoraqalpoq kelib chiqishli aholi nutqi','A7',473,anchor,note)
save('GRAMMATIKA.json',grammar)

def normalized(s):
    return re.sub(r'\s+',' ',s).strip()
samples=[]
def sample(source,page,start,meaning,kind,region,note):
    text=texts[source][page-1]
    assert start in text, (source,page,start)
    pos=text.index(start); end=text.index('(<',pos)
    original=text[pos:end].strip()
    # Muallif tarjimasigacha bo‘lgan ayni iqtibos; belgilar tahrirlanmaydi.
    assert original in text
    samples.append({'id':f'AN{len(samples)+1:02}','original_extracted':original,'display':normalized(original),
        'standard_meaning':meaning,'translation_kind':kind,'region':region,'genre':'maqoladagi yozma misol',
        'note':note,'source_refs':[ref(source,page,start)]})
sample('A3',172,'qïzïz dänäk qïz','Qizingiz danak qiz bo‘libdi; yosh bo‘lsa ham gapga chechan.','muallif tarjimasi va izohiga tayangan talqin','Dardoq','Danakning qizcha haqidagi ma’nosi.')
sample('A3',172,'adam\ndegӓn šӓldir-šüldir','Odam sodda, kirishimli bo‘lishi, dimog‘dor bo‘lib kek saqlamasligi kerak.','tahririy mazmuniy talqin','Dardoq','Muallif tarjimasi yonida bor; shaldir-shuldirning ijobiy tusi.')
sample('A3',174,'Bӓrčin jerdi kinnigini','Barchin tinmay mehnat qiladigan ayol; issiqxona va dehqonchilik qilib besh qizini uzatgan.','tahririy mazmuniy talqin','Dardoq','Jerdi kinnigini uzmoq iborasi; oddiy literal gap emas.')
sample('A7',330,'Bü toqsї tāvāqta','Bu to‘qsi tovoqda bodom kam ekan, qo‘shib qo‘yinglar.','muallif tarjimasi; ko‘rsatish shakli saqlandi',SE,'Muallif tarjimasida taksi deb yozilgan; buyumning nomi to‘qsi tovoq, transport taksisi emas.')
sample('A7',331,'Nān pӧpӓnӓk bāsmästän','Nonni mog‘or bosmasidan oldin quyoshga yoyib quritib qo‘y.','tahririy mazmuniy talqin',SE,'Non saqlash haqidagi maqola gapi.')
samples.append({'id':f'AN{len(samples)+1:02}','original_extracted':'Bugun kečka\nsolli šävlä qilärkämmiz enäm äjtti.',
    'display':'Bugun kečka solli šävlä qilärkämmiz enäm äjtti.', 'standard_meaning':'Bugun kechga suvi ko‘proq shavla qilar ekanmiz, onam aytdi.',
    'translation_kind':'tahririy mazmuniy talqin','region':SE,'genre':'maqoladagi yozma misol',
    'note':'So‘lning suvliroq ovqat ma’nosi, qovurilgan go‘sht ma’nosi emas.', 'source_refs':[ref('A7',329,'solli šävlä')]})
samples.append({'id':f'AN{len(samples)+1:02}','original_extracted':'go: undey, go: bundey',
    'standard_meaning':'goh unday, goh bunday','translation_kind':'muallif tarjimasi','region':'Dardoq',
    'genre':'maqoladagi yozma misol','source_refs':[ref('A3',76,'go: undey, go: bundey')]})
samples.append({'id':f'AN{len(samples)+1:02}','original_extracted':'Yo‘q, buvi, siz nimanidir yashirayapsiz?',
    'region':'Andijon deb talqin qilingan badiiy personaj nutqi','genre':'U. Hamdam asaridan ikkilamchi iqtibos',
    'translation_kind':'talqin ochiq; buvi referentini aniqlash uchun asarning to‘liq konteksti kerak',
    'note':'Dala suhbatining audio yozuvi emas; buvi barcha Andijonda doim ona degan lug‘aviy qoida olinmadi.',
    'source_refs':[ref('A3',194,'Yo‘q, buvi, siz nimanidir')]})
samples.append({'id':f'AN{len(samples)+1:02}','original_extracted':'Toqāčli balä sujgunčik.',
    'region':SE,'genre':'maqol','translation_kind':'ma’no manbada batafsil ochilmagan; tayyor suhbatga qo‘llash belgilanmagan',
    'source_refs':[ref('A7',331,'Toqāčli balä sujgunčik')]})
for s in samples:
    sr=s['source_refs'][0]
    assert normalized(s['original_extracted']) in normalized(texts[sr['source']][sr['pdf_page']-1]),s['id']
save('NUTQ_NAMUNALARI.json',samples)

profiles=[
    {'id':'AP1','region':'Andijon shahar–Shahrixon guruhi','summary':'Qarluq-chigil-uyg‘ur lahjasining Farg‘ona guruhida berilgan.', 'source_refs':[ref('A1',36,'2. Andijon-Shahrixon dialekti'),ref('A2',34,'Andijon-Shahrixon')], 'limit':'Tasnif butun viloyatni bir xil qilmaydi. O‘sh–O‘zgan alohida guruh sifatida ham beriladi.'},
    {'id':'AP2','region':'Dardoq qishlog‘i','summary':'Cho‘ziqlik, eliziya/sinerezis misollari, shaxs sifati so‘zlari va obrazli birikmalar.', 'source_refs':[ref('A3',75,'Dardoq qishlog‘i'),ref('A3',170,'Dardoq qishlog‘i')], 'limit':'Muayyan tuman dalilsiz tayinlanmadi; so‘zlovchilar, audio va yosh kesimidagi to‘liq taqsimot yo‘q.'},
    {'id':'AP3','region':'Janubi-sharqiy Andijon','summary':'Jalaquduq, Xo‘jaobod, Qo‘rg‘ontepa oziq-ovqat, marosim va uy-ro‘zg‘or leksikasi.', 'source_refs':[ref('A7',327,'Andijon viloyatining Jalaquduq')], 'limit':'Har birlik uch tuman va har qishloqda bir xil qo‘llanadi degan da’vo emas.'},
    {'id':'AP4','region':'Shahrixon, Segaza','summary':'Sövzï, sövdogar, Shövkat, Rövshan singari shakllar.', 'source_refs':[ref('A7',477,'Segaza')], 'limit':'Unli qatori haqidagi muallif terminlari chalkash bo‘lishi mumkin; shahar Shahrixonning barcha nutqiga tatbiq qilinmaydi.'},
    {'id':'AP5','region':'Izboskan, Gurkirov MFY','summary':'Tag‘a, yang‘aq, bala shakllari qayd etilgan.', 'source_refs':[ref('A7',477,'Gurkirov')], 'limit':'Izboskanning hammasi shu talaffuzda so‘zlashadi degan dalil emas.'},
    {'id':'AP6','region':'Baliqchi va ayrim qipchoq qishloqlari','summary':'-di kelishik shakllari, xo‘pitmoq/hayat/malda, turli darajadagi j-lashish qaydlari.', 'source_refs':[ref('A7',478,'akamdi kitobi'),ref('A7',33,'Sizada “dj”lashish')], 'limit':'Tumanda y-lovchi Chinobod ham eslatilgan; butun Baliqchi bir xil j-lovchi deb olinmaydi.'},
    {'id':'AP7','region':'Andijon tumanidagi qoraqalpoq kelib chiqishli aholi','summary':'Mahalliy maqolada j-lashish, mag‘an/sag‘an, davom zamon va aniq glossli birliklar.', 'source_refs':[ref('A7',472,'Andijon tumanidagi'),ref('A7',473,'mag‘an (menga)')], 'limit':'Andijon shahar shevasi yoki standart qoraqalpoq tili bilan aynan tenglashtirilmaydi. Qishloqlar ro‘yxati misollarni alohida taqsimlamaydi.'},
    {'id':'AP8','region':'Chegara hududlari va til kontaktlari','summary':'Qirg‘iz va uyg‘ur unsurlari, ichki etnik qatlamlar haqida hududiy sharh.', 'source_refs':[ref('A7',33,'Qirg‘iziston bilan chegaradosh')], 'limit':'O‘sh/Jaloloboddagi et, og‘ay, opay singari misollar Andijonning barcha aholisi nutqi qilib olinmadi; etnik mansublikdan yakka shaxs nutqi taxmin qilinmaydi.'}]
save('HUDUDIY_PROFILLAR.json',profiles)
save('KEYINGI_VODIY_BOSQICHLARI.json',[
    {'source':'A5','title':metadata['A5']['title'],'region':'Farg‘ona, Oltiariq','status':'to‘liq o‘qilgan; Andijon asosiy lug‘atiga qo‘shilmagan','note':'Fonetik jarayon ta’riflarini keyingi bosqichda misollardan alohida tekshirish kerak.'},
    {'source':'A1','pdf_page':39,'region':'Namangan/Uychi','status':'Andijon -yap qiyosiga kontekst','note':'-vat/-ut evolyutsiyasi Namangan misollarini Andijon paradigmasi qilib olishga asos emas.'},
    {'source':'A3','pdf_pages':[96],'region':'Namangan, Mingbuloq','status':'Andijon bilan chegaradoshlikning qidiruv mosligi; Andijon nutqi emas'}])
save('TEKSHIRILADIGAN_DAVOLAR.json',[
    {'claim':'Andijon viloyati bitta bir xil shevada gapiradi.','status':'manbalarning hududiy tafovutlari bilan mos kelmaydi','source_refs':[ref('A7',478,'so‘kichak'),ref('A7',33,'Chinobod')]},
    {'claim':'A4ning 1971-yil lug‘atida Jizzax birliklari yo‘q degan gapini qabul qilish.','status':'oldingi tekshirilgan Jizzax/Forish/Zomin qaydlariga zid','source_refs':[ref('A4',2,'Jizzax va Navoiy')],'cross_reference':'../jizzax/LUGAT.json; E1 manbasi'},
    {'claim':'A5dagi barcha fonetik misollar Andijonniki.','status':'noto‘g‘ri hududga biriktirish; Oltiariq maqolasi','source_refs':[ref('A5',1,'OLTIARIQ')]},
    {'claim':'A9 Iqon maqolasining misollari Andijon nutqidir.','status':'Andijon bibliografiya va nazariy iqtibosda; mustaqil mahalliy dalil emas','source_refs':[ref('A9',55,'Андижон шеваси')]},
    {'claim':'Dardoq maqolasidagi cho‘ziqlikning barcha tarixiy tasniflari bir xil qat’iy.','status':'aniqlashtirish kerak: birlamchi/ikkilamchi/emfatik atamalari va o‘zlashma misollari aralash','source_refs':[ref('A3',74,'birlamchi turkiy cho‘ziq')],'handling':'Kuzatilgan shakl saqlanadi, tarixiy kelib chiqishi va cho‘ziqlik sababi mustaqil isbotlangan deyilmaydi.'},
    {'claim':'A6dagi evere/arava juftligidan undosh metatezasi chiqarish.','status':'juftlikda undoshlar o‘rni almashinishi ko‘rsatilmagan','source_refs':[ref('A6',83,'evere (Andijon)')]},
    {'claim':'Dardoqdagi juda- fe’li doim kuchaytiruvchi juda ravishidir.','status':'bu manbada judadim ishlarga ulgurolmaslik ma’nosida','source_refs':[ref('A3',172,'ishlarga ulgurmaslik')]},
    {'claim':'Nasvi etimologiyasi va push/pusht izohi qat’iy isbotlangan.','status':'muallif taxmini yoki talqini; qo‘shimcha dalil kerak','source_refs':[ref('A7',330,'Taxminimizcha'),ref('A7',330,'pusht so‘zining')]},
    {'claim':'Jezda maqolasidagi gloss berilmagan barcha shakllarga ma’no yasash.','status':'qabul qilinmaydi; anna, checha, toptora va boshqalar ma’nosiz sanalgan','source_refs':[ref('A7',473,'toptora, anna')]},
    {'claim':'Badiiy dialogdagi buvi Andijonning barcha nutqida doim ona degani.','status':'to‘liq badiiy kontekst va alohida lug‘aviy qayd kerak','source_refs':[ref('A3',194,'Yo‘q, buvi')]},
    {'claim':'Qoqirim yoki Dardoqdagi ovqat berish misoli tibbiy ko‘rsatmadir.','status':'lingvistik manbadagi gap; davolash samarasi tekshirilmagan','source_refs':[ref('A7',328,'(qoqirim)'),ref('A3',171,'pechal,')]},
    {'claim':'Barcha katta konferensiya to‘plamlari to‘liq o‘qildi yoki barcha 2024 qaydlar 2026 og‘zaki nutqida tasdiqlandi.','status':'bunday da’vo yo‘q; tegishli maqolalar o‘qildi, mustaqil audio tekshiruvi o‘tkazilmadi'}])
save('OLDINGI_HUDUDLAR_QIYOS.json',{
    'duplicates':[{ 'current':x['id'],'previous':x.get('duplicate_of',[]),'sha256':x['sha256']} for x in manifest if x.get('duplicate_of')],
    'semantic_comparisons':[
        {'form':'bulamiq','andijon':'Unni sariyog‘da qovurib sut bilan qaynatilgan taom','jizzax_comparison_in_article':'Tuxum va unni atalashdan olingan aralashma','source_refs':[ref('A7',328,'(bulamiq)')]},
        {'form':'doxsu / obdish / objo‘sh','relation':'Qaynatilgan suv haqida hududlararo qiyos; bitta talaffuz andozasi emas','source_refs':[ref('A7',332,'(doxsu)')]},
        {'form':'chuli / g‘o‘lin','relation':'Turshak ichimligi; Andijon va Buxoro/Navoiy qiyosi','source_refs':[ref('A7',332,'(chuli)')]}],
    'notation':'j harfi va maxsus fonetik belgilar turli manbalarda bir xil kod deb olinmaydi; asliy transkripsiya bilan display farqlanadi.'})
stats={'uploaded_pdf_pages_indexed':sum(x['pages'] for x in manifest),'uploaded_files':len(manifest),
    'regional_articles_read':len(articles),'lexicon_entries':len(lexicon),'idiom_and_process_expressions':len(idioms),
    'contextual_grammar_observations':len(grammar),'speech_samples_including_literary_and_proverb':len(samples)}
save('HISOBOT_STATISTIKASI.json',stats)
assert stats['uploaded_pdf_pages_indexed']==1855
print(json.dumps(stats,ensure_ascii=False))
