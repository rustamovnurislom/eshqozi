"""Toshkent ko‘cha uslubi: foydalanuvchi so‘zlari, manbali kontekst va ijodiy takliflar alohida."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).parent
BASE=ROOT.parent/'toshkent'

def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def norm(s):return re.sub(r'\s+',' ',s).strip()

def local_ref(source,page,needle):
    path=BASE/(source+'.txt') if source!='Q4' else ROOT.parent/'qashqadaryo/Q4.txt'
    text=norm(path.read_text().split('\f')[page-1]);q=norm(needle)
    assert q in text,(source,page,needle)
    i=text.index(q)
    return {'source_id':source,'pdf_page':page,'anchor':text[max(0,i-70):i+len(q)+180],
            'source_text_path':str(path),'claim_scope':'Faqat ko‘rsatilgan grammatik, nazariy yoki lug‘aviy mazmun; zamonaviy Toshkent ko‘cha chastotasi emas.'}

refs={
 'register':local_ref('T1',55,'jargon va argolardan farqlash'),
 'definition':local_ref('T1',56,'Jargon [slang]'),
 'present':local_ref('T1',47,'борвоссэн'),
 'plural':local_ref('T4',167,'д э д э м л э'),
 'social':local_ref('T4',174,'назар-писанд'),
 'bratishka_gloss':local_ref('Q4',355,'братишка'),
 'koki':local_ref('T1',55,"ko'ki"),
 'otar':local_ref('T1',55,'otar'),
 'yakan':local_ref('T1',55,'yakan'),
 'historical_bias':local_ref('T4',57,'тубанликка')}

entries=[]
def add(form,variants,meaning,function,example,note,provenance='user_seed',level='norasmiy',source_refs=None):
    row={'id':'SK-'+str(len(entries)+1).zfill(3),'form':form,'variants':variants,
         'meaning_uz':meaning,'conversation_function':function,'constructed_example':example,
         'example_origin':'assistant_constructed_not_corpus_quote','notes':note,'register':level,
         'provenance':provenance,'refs':source_refs or [],
         'meaning_is_analyst_interpretation':True,
         'modern_tashkent_usage_verified':False,'regional_exclusivity_verified':False,
         'telegram_observation':False,'frequency_measured':False,'audio_verified':False}
    entries.append(row)

# Aynan foydalanuvchi keltirgan o‘n bir birlik. Ma’nolari tahlilchining izohi.
seeds=[
 ('Bratan',['bratan','братан'],'yaqin oshna yoki sherikka norasmiy murojaat','yaqinlik','Bratan, tinchmi? Kechga nima plan?','Haqiqiy aka-uka ekanini anglatishi shart emas. Har gapda takrorlanmasin.'),
 ('Bratishka',['bratishka','братишка'],'yaqinlik/erkalash tusidagi aka-uka yoki oshnaga murojaat','murojaat','Bratishka, otdushi, vaqtida aytding.','1971 lug‘atida bu so‘z ukaning ruscha tarjima-izohi sifatida bor; ruscha o‘zlashma Toshkentda ishlatilgani dalili emas.'),
 ('Rodnoy',['rodnoy','радной','родной'],'yaqinim, qadrdonim ma’nosidagi iliq norasmiy murojaat','murojaat','Rodnoy, bugun ko‘rinmading-ku. Tinchmi?','Qarindoshlikni majburiy bildirmaydi; kinoyada tus o‘zgarishi mumkin.'),
 ('Kotta bola',['kotta bola','katta bola'],'kattaroq/tajribali yoki o‘zini nufuzli tutayotgan kishiga ishora; ba’zan hazil','ijtimoiy rol yoki kinoya','Ha, kotta bola, endi vaqt topildimi?','Yosh ma’nosi ham bor. Avtomatik ravishda jinoyatchi, boshliq yoki boy degani emas.'),
 ('Otdushi',['otdushi','ot dushi','от души'],'chin dildan; samimiy rahmat yoki ma’qullash','minnatdorlik va kuchaytirish','Otdushi, brat, ishni yengillatding.','Bir vaziyatda rahmat, boshqasida ishni jon-dildan qilish ma’nosi; bir xil tarjima yetmaydi.'),
 ('Seryozniy',['seryozniy','seryozni','серьёзный'],'jiddiy; salmoqli; hazil bo‘lmagan','baholash','Bu seryozniy tema, hazilga olma.','Oddiy ruscha sifat ham; har ishlatilishi slang bo‘lavermaydi.'),
 ('Tupik',['tupik','тупик'],'berk ko‘cha; ko‘chma ma’noda yechimsiz yoki yo‘lsiz holat','joy yoki muammo tavsifi','Bu variant tupik, boshqa yo‘lini ko‘ramiz.','To‘g‘ri va ko‘chma ma’no ajratilsin; doimo ko‘cha jargoni emas.'),
 ('Dvijeniya',['dvijeniya','dvijenie','dvij','движение','движ'],'harakat, faollik, rejalar, yig‘ilish yoki davra','reja va faoliyat','Kechga nima dvijeniya? Bolla yig‘ilvotti.','Qaysi harakat yoki davra ekani kontekstdan; maxsus noqonuniy ish degan ma’no yuklanmaydi.'),
 ('Kidat qilmoq',['kidat qilish','kidat qilmoq','кидать'],'aldash, kelishuvni buzish, va’daga turmaslik yoki sherikni yarim yo‘lda qoldirish','ishonch va kelishuv','Kelaman deb kidat qima, plan o‘zgarayotgan bo‘lsa ayt.','Pul bilan aldash va kelmay qo‘yish bir xil vaziyat emas; obyekt va kontekst saqlansin.'),
 ('Zashshita qilish',['zashshita qilish','zashita qilish','защита'],'himoya qilish; tarafini olish','himoya va yordam','Rodnoy, faktni ayt, kim haq bo‘lsa o‘shani zashshita qilamiz.','Diplom himoyasi yoki sport himoyasi alohida ma’no. Taraf olish tahdid qilishga teng emas.'),
 ('Vapshe',['vapshe','vobshche','voobshe','вообще'],'umuman; kuchli ta’kid, hayrat yoki baholash','ta’kid','Bu vapshe boshqa tema ekan-ku.','Vapshe bilmayman va vapshe zo‘r vaziyatlari boshqa; butun gapga qarab izohlanadi.')]
for row in seeds:
    add(*row,source_refs=[refs['bratishka_gloss']] if row[0]=='Bratishka' else [])

# Bular ruscha/o‘zbekcha so‘zlashuv haqidagi umumiy bilimdan ijodiy nomzodlar.
# Yangi tashqi manbada yoki foydalanuvchi bergan chatda tasdiqlangan deb ko‘rsatilmaydi.
candidates=[
 ('Brat',['brat','брат'],'oshna, birodar deb yaqin murojaat','murojaat','Brat, gapni ochiq ayt.','Bratan bilan bir oiladagi murojaat; real chat chastotasi yo‘q.'),
 ('Malades',['malades','molodes','molodets','молодец'],'barakalla, qoyil','maqtov','Malades, ishni vaqtida bitiribsan.','Ohangga qarab kinoya ham bo‘lishi mumkin.'),
 ('Krasavchik',['krasavchik','красавчик'],'qoyil, zo‘r ish qilgan odam; aslida kelishgan yigit','maqtov','Krasavchik, otdushi, hammasini joyiga qo‘yibsan.','Asl tashqi ko‘rinish ma’nosi bilan ko‘chma maqtov ajratiladi.'),
 ('Chotki',['chotki','chotkiy','chetki','чёткий'],'aniq, puxta, zo‘r','baholash','Plan chotki, endi vaqtini kelishamiz.','Taklif etilgan yozuvlar; qaysi variant mahalliyroq ekani tekshirilmagan.'),
 ('Realniy',['realniy','realni','реальный'],'haqiqiy, amalda bor; ishonchli yoki jiddiy','baholash','Realniy gap bo‘lsa ayt, taxminni keyin ko‘ramiz.','Fakt ma’nosi bilan maqtov ma’nosi bir emas.'),
 ('Krutoy',['krutoy','крутой'],'zo‘r, ta’sirli, nufuzli','baholash','Krutoy chiqibdi, gap yo‘q.','Nufuzli deyish har doim hurmat yoki jinoyat maqomini bildirmaydi.'),
 ('Jostki',['jostki','jostkiy','жёсткий'],'qattiq, og‘ir, keskin; ba’zan juda kuchli','baholash','Bugungi kun jostki bo‘ldi, endi dam olamiz.','Ijobiy yoki salbiy tus kontekstga bog‘liq.'),
 ('Bez bazara',['bez bazara','без базара'],'e’tirozsiz, albatta, kelishdik','rozilik','Bez bazara, o‘sha vaqtda boraman.','Umumiy ruscha ko‘cha iborasi nomzodi; Toshkentga mutlaq xos emas.'),
 ('Bazar yo‘q',["bazar yo‘q","bazar yoq"],'gap yo‘q; kelishdik yoki yaxshi ekan','rozilik yoki maqtov','Bazar yo‘q, plan shu bo‘lsin.','Bozor yo‘qligi ma’nosi bilan aralashtirilmaydi.'),
 ('Bazar qilma',['bazar qilma','bazar qima'],'ortiqcha gapirma, bahslashma degan keskin ibora','keskin e’tiroz','Bazar qima, oldin faktni ko‘raylik.','Buyruq tusidagi ibora; oddiy savolga asossiz javob bo‘lib ketmasin.'),
 ('Po faktu',['po faktu','по факту'],'amalda, faktga ko‘ra, gapning asl holati','aniqlashtirish','Po faktu, vaqtimiz yetmayapti.','Slang ifoda faktni o‘z-o‘zidan tasdiqlamaydi.'),
 ('Po lyubomu',['po lyubomu','по-любому'],'baribir, qanday bo‘lsa ham, aniq','ishonch yoki zarurat','Po lyubomu bugun kelishib olishimiz kerak.','Ishonch ifodasi dalil o‘rniga qo‘yilmaydi.'),
 ('Karoche',['karoche','koroche','короче'],'qisqasi; gapni umumlashtirish yoki yangi nuqtaga o‘tish','diskurs bog‘lovchi','Karoche, ikki variant bor.','Har gap boshida takrorlansa uslub sun’iylashadi.'),
 ('Tema',['tema','тема'],'mavzu, masala, taklif yoki ma’qul variant','mavzu va baholash','Bu tema ekan, ko‘rib chiqamiz.','Yashirin/taqiqlangan ish ma’nosi avtomatik yuklanmaydi.'),
 ('Tusovka',['tusovka','тусовка'],'yig‘ilish, davra, do‘stlar bilan vaqt o‘tkazish','ijtimoiy faoliyat','Tusovka keyin, oldin ishni tugataylik.','Yig‘ilish turi kontekst bilan aniqlanadi.'),
 ('Pont',['pont','понт'],'o‘zini ko‘rsatish, ko‘z-ko‘z qilish','ijtimoiy baholash','Gapda pont ko‘p, natijani ham ko‘raylik.','Avtomatik shaxsni haqorat qilish o‘rniga xatti-harakatga bog‘lansin.'),
 ('Pont qilmoq',['pont qilish','pont qilmoq'],'o‘zini ko‘rsatish yoki ortiqcha kerilish','ijtimoiy baholash','Pont qima, bilmasang ochiq ayt.','Keskin murojaat; barcha foydalanuvchilarga birday qo‘llanmaydi.'),
 ('Prikol',['prikol','прикол'],'hazil, kulgili yoki qiziq holat','hazil va hayrat','Prikolni qara, ikkovimiz bir xil plan qilibmiz.','Hazil va qiziq vaziyat ma’nolari farqlanadi.'),
 ('Oblom',['oblom','облом'],'rejaning o‘xshamasligi, hafsalani pir qilgan natija','salbiy natija','Joy band ekan, oblom bo‘ldi.','Oddiy rad javobini hujumdek talqin qilmaslik kerak.'),
 ('Razbor',['razbor','разбор'],'masalani aniqlash, muhokama; kontekstda hisob-kitob yoki tortishuv','muammoni hal qilish','Razborni gap bilan qilamiz, nima bo‘lganini ayt.','Tortishuv ma’nosi mumkin; ko‘rib chiqish ham bo‘lishi mumkin.'),
 ('Otvet',['otvet','ответ'],'javob; vaziyatda mas’uliyat yoki javob qaytarish','javob va mas’uliyat','Savolga otvet bor, hozir tushuntiraman.','Har holatda tahdid ma’nosiga aylantirilmaydi.'),
 ('Bomba',['bomba','бомба'],'juda zo‘r, kuchli taassurot qoldiradigan','maqtov','Natija bomba chiqibdi.','Bu namunada ko‘chma maqtov; asl predmet ma’nosi alohida.'),
 ('Top',['top','топ'],'juda yaxshi, yuqori darajadagi','maqtov','Shu variant top, shundan boshlaymiz.','Umumiy internet so‘zlashuvi; maxsus Toshkent belgisi emas.'),
 ('Kayf',['kayf','кайф'],'rohat, yaxshi hissiyot; zo‘r degan baho','hissiy baholash','Ish bitdi, endi kayf qilib dam olamiz.','Rohatni doimo mastlik bilan tenglashtirish noto‘g‘ri.'),
 ('Prosta',['prosta','prosto','просто'],'shunchaki, oddiygina; ta’kid','izoh va ta’kid','Prosta vaqti mos kelmadi, boshqa kuni qilamiz.','Ba’zan oddiy ruscha so‘z; hamma hollarda slang emas.')]
for row in candidates:add(*row,provenance='analyst_candidate_not_verified')

for form,meaning,function,example,key,note in [
 ('Ko‘ki','dollar o‘rnida ishlatilgan savdogarlar jargoni','pul haqida',"Ko‘kida aytyapsanmi yoki so‘mda?",'koki','Ashirboyev ijtimoiy jargon misoli sifatida beradi; Toshkent ko‘cha nutqining bugungi chastotasi tasdiqlanmagan.'),
 ('Yakan','pul o‘rnida ishlatilgan jargon','pul haqida','Yakan masalasini oldindan kelishaylik.','yakan','Kitob yallachilar kontekstida beradi; umumiy Toshkent so‘zi deb belgilanmaydi.'),
 ('Otar','to‘y o‘rnida qo‘llangan yallachilar jargoni','kasbiy tadbir','Otar haqida gapiryapsanmi, oddiy uchrashuvmi?','otar','Kitobdagi ma’no; zamonaviy ijrochilar ishlatishiga alohida dalil kerak.')]:
    add(form,[],meaning,function,example,note,provenance='pdf_social_jargon_not_tashkent_specific',source_refs=[refs[key]])

# "Undanam battar" so‘roviga qo‘pol hissiy qatlam. Bular ham manbada tasdiqlangan deb ko‘rsatilmaydi.
for row in [
 ('Blya',['blya','бля'],'qo‘pol hissiy undov; norozilik/hayrat','hissiy undov','Blya, kalitni yana uyda qoldiribman.','Bu namunada o‘z holatiga undov; suhbatdoshga haqorat emas.'),
 ('Pizdes',['pizdes','pizdets','пиздец'],'o‘ta keskin holat, katta muammo yoki kuchli hayratni ifodalovchi qo‘pol undov','hissiy kuchaytirish','Bugungi tirbandlik pizdes ekan.','Ijobiy hayrat ma’nosi ham bo‘lishi mumkin; juda qo‘pol.'),
 ('Zayebis',['zayebis','заебись'],'juda yaxshi/zo‘r ma’nosidagi qo‘pol baho','maqtov','Zayebis, plan o‘xshadi.','Oddiy hurmatli suhbatga ko‘chirilmaydi; juda qo‘pol.')]:
    add(*row,provenance='analyst_candidate_not_verified',level='qo‘pol')

write('SLANG_LUGAT.json',entries)
with (ROOT/'SLANG_LUGAT.csv').open('w',newline='') as f:
    fields=['id','form','meaning_uz','conversation_function','register','provenance','constructed_example','notes','modern_tashkent_usage_verified']
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(entries)

source_manifest=json.loads((BASE/'MANBALAR.json').read_text())['uploaded_sources']
qm=json.loads((ROOT.parent/'qashqadaryo/MANBALAR.json').read_text())
q4=next(x for x in qm if x['id']=='Q4')
checked=[]
for s in [next(x for x in source_manifest if x['id']=='T1'),next(x for x in source_manifest if x['id']=='T4'),q4]:
    path=s.get('pdf_path',s.get('path'))
    sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if s.get('sha256'):assert sha==s['sha256']
    checked.append({'id':s['id'],'title':s['title'],'year':s['year'],'pdf_path':path,'sha256':sha,
                    'modern_street_slang_corpus':False})
write('MANBALAR.json',{
 'checked_existing_pdfs':checked,'checked_page_refs':refs,
 'user_seed':{'count':len(seeds),'description':'Shu suhbatdagi foydalanuvchi keltirgan so‘zlar; chat korpusidan olingan dalil emas.'},
 'telegram_url':'https://t.me/Tashkent_Chat_Go','telegram_content_read':False,
 'new_external_sources_read':0,
 'network_permission_requested_and_granted':True,
 'network_result':'Proxy CONNECT 403 Forbidden; to‘g‘ridan-to‘g‘ri ulanishda DNS Temporary failure in name resolution.',
 'network_log':str(ROOT/'NETWORK_PROBES.json'),
 'modern_tashkent_slang_evidence':'Hozircha mustaqil tasdiqlanmagan. Umumiy ruscha slang ma’nosi Toshkentka xosligini yoki foydalanish chastotasini isbotlamaydi.'})

examples=[
 ('uchrashuv','Bratan, tinchmi? Kechga nima dvijeniya? Bolla yig‘ilvotti, senam chiqasanmi?'),
 ('rejani aniqlashtirish','Rodnoy, karoche, plan shunaqa: oldin ishni bitiramiz, keyin chiqamiz. Bez bazara?'),
 ('rahmat','Krasavchik, bratishka. Otdushi, vaqtida aytding, ishni vapshe yengillatding.'),
 ('va’daga turish','Bratan, kelaman deb kidat qima. Plan o‘zgarsa, hozirdan ayt, bolla bekorga kutmasin.'),
 ('tanlash','Bu variant tupik ekan. Po faktu, boshqa yo‘l bor — shuni ko‘raylik.'),
 ('jiddiy masala','Rodnoy, bu seryozniy tema. Hazil keyin, hozir kim nima qilayotganini aniq kelishamiz.'),
 ('xato qilganida','Brat, bu joyini adashtiribman. Hozir to‘g‘rilayman, pont qilib o‘tirmayman.'),
 ('o‘zini tutgan bahs','Bazar qima, brat. Avval nima bo‘lganini ayt — po faktu gaplashamiz.'),
 ('yordam','Rodnoy, nimaga tiqilib qolding? Qaysi joyi ishlamayapti, tashavor, ko‘rib chiqamiz.'),
 ('maqtov','Malades, ish chotki chiqibdi. Otdushi, ortiqcha gap yo‘q.'),
 ('qo‘pol hissiy qatlam','Blya, yana kech qolibman. Bratan, o‘n minutda yetaman, kutib tur.')]
write('KREATIV_NAMUNALAR.json',[{'id':'KN-'+str(i).zfill(2),'scenario':scenario,'text':text,
 'provenance':'assistant_constructed','authentic_chat_quote':False,'modern_usage_verified':False,
 'raw':scenario=='qo‘pol hissiy qatlam'} for i,(scenario,text) in enumerate(examples,1)])

prompt='''Sen Eshqo‘zi botining “Toshkent ko‘cha” uslubida javob yozasan. Bu tanlangan ijodiy uslub; barcha Toshkentliklar shunday gapiradi deb aytma.
O‘zbekcha mazmunni tushunarli saqla. Norasmiy, qisqa, jonli gapir. Vaziyatga mos bratan, bratishka, rodnoy; otdushi, vapshe, seryozniy, dvijeniya, kidat qilish kabi birliklarni ishlat.
Kuchli rejimda slang sezilarli bo‘lsin, lekin har so‘zni ruscha qilma. Har gapni bratan bilan boshlama. Murojaat, ta’kid va mavzu so‘zlarini aylantirib ishlat.
Ma’noni shaxs, zamon, yo‘nalish va inkordan ajratma. Men boryapman / sen boryapsan / u boryapti bir xil “borvotti” emas. Qayerga kelyapsan mazmunini qayerga ketyapsan qilib o‘zgartirma.
“-la” har doim ko‘plik emas; hurmat bo‘lishi mumkin. Foydalanuvchi sizlasa, sizlab javob ber. “Kotta bola”ni barcha kishining maqomi deb taxmin qilma.
Kidat qilish, tupik, zashshita, vapshe ma’nosini kontekstdan tanla. Ko‘chma so‘zni har doim to‘g‘ri ma’noda olma. Shaxs nomi, son, sana, kod, URL va muhim faktlarni buzma.
Ko‘cha uslubi uchun noto‘g‘ri fakt, keraksiz po‘pisa yoki foydalanuvchiga tegish shart emas. Bilmasang ochiq ayt. Kerak bo‘lsa aniq va batafsil tushuntir; slang sabab ma’no yo‘qolmasin.
Raw rejimda vaziyatga mos qo‘pol hissiy undov mumkin; uni har gapga qo‘shma va oddiy savol bergan odamga haqorat qilma.
Bu profildagi kreativ namunalarni Telegramdan olingan haqiqiy sitata deb ko‘rsatma. Manba so‘ralsa foydalanuvchi bergan so‘z, PDF konteksti va tekshirilmagan taklifni farqla. Chatni o‘qidim, audio bilan tekshirdim yoki modelni o‘qitdim deb yolg‘on aytma.
'''
(ROOT/'BOT_USLUB_PROMPTI.txt').write_text(prompt)
write('USLUB_PROFILI.json',{
 'id':'toshkent_kocha','display_name':'Toshkent ko‘cha','version':'0.1-creative-draft',
 'base_region_profile':str(BASE/'HUDUDIY_PROFILLAR.json'),
 'type':'Toshkent shahar grammatikasi + ruscha/o‘zbekcha norasmiy slangdan ijodiy uslub',
 'real_chat_calibrated':False,'default_intensity':'kuchli',
 'levels':{'kuchli':'Ko‘p seziladigan slang, qisqa va norasmiy nutq, mat talab qilinmaydi.',
           'raw':'Kuchli uslubga qo‘pol hissiy undovlar ham qo‘shilishi mumkin; har gapga majburiy emas.'},
 'register_behavior':{'friend_chat':'senlash va yaqin murojaat mumkin','user_uses_siz':'sizlash saqlanadi',
                      'technical_or_serious':'slang qisqarishi mumkin; aniqlik va to‘liqlik saqlanadi'},
 'address_rotation':['bratan','bratishka','rodnoy','brat'],
 'grammar_refs':[refs['present'],refs['plural'],refs['social']],
 'lexicon_path':str(ROOT/'SLANG_LUGAT.json'),'prompt_path':str(ROOT/'BOT_USLUB_PROMPTI.txt'),
 'examples_path':str(ROOT/'KREATIV_NAMUNALAR.json'),
 'training_performed':False,'bot_runtime_modified':False,
 'next_required_evidence':'Telegram eksporti yoki foydalanish mumkin bo‘lgan ochiq korpus; haqiqiy matn, sana va kontekst bilan tekshirish.'})

leads=[
 {'kind':'user_provided_telegram','url':'https://t.me/Tashkent_Chat_Go','status':'network_blocked_not_read'},
 {'kind':'public_preview_attempt','url':'https://t.me/s/Tashkent_Chat_Go','status':'network_blocked_not_read'},
 {'kind':'search_query','query':'Toshkent kocha slang bratan rodnoy otdushi','status':'search_blocked_no_results_read'},
 {'kind':'search_query','query':'ташкентский сленг словарь','status':'search_blocked_no_results_read'},
 {'kind':'next_query','query':'Ташкент узбекско русский молодёжный сленг переключение кодов','status':'not_run'},
 {'kind':'next_query','query':'Uzbek youth slang Russian Uzbek code switching Tashkent','status':'not_run'}]
write('QIDIRUV_YONALISHLARI.json',leads)

stats={'total_lexicon_entries':len(entries),'user_seed_entries':len(seeds),
 'analyst_candidate_entries':len(candidates)+3,'pdf_general_jargon_entries':3,
 'creative_examples':len(examples),'verified_modern_tashkent_slang_entries':0,
 'external_pages_read':0,'existing_pdf_sources_checked':len(checked),'source_anchors_checked':len(refs)}
write('HISOBOT_STATISTIKASI.json',stats)
assert len(entries)==42 and len({x['id'] for x in entries})==42
assert all(not x['telegram_observation'] for x in entries)
assert all(not x['modern_tashkent_usage_verified'] for x in entries)
assert len(seeds)==11
write('TEKSHIRUV_NATIJASI.json',{'local_source_anchors_checked':len(refs),'pdf_hashes_checked':len(checked),
 'provenance_and_verification_flags_checked':len(entries),'user_examples_preserved':len(seeds),
 'authentic_telegram_messages_read':0,'status':'Ijodiy loyiha tekshirildi; yangi internet manbalari bloklangan.'})
print(json.dumps(stats,ensure_ascii=False,indent=2))
