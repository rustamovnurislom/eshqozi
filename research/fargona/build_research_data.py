import json, re, hashlib
from pathlib import Path

ROOT = Path('/workspace/research/fargona')
SOURCES = json.loads((ROOT/'download_manifest.json').read_text())
PAGES = {s['id']:(ROOT/(s['id']+'.txt')).read_text().split('\f') for s in SOURCES}

def save(name, value):
    (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def ref(source, page, anchor):
    text = PAGES[source][page-1]
    assert anchor in text, (source, page, anchor)
    pos = text.index(anchor)
    printed = {'F1':page-1,'F2':page,'F5':page+24,'F7':page+146,'F8':page}.get(source)
    return {'source':source,'pdf_page':page,'printed_page':printed,
            'anchor_extracted':anchor,
            'evidence_extracted':text[max(0,pos-100):min(len(text),pos+len(anchor)+340)],
            'extraction':'PDF matn qatlami; asl sahifa alohida tekshiriladi'}

def common():
    return {'exclusive_to_region':None,'independent_modern_usage_verified':False,
            'audio_verified':False,'model_training_performed':False}

bibliography = [
 ('F1','Samixon Ashirboyev','O‘zbek dialektologiyasi',2016,'Navro‘z, Toshkent','darslik',
  '139 PDF sahifa; bibliografiyada 136 bet. Qashqadaryo va Samarqand bosqichlaridagi fayl bilan bir xil.'),
 ('F2','Sh. Xudoyqulova','O‘zbek dialektologiyasi fanidan o‘quv-uslubiy majmua',2008,'Guliston davlat universiteti','o‘quv majmua',
  'Avvalgi hududlarda ishlatilgan 5b015f0357f16.pdf bilan bir xil; mustaqil yangi dalil emas.'),
 ('F3','Yoqub Saidov','O‘zbek dialektologiyasi (to‘ldirilgan va qayta nashri)',2022,'Durdona / Sadriddin Salim Buxoriy, Buxoro','o‘quv qo‘llanma',
  '96 PDF sahifa; katalog matnidagi 74 bet raqami bilan farq bor. Shu sabab PDF sahifasi asosiy ko‘rsatkich. Jizzaxdagi nusxa bilan bir xil.'),
 ('F4','G. Jo‘raboyeva; M. Tursunboyeva','Farg‘ona (Oltiariq) guruhi shevalarining fonetik tahliliga doir',None,None,'fonetik maqola',
  'Nashr sanasi va individual respondentlar berilmagan. Andijon A5 bilan bir xil; Oltiariq materiali shu yerga tegishli.'),
 ('F5','Mavjudboyeva Mardona Muzaffar qizi','Farg‘ona va Xorazm shevalarida leksik farqlanish xususiyatlari (qiyosiy tahlil)',2026,'Qo‘qon DPI. Ilmiy xabarlar, 8-son, B seriya','qiyosiy maqola',
  'Bosma 25–30-bet. DOI: 10.70728/b.series.fil.v08.i08.004. Muayyan qishloq va respondentlar ko‘rsatilmagan; vodiy va viloyat miqyosi aralashadi.'),
 ('F6','Saidumarova Muxlisaxon Saidazimxon qizi','Farg‘ona viloyati, Uchko‘prik tumani hududi atrof qishloqlar shevasiga oid so‘zlardan to‘plangan ayrim so‘zlar lug‘ati',2025,'Ilmiy tadqiqotlar va ularning yechimlari jurnali, volume 4, issue 02, aprel','mahalliy lug‘at maqolasi',
  'Annotatsiyada Begmurod qishlog‘i qayd etilgan; 10 birlikning qishloqlar bo‘yicha alohida taqsimoti va respondent ma’lumotlari yo‘q.'),
 ('F7','Ahmadova Rohila Nodirjon qizi; ilmiy rahbar I.H. Yoqubov','Farg‘ona shevasining fonetik, morfologik hamda leksik xususuyatlari',None,'Education Science and Innovative Ideas in the World','umumlashtiruvchi maqola',
  'Bosma 147–154-bet. Kolontitulda November va Part 10 1; aniq yil ko‘rsatilmagan. Leksik va grammatik izohlardagi kamchiliklar alohida qayd etildi.'),
 ('F8','Feruza Musayeva','O‘zbek xalq so‘zlari',2023,'Innovatsion rivojlanish nashriyot-matbaa uyi, Toshkent','izohli lug‘at va nazariy kirish',
  '392 PDF sahifa. Lug‘at 54-betdan boshlanadi. Illyustratsiyalar badiiy, ilmiy va publitsistik asarlardan; audio yoki respondent dialogi deb qaralmaydi.')
]
for s,b in zip(SOURCES,bibliography):
    assert s['id']==b[0]
    s.update(author=b[1],title=b[2],year=b[3],publication=b[4],genre=b[5],notes=b[6])

duplicate_map={'F1':[('qashqadaryo','Q3'),('samarqand','M1')],
               'F2':[('qashqadaryo','Q2'),('samarqand','M2'),('jizzax','J2'),('andijon','A2')],
               'F3':[('jizzax','J3')], 'F4':[('andijon','A5')]}
for s in SOURCES:
    s['duplicates']=[{'region':a,'source':b} for a,b in duplicate_map.get(s['id'],[])]
    s['references_online_verified']=False
    s['external_instructions_followed']=False
save('MANBALAR.json',{'uploaded_sources':SOURCES,'source_note':'Bir xil faylning takror yuborilishi mustaqil tasdiq emas.'})

lex=[]
def word(form, meaning, area, source, page, anchor=None, register='maishiy yoki neytral', notes='', status='manbada_qayd_etilgan', extra_refs=()):
    row={'id':f'FL{len(lex)+1:03}','form_source':form,'meaning_uz':meaning,'area':area,
         'register':register,'evidence_status':status,'notes':notes,
         'refs':[ref(source,page,anchor or form)]+list(extra_refs), **common()}
    lex.append(row); return row

local=[
 ('Paynob','Dala va uylardagi ariqlardan suvning chiqib ketish joyi.','suv taqsimoti','Ta’rif chiqishni, misol suv kelishini aytadi; chiqish/kirish yo‘nalishi kontekstda tekshiriladi.'),
 ('Durra','Ro‘mol.','kiyim-kechak','Katta ro‘mol misoli bor; barcha ro‘mol turi yoki faqat shu qishloqqa xos deb umumlashtirilmaydi.'),
 ('Cherdak','Tom (maqoladagi izoh).','uy-ro‘zg‘or','Adabiy cherdak/chordoq bilan aynanlashtirish uchun qo‘shimcha dalil kerak; o‘rik yoyib quritish konteksti.'),
 ('Otashkurak','Tandir va o‘choqdagi cho‘g‘larni tortib olish asbobi.','pazandachilik','Oddiy dala kuragi bilan tenglashtirilmaydi.'),
 ('Salla','Sallaga o‘xshab o‘ralgan shirinlik turi.','marosim va taom','Bosh kiyim ma’nosidan farq qiladi; qudaziyopa konteksti.'),
 ('Charqi','Quyuq ovqat solish uchun ishlatiladigan idish.','idish-tovoq','Osh solish misoli bor; hajm, material, kosaga/tovoqqa aynan muqobilligi berilmagan.'),
 ('Yelpishtovoq','Temir idish; don mahsulotlarini kurmakdan tozalashda ishlatiladi.','xo‘jalik','Ta’rif dukkakli mahsulot deydi, misol guruchni tozalash haqida. Don tozalash funksiyasi matndan chiqarilgan umumiy izoh.'),
 ('Keli','Mahsulot ezib-maydalash, tolqon qilish uchun ishlatiladigan, ichi o‘yilgan yog‘och buyum.','xo‘jalik','Maqolada tut daraxtidan ishlanishi va mos sopi aytiladi; bu material barcha kelilar uchun shart deb belgilanmaydi.'),
 ('Rumcha','Kamzir, nimcha (manba yozuvi).','kiyim-kechak','Kamzir imlosi asl holicha saqlanadi.'),
 ('Uyqozon','Qozonda chini va to‘rtta cho‘pak ustiga manti idishi joylashtirib pishirish tuzilmasi/usuli.','pazandachilik','Ma’no izohdan chiqarilgan; misolda uyquzun yozilgan. Bir xil talaffuz deb avtomatik birlashtirilmaydi.')
]
for form,meaning,register,note in local:
    word(form,meaning,'Uchko‘prik atrof qishloqlari; Begmurod annotatsiyada','F6',2,register=register,notes=note)

dict_data=[
 ('ALAMAZON',58,'O‘t, olovning gurullab yonishi.','tasviriy; olov', 'Olovning kuchli yonish holati; oddiy olovning har qanday nomi emas.'),
 ('ARRATO‘PON',61,'Qipiq.','xo‘jalik','Lug‘at misolida hayvon yotadigan joyga sepiladi.'),
 ('ARZIQ',62,'Tarkibida ohak, bo‘r bo‘lgan, changsimon oq tuproq.','tuproq va tabiat','Oddiy chang yoki barcha tuproqning muqobili emas.'),
 ('BEDANATUT',68,'Bedona tut.','meva','Tut navi; bedana qushiga oid so‘z deb tushunilmaydi. Botanika tafsiloti mustaqil tekshirilmagan.'),
 ('BEXIT',71,'Xarxashasi kamroq.','so‘zlashuv','Misollarda bexitroq yo‘nalish va joy; faqat insonga xos sifat sifatida cheklanmaydi.'),
 ('BESHLIK',71,'Panshaxa.','xo‘jalik','Son, pul yoki baho ma’nolaridan kontekst orqali ajratiladi.'),
 ('BUVI',81,'Ona.','qarindoshlik','Umumadabiy buvi = ota yoki onaning onasi ma’nosidan farq qiluvchi lokal ma’no; murojaat konteksti zarur.'),
 ('DEPARA',91,'Tuman.','tarixiy yoki hududiy','Tarixiy hudud nomlash; hozirgi rasmiy ma’muriy tuman chegarasi deb olinmaydi.'),
 ('ELCHIMOQ',103,'Ergashmoq.','badiiy va so‘zlashuv','Elchi yuborish ma’nosi emas. Metaforik ergashish misoli ham bor.'),
 ('POYCHO‘KIR',229,'Sodda.','baholovchi','Misollarda kamtar/oddiy odam va sodda deb hisoblash ohangi bor. Foydalanuvchiga o‘z-o‘zidan shu sifat bilan murojaat qilinmaydi.'),
 ('SARIQSO‘FIYON',264,'Sassiq popishak.','qush nomi','Kirishda sassiqpopishakning bir turi deb izohlanadi; zoologik tur darajasi tekshirilmagan.'),
 ('G‘ULG‘ULI',352,'Kurka.','parranda','G‘ulig‘uli va quliquli kirishdagi boshqa yozuvlar; mustaqil variant qaydi sifatida saqlanadi.')
]
for form,page,meaning,register,note in dict_data:
    word(form,meaning,'Farg‘ona (lug‘at belgisi, aniq tuman ko‘rsatilmagan)','F8',page,register=register,notes=note)
lex[16]['refs'].append(ref('F1',54,'Farg‘onada ona'))

intro_words=[
 ('lappak',42,'Sun’iy yo‘ldosh antennasi.','Farg‘ona shevalaridan biri','shakl asosida nomlash',ref('F8',180,'LAPPAK')),
 ('shox-',43,'Shoxilon — shilliqqurt; nom boshidagi o‘simta asosida izohlangan.','Farg‘ona (Farg‘. belgisi)','jonivor nomi',None),
 ('ot ninachi',44,'Katta ko‘k tusli ninachi.','Farg‘ona','hasharot nomi',ref('F8',214,'OT NINACHI')),
 ('vala-va-',48,'Vala-vala — vaysaqi odam.','Qo‘qon','salbiy baholovchi',None),
 ('shapshak',49,'Bezori.','Qo‘qon','salbiy baholovchi',None),
 ('g‘ulig‘uli',49,'Kurka.','Farg‘ona','parranda nomi',None),
 ('quliquli',49,'Kurka.','Farg‘ona','parranda nomi',None)
]
for anchor,page,meaning,area,register,extra in intro_words:
    form={'shox-':'shoxilon','vala-va-':'vala-vala'}.get(anchor,anchor)
    word(form,meaning,area,'F8',page,anchor,register,notes='Kirishdagi qayd; nomning etimologik izohi muallif talqini. Satrdagi bo‘linish alohida tiklangan.',extra_refs=([extra] if extra else []))

book_words=[
 ('buvak','Chaqaloq.','F1',54,'бувэк','Farg‘ona','O‘qishga qulay lotin shakli; asl transkripsiya havolada.',[ref('F2',42,'buvək')]),
 ('shoti','Narvon.','F1',54,'шоть','Farg‘ona','F2 57-betda narvon va arava qismi ma’nolari birga berilgan; kontekst muhim.',[ref('F2',57,'narvon, b)arava qismi')]),
 ('pashsha','Chivin; chaqadigan hasharot.','F2',57,'Farg’ona chivin','Farg‘ona','Toshkentdagi pashsha bilan muqobili bir xil emas.',[ref('F1',54,'chaqadigan hashorat')]),
 ('ayya','Ona.','F3',82,'ayya','Farg‘ona','Buvi bilan yonma-yon variant sifatida berilgan.',[]),
 ('mardak','So‘ta.','F1',61,'мэрдэк','Farg‘ona','Adabiy imloga yaqin ko‘rsatish; manbada o‘simlik turi ochilmagan.',[]),
 ('ko‘kmak','Ko‘kat.','F1',49,'к о к м э к','Andijon va Farg‘ona','-mak affiksli yasalish; o‘qishga qulay shakl, asl transkripsiya saqlanadi.',[]),
 ('misilcha','Musicha.','F3',68,'misilcha','Farg‘ona','F2da m’s’lchə, boshqa jadvalda mъsъəchə; yozuvlar majburan bir shaklga keltirilmaydi.',[ref('F2',55,"m’s’lchə")]),
 ('hayunchak','Arg‘imchoq.','F3',68,'hayunchak','Farg‘ona','Qiyosiy jadval qatori; aniq tuman berilmagan.',[]),
 ('barqit','Baxmal.','F3',68,'barqit','Farg‘ona','F2da Barqt yozuvi; tovush aniqligi tekshirishga muhtoj.',[ref('F2',55,'Barqt')]),
 ('chumalik','Chumoli.','F3',68,'chumalik','Farg‘ona','Qiyosiy jadval materiali.',[]),
 ('g‘ora','Dovuchcha.','F2',55,"g’ora",'Farg‘ona','Qiyosiy jadval; mevaning turi va pishish bosqichi mustaqil aniqlanmagan.',[]),
 ('chikaldak','Qalamcha.','F2',55,"ch’kəldək",'Farg‘ona','Taxminiy o‘qish, asl aralash transkripsiya havolada; tayyor talaffuz qoidasi emas.',[]),
 ('Dj’nqarchə','Chittak ma’nosiga qiyoslangan jadval birligi.','F2',55,"Dj’nqarchə",'Farg‘ona','Toshkent ustunidagi ch’ttey bilan qiyos; zoologik identifikatsiya va soddalashtirilgan lotin o‘qish berilmaydi.',[]),
 ('chimmət','Chachvon/chashpan(t) bilan qiyoslangan yopinchiq.','F2',55,"ch’mmət",'Farg‘ona','Tarixiy kiyim atamasi; buyumlarning mutlaq bir xilligi tasdiqlanmagan.',[]),
 ('kelъ','O‘g‘ir/hovon bilan qiyoslangan birlik.','F2',42,'kelъ','Farg‘ona','Uchko‘prik maqolasidagi Keli izohi ma’noni qo‘llab-quvvatlaydi; transkripsiya va aniq fonetika alohida.',[ref('F6',2,' Keli')])
]
for form,meaning,src,p,anchor,area,note,extras in book_words:
    word(form,meaning,area,src,p,anchor,notes=note,extra_refs=extras)

# Qiyosiy maqoladagi Farg‘ona ustuni. Bular muallif da’vosi sifatida saqlanadi.
candidates=[
 (3,'Amaki, Katta dada, Amak','Otaning akasi/ukasi','Amak'),
 (3,'Tog‘a, Tog‘ay','Onaning akasi/ukasi','Togʻay'),
 (3,'Amma, Ammaki','Otaning opasi/singlisi','Ammaki'),
 (3,'Xola, Xolapo','Onaning opasi/singlisi','Xolapo'),
 (3,'Er, Xo‘jayin, Dadamlar','Ayolning turmush o‘rtog‘i','Dadamlar'),
 (3,'Xotin, Ayol, Kelinchak','Erkakning turmush o‘rtog‘i','Kelinchak'),
 (4,'Patir, Yupqa, Qatlama','Non turlari','Qatlama'),
 (4,'Qovurdoq, Jizza','Qovurilgan yoki dimlangan go‘sht sifatida qiyoslangan','Jizza'),
 (4,'Moshxo‘rda, Moshaba','Moshli suyuq osh sifatida qiyoslangan','Moshaba'),
 (4,'Pichoq, Oshpichoq','Oshpazlik pichog‘i','Oshpichoq'),
 (4,'Qozonqirg‘ich, Qirqich','Qozonni tozalaydigan buyum','Qirqich'),
 (4,'Ayron, Chalop','Qatiq va suv aralashmasi','Chalop'),
 (4,'Rapida, Nonpar','Tandirda non yopish moslamasi deb qiyoslangan','Nonpar'),
 (4,'Dalan, Supa, Ayvon','Hovlidagi eshik oldi ayvoni deb qiyoslangan','Dalan'),
 (5,'Sandiq','Kiyim soladigan sandiq','Sandiq'),
 (5,'Chelak, Paqir','Suv tashiydigan chelak','Chelak'),
 (5,'Supurgi, Sidirg‘ich','Supurgi','Sidirgʻich'),
 (5,'Darvoza, Katta eshik','Hovli darvozasi/eshigi','Katta eshik'),
 (5,'Chiroq, Lampa','Yoritgich','Lampa'),
 (5,'Tog‘ora, Tos','Kir yuvish tog‘orasi','Togʻora'),
 (5,'Pomidor, Lopqa','Pomidor','Lopqa'),
 (5,'Oshqovoq, Qovoq','Oshqovoq','Oshqovoq'),
 (5,'Tarvuz','Tarvuz','Tarvuz'),
 (5,'Xazon, Paxal, Cho‘p','Xazon, cho‘p, mayda shoxlar deb qiyoslangan','Paxal'),
 (5,'Ariq, Shox, Salariq','Kichik suv yo‘li','Salariq'),
 (5,'Baqa, Qurbaqa','Qurbaqa','Qurbaqa'),
 (5,'Molxona, Og‘ilxona','Og‘il/molxona','Ogʻilxona')
]
for p,form,meaning,anchor in candidates:
    word(form,meaning,'Farg‘ona areali; maqolada vodiy/viloyat ajratilmagan','F5',p,anchor,
         notes='Aniq joy, respondent, yig‘ish sanasi va birlik bo‘yicha lug‘at sahifasi berilmagan. Sinxron faol ishlatilishi tekshirilmagan. Guruhlangan birliklar mutlaq sinonim deb olinmaydi.',
         status='muallif_davosi_qoshimcha_tekshiriladi')
save('LUGAT.json',lex)

phon=[]
def phon_group(group, page, pairs, note='', status='manbada_qayd_etilgan', allow_display=True):
    for inp,out in pairs:
        display=None
        if allow_display:
            # Faqat diakritik belgilarni o‘qishga qulaylashtirish; asl shakl asosiy dalil.
            display=out.replace('č','ch').replace('š','sh').replace('â','o').replace('ä','a').replace('ø','o‘').replace('ü','u').replace('ı','i')
        phon.append({'id':f'FP{len(phon)+1:03}','process_group':group,'input_as_source':inp,
                     'form_source':out,'display_approximation':display,
                     'display_note':'Taxminiy o‘qish; IPA yoki audio tasdig‘i emas.' if display else 'Grafema yoki izoh noaniq; taxminiy o‘qish berilmadi.',
                     'area':'Farg‘ona (Oltiariq) guruhi, maqola miqyosi','evidence_status':status,
                     'notes':note,'refs':[ref('F4',2 if out=='düvâl' else page,out)],**common()})

phon_group('so‘z oxiri k/g',2,[('bo‘lak','bøleg'),('terak','tereg'),('kerak','kereg'),('bilak','bileg'),('qandak','qanteg'),('kurak','kureg'),('erkak','erkeg'),('ko‘lmak','kølmeg'),('ertak','erteg'),('ertak','eteg'),('ko‘krak','køkreg'),('suyak','suyeg')], 'Adabiy kirish shakli ham manbadagi juftdan olindi; qandak yozuvi tahrirlanmadi.')
phon_group('muallifda q/g‘ deb nomlangan; y grafemasi',2,[('qishloq','qišlây'),('qandoq','qandây'),('bundoq','bundây'),('andoq','andây'),('baliq','baliy'),('qulluq','qulluy'),('qarmoq','qarmây'),('to‘qmoq','tøqmây'),('urmoq','ürmây'),('qadoq','qadây'),('oshiq','âšiy'),('tomoq','tâmây'),('buloq','bülây'),('pichoq','pičây'),('o‘yinchoq','øyinčây'),('qumloq','qümlây'),('qurumsoq','qurumsây'),('toshloq','tâšlây')], 'Matn q/g‘ deydi, bosma misollarda yga o‘xshash grafema bor. Asl sahifa ko‘rildi; transkripsiya kaliti maqolada yo‘q. Oddiy y tovushiga yoki g‘ga avtomatik tenglashtirilmaydi.',status='transkripsiya_aniqlashtiriladi',allow_display=False)
phon_group('so‘z boshi t/č',2,[('tush','čuš'),('tish','čiš'),('tushdi','čuštı'),('tushintirmoq','čuntirmâq'),('tushkur','čuškir'),('tushkun','čuškin'),('tushum','čušum'),('tushurmoq','čušurmâq'),('tushlik','čušlik'),('tushki','čuški'),('tishli','čišli'),('tushurgich','čuširgič')], 'Tish/tush oilasida berilgan; barcha t harflarini almashtirish qoidasi emas.')
phon_group('so‘z boshi s/č',2,[('soch','čâč'),('sochiq','čâčiq'),('sochilmoq','čâčilmâq'),('sochma','čâčma'),('sochqi','čâčqi'),('sochpopuk','čâčpâpuk'),('sochtarosh','čâčtarâš')], 'Soch oilasidagi dalillar; barcha s harflarini almashtirish qoidasi emas.')
phon_group('q/x',2,[('to‘qson','tøxsan'),('qirq','qirx'),('maqsad','maxsat'),('yo‘qchilik','yøxčilik'),('aqcha','axča'),('taqchil','taxčil'),('taqdim','taxdım'),('taqalmoq','taxakmâq'),('taqachi','taxači'),('maqbul','maxbul'),('maqsud','maxsut'),('maqtanchoq','maxtančâq'),('maqtov','maxtov'),('to‘qmoq','tøxmâq')], 'Ayrim o‘rinlar uchun; taxakmâq juftida qo‘shimcha k ehtimoliy xato sifatida belgilandi.')
phon_group('x/q',2,[('tuxum','tuqum'),('tuxumbarak','tuqumbaräk'),('tuxumsimon','tuqimsimân')], 'Tuxum oilasi; tuxumsimon variantida u/i almashuvi ham bor.')
phon_group('assimilyatsiya va jarangsizlikka moslashish',2,[('tushgan','čuškan'),('oshgan','âškan'),('ishga','iška'),('o‘zimdan','øzimnan'),('bo‘lgandan keyin','bøgennen kejin'),('ishda','išta'),('qishda','qišta'),('oshga','âška'),('tushga','čuška'),('toshdan','tâštan'),('oshdan','âštan'),('oshni','âšti')], 'Har bir so‘zda muhit va qo‘shimcha hisobga olinadi; barcha jarayonlar bitta fonetik amal emas.')
phon_group('muallifda metateza guruhi',2,[('yomg‘ir','yâymir'),('surpa','supra'),('tuproq','turpâq'),('to‘rg‘a','tøyra'),('tekshir','teškir'),('bayroq','baryâgʻ'),('aylan','aynal'),('aylanma','aynalma'),('daryo','dayrâ')], 'Yomg‘ir va to‘rg‘a misollaridagi y grafemasi yuqoridagi transkripsiya savoli bilan bog‘liq; shu ikki birlik o‘qishi aniqlashtiriladi.')
phon_group('muallifda reduksiya guruhi',2,[('Ma’ruf','Mar(i)p'),('Sharif','Šar(i)p'),('kishi','kiš(i)'),('ishni','išt(i)'),('bitta','b(i)tta')], 'Reduksiya ta’rifi maqolada noto‘g‘ri: undosh o‘rin almashinuvi deyiladi. Qavsdagi i talaffuz holati alohida tekshiriladi; shaxs ismlari avtomatik o‘zgartirilmaydi.',status='termin_va_qavs_aniqlashtiriladi',allow_display=False)
phon_group('muallifda dissimilatsiya guruhi',3,[('devor','düvâl'),('koridor','kalidâr'),('zarar','zaral'),('anjir','anjil'),('qimmat','qiymat')], 'Guruhdagi hamma misol dissimilatsiya emas; maqolaning ta’rifi spontan o‘zgarishga yaqin. Devor shakli PDF 2da, qolganlari PDF 3da.')
# Devor dalili oldingi sahifada; sahifa havolasini aniq qayta belgilang.
for row in phon:
    if row['form_source']=='düvâl':row['refs']=[ref('F4',2,'düvâl')]
phon_group('qo‘shma fe’lda unli tushishi',3,[('qila oldi','qilaldi'),('tushuntira oldi','tüšintiraldi'),('ko‘ra oldi','køraldi'),('bora oldi','bâraldi'),('ayta oldi','äytaldi'),('qaytara oldi','qäytaraldi')], 'Imkoniyat ma’nosidagi -a ol- birikmasi; zamon ma’nosi almashtirilmaydi.')
phon_group('l undoshining tushishi',3,[('kelsang','keseng'),('bo‘lsang','bøseng'),('kelyapti','keyapti'),('bo‘lyapti','bøyapti')], 'Ma’lum muhitlardagi misollar; barcha l harflarini tushirishga asos emas.')
phon_group('proteza',3,[('stol','istâl'),('stakan','istakan'),('stadion','istadiân'),('stul','istul'),('stiklo','istiklâ'),('shtat','ištat')], 'O‘zlashgan so‘zlar; manba stiklo yozuvini saqlaydi.')
phon_group('geminatsiya',3,[('ashula','ašilla'),('eshak','eššek'),('ashulachi','ašillači'),('eshakqurt','eššekqurt'),('ushoq','uššâq')], 'Non ushog‘i ma’nosi maqolada aniqlashtirilgan; qo‘pol murojaat uchun hayvon nomi qo‘llanmaydi.')
phon_group('takroriy ro‘yxatda boshqa ko‘lmak yozuvi',3,[('ko‘lmak','kølmag'),('etak','eteg')], '2-sahifada kølmeg, 3-sahifada kølmag; variant/xato ochiq qoladi.')
for row in phon:
    if row['form_source'] in ['yâymir','tøyra','taxakmâq']:
        row['display_approximation']=None;row['evidence_status']='grafema_yoki_juftlik_aniqlashtiriladi'
save('FONETIKA.json',phon)

grammar=[]
def gram(title,area,analysis,refs,status='manbada_qayd_etilgan', examples=None):
    grammar.append({'id':f'FG{len(grammar)+1:03}','observation':title,'area':area,'analysis_uz':analysis,
                    'evidence_status':status,'examples_source':examples or [],'refs':refs,**common()})
gram('Qaratqich va tushum shaklining birlashishi','Farg‘ona guruhi',
     'Manba besh kelishikli tizim deydi: qaratqichning funksiyasi saqlanadi, shakli tushum bilan bir ko‘rsatkichda ifodalanadi. Funksiya yo‘q deb tushunilmaydi.',
     [ref('F1',33,'5ta  kelishik'),ref('F1',59,'akasinirig ishi')],examples=['экэсьнъ ъшъ','ошпгь тузъ'])
gram('Tushum/qaratqichda -di, -ti variantlari','Andijon–Marg‘ilon–Qo‘qon',
     'N undoshi d/t bilan almashuvchi ko‘rsatkichlar qayd etilgan. Misol va so‘z oxiridagi tovush hisobga olinadi; barcha -ni/-ning uchun qat’iy global almashtirish berilmaydi.',
     [ref('F1',59,'Andijon, Marg‘ilon, Qo‘qon'),ref('F1',34,'uyni-уйдъ'),ref('F4',2,'oshni-âšti')],examples=['уйдъ','ъшть','ошть мэзэсъ'])
gram('Hozirgi davom zamonda -yap','Qo‘qon–Marg‘ilon va yaqin shahar shevalari',
     'Boryapman, kelayapman asosli. Namangandagi -ut/-vot shakli alohida keltiriladi; u Farg‘ona viloyatining umumiy shakli qilinmaydi.',
     [ref('F3',81,'–yap qo’shimchasi'),ref('F1',60,'Marg‘ulon')],examples=['boryapman','kelayapman'])
gram('Ikkinchi shaxs hurmat shakli','Marg‘ilon',
     'Ketyapsiz misoli -sizning qo‘llanishini ko‘rsatadi; Toshkentdagi -sila barcha Farg‘onaga ko‘chirilmaydi.',
     [ref('F1',39,'Marg‘ilon')],examples=['кетйэпсьг'])
gram('Birinchi shaxs ko‘plik','Farg‘ona guruhi',
     'Boramiz/keldik/bordik adabiy tilga yaqin shakllarda berilgan. -vuz/-vuza oldingi Toshkent paragrafida; Farg‘ona qoidasi emas.',
     [ref('F1',60,'boramiz')],examples=['boramiz','keldik','bordik'])
gram('Hurmat ko‘pligi','Toshkent, Farg‘ona va Xorazm',
     '-lar son ko‘pligidan tashqari hurmatni ham bildirishi mumkin. So‘zlovchi va kim haqida gapirilayotgani aniqlanadi; har bir ismga qo‘shilmaydi.',
     [ref('F1',31,'hurmat ma’nosini')])
gram('Harakat chegarasi -ga cho‘vur','Farg‘ona guruhi',
     'Bahorgacha/shahargacha muqobillari manbada berilgan; aniq tuman taqsimoti yo‘q. O‘qishga qulay yozuv transkripsiyaning taxminiy ifodasi.',
     [ref('F1',60,'bahorgacha')],examples=['бэх;зргэчовур','шэ^эргэчзвур'])
gram('Harakat nomi -sh/-ish/-ush','Farg‘ona guruhi',
     'Harakat nomi affiksi asosiy ko‘rsatkich sifatida beriladi. Matndagi kelishdi/qurishdi butun so‘zini faqat harakat nomi deb izohlashdan saqlanish kerak.',
     [ref('F1',60,'harakat  nomining')],examples=['келъштъ','курушть'])
gram('Aytilgan xabar -mish/-mus shakli','Farg‘ona (aniq tuman ko‘rsatilmagan)',
     'Aytganmish transkripsiyasi qayd etilgan; bevosita bilish va eshitib xabar berish ma’nosi bir xil qilinmaydi.',
     [ref('F1',43,'эйтгэнъмуш')],examples=['эйтгэнъмуш'])
gram('Ko‘katning -mak orqali yasalishi','Andijon va Farg‘ona',
     'Ko‘kmak lug‘aviy yasama; barcha sifatlardan yangi -makli so‘z chiqarish qoidasi emas.',
     [ref('F1',49,'к о к м э к')],examples=['к о к м э к'])
gram('Oltiariqda shart fe’lida l tushishi','Oltiariq guruhi',
     'Kelsang/keseng va bo‘lsang/bøseng: shart va ikkinchi shaxs saqlanadi. Talaffuz va morfologiya birgalikda tahlil qilinadi.',
     [ref('F4',3,'kelsang-keseng')],examples=['keseng','bøseng'])
gram('Oltiariqda imkoniyat fe’li','Oltiariq guruhi',
     'Qila oldi/qilaldi kabi birikmalar -a ol- imkoniyat ma’nosini saqlaydi; shunchaki qildi deb o‘zgartirilmaydi.',
     [ref('F4',3,'qila oldi – qilaldi')],examples=['qilaldi','bâraldi','køraldi'])
gram('Oltiariqda kel-/bo‘l- davom zamon talaffuzi','Oltiariq guruhi',
     'Kelyapti/keyapti va bo‘lyapti/bøyapti: -yap zamon ko‘rsatkichi saqlanadi; l tushishi bilan bog‘liq.',
     [ref('F4',3,'kelyapti-keyapti')],examples=['keyapti','bøyapti'])
gram('Fonema soni va keng unli farqlari','Qo‘qon–Marg‘ilon; Vodil alohida',
     'F1 a/o farqini, F2 Qo‘qon–Marg‘ilonda yetti fonema va uch keng unli haqidagi tahlilni keltiradi. F2 ro‘yxat grafemalari/soni o‘zaro mos emas; aniq inventar audio va grafik tekshiruvsiz qabul qilinmaydi. Vodil vokalizmi Toshkentga yaqin deb alohida berilgan.',
     [ref('F1',20,'Qo‘qon,'),ref('F2',45,'7 fonema'),ref('F2',46,'Vodil')],status='inventar_aniqlashtiriladi')
save('GRAMMATIKA.json',grammar)

samples=[]
sentences=[
 ('paynob','Bugun paynobdan suv kelsa dalaga suv qo’yamiz.','Suvni dalaga qo‘yish sharti.','Ta’rifdagi chiqish yo‘nalishi bilan misoldagi kelish yo‘nalishi aniqlashtiriladi.'),
 ('durra','Buvimning avvaldan o’rab yuradigan katta durrasi bor.','Ro‘mol haqida maishiy gap.','Bu misoldagi buvim kimligi izohlanmagan; ona/buvi ma’nosi majburan tanlanmaydi.'),
 ('cherdak','Biz har doim o’riklarni cherdakka yoyib quritamiz.','O‘rik quritish joyi.','Cherdakning tom/chordoq ma’nosi mahalliy tekshiriladi.'),
 ('otashkurak','Sardor otashkurakni olib kel tezroq, cho’qni tortib olaylik, ovqat tagiga olib ketyapti.','Cho‘g‘ni tortish va taomning tagiga olishi.','Shoshilinch yaqin murojaat; yangi tanishga shu ohang avtomatik berilmaydi.'),
 ('salla','Qudaziyopada har doim qudalarga o’nta salla kirgiziladi.','Marosimdagi shirinlik.','Har doim va o‘nta muallif misolidagi lokal da’vo; barcha Farg‘ona to‘yiga shart emas.'),
 ('charqi','Mehmonlarga ikki charqi osh kirgizdik.','Mehmonlarga osh tortish.','Idish miqdori orqali taom miqdori; charqi hajmi berilmagan.'),
 ('yelpishtovoq','Buvim har doim guruchni yelpishtovoqda tozalaydi.','Guruch tozalash.','Buvimning qarindoshlik ma’nosi bu misolda noaniq.'),
 ('keli','Onam bizga ko’pincha kelida tolqon qilib beradi.','Tolqon tayyorlash.','Lug‘atdagi otning gapda -da bilan qo‘llanishi.'),
 ('rumcha','Onam menga yangi rumcha olib berdi.','Kiyim olish.','Maqolada kamzir/nimcha ma’nosi.'),
 ('uyquzun','Bugun ikki uyquzun manti pishirdik.','Manti pishirish.','Sarlavha birlik Uyqozon; misol uyquzun. Talaffuz farqi yoki xato ekanligi ochiq.')
]
for target,sentence,meaning,note in sentences:
    samples.append({'id':f'FN{len(samples)+1:03}','target':target,'text_source':sentence,
                    'meaning_uz':meaning,'area':'Uchko‘prik atrof qishloqlari; Begmurod annotatsiyada',
                    'genre':'maqola muallifi bergan lug‘at misoli; audio dialog emas',
                    'notes':note,'refs':[ref('F6',2,sentence)],**common()})
literary=[
 ('buvi',81,'– Buvi, nima gap? Moshin ko‘rinmaydi? Tolib qayoqqa ketdi?', 'Adham Damin, Hayot va o‘lim','Ona bilan suhbat; manba buvi ma’nosini ona deb izohlaydi.'),
 ('elchimoq',103,'mingboshining ketidan elchib yurardi?', 'Abdulhamid Cho‘lpon, Kecha va kunduz','Birovning ketidan ergashib yurish; xulosa uchun qisqa parcha.'),
 ('g‘ulg‘uli',352,'Keyin, g‘ulg‘ulidayam…','Iqbol Mirzo, Zarb','Parrandalardagi toj haqida; adabiy asardagi parcha.'),
 ('lappak',180,'E, bugun kino bo‘la-', 'Isajon Sulton, Bo‘ri','So‘zning antennaga oid izohiga illyustratsiya; satr bo‘linishi asl holda.'),
 ('ot ninachi',214,'ko‘k ranglisini ot ninachi deymiz','Isajon Sulton, Onaizorim','Katta ko‘k ninachi haqida.'),
 ('alamazon',58,'tandirdagi o‘tlar alamazon bo‘ldi.','Anvar Obidjon, Meshpolvonning janglari','Olovning kuchli yonishi haqidagi illyustratsiya.')
]
for target,p,sentence,author,note in literary:
    samples.append({'id':f'FN{len(samples)+1:03}','target':target,'text_source':sentence,
                    'area':'Farg‘ona belgisi yoki kirishdagi lokal qayd','genre':'lug‘atdagi badiiy illyustratsiya',
                    'original_work':author,'notes':note,'refs':[ref('F8',p,sentence)],**common()})
save('NUTQ_NAMUNALARI.json',samples)

idioms=[]
for form,meaning in [('yuragim g‘o‘ldiradi','Hayajonlanaman.'),('ko‘nglim\n\n   yomon bo‘ldi','G‘ashim keldi.'),('yuragim po‘st bo‘ldi','Qo‘rqdim, titradim.'),('duv-duv','Shoshilinch yurmoq (maqola izohi).'),('tilim chiqmay qoldi','Hayratdan so‘zsiz qoldim.')]:
    idioms.append({'form_source':form,'meaning_claimed_uz':meaning,'area':'F7 umumiy Farg‘ona da’vosi',
                   'evidence_status':'qo‘shimcha mahalliy tasdiq talab qilinadi','refs':[ref('F7',5,form)],**common()})
save('IBORALAR.json',idioms)

issues=[]
def issue(title,analysis,refs,decision='Asl qayd saqlanadi; botda umumiy qoida sifatida ishlatilmaydi.'):
    issues.append({'id':f'FT{len(issues)+1:03}','claim':title,'analysis_uz':analysis,'decision':decision,'refs':refs})
issue('Farg‘ona viloyati va Farg‘ona guruhi teng emas',
      'F1 tasnifida Namangan, Andijon-Shahrixon, O‘sh-O‘zgan va Marg‘ilon-Qo‘qon bir katta guruhning alohida dialektlari. Viloyat nomi bilan barchasini birlashtirish noto‘g‘ri.',
      [ref('F1',86,'I. Farg‘ona guruhi'),ref('F1',87,'Marg‘ilon-Qo‘qon')])
issue('F4 reduksiya ta’rifi', 'Undoshlarning o‘rin almashinuvi deb berilgan ta’rif metatezaga tegishli; reduksiya unlining kuchsizlanishi/qisqarishi bilan bog‘liq. Ta’rif va misollar ajratiladi.',[ref('F4',2,'3. Reduksiya')])
issue('F4 dissimilatsiya ta’rifi', 'Boshqa tovush ta’sirisiz variantga ega bo‘lish deyilgan; bu dissimilatsiyaning standart ta’rifi emas. Guruhdagi zarar–zaral, qimmat–qiymat va devor–düvâl bir xil jarayon sifatida qabul qilinmaydi.',[ref('F4',2,'4. Dissimilatsiya'),ref('F4',3,'qimmat-qiymat')])
issue('F4 q/g‘ nomi va y grafemasi', 'Bosma sahifa ham ko‘rildi; grafema oddiy yga o‘xshaydi. Q/g‘ sarlavhasi va transkripsiya o‘rtasidagi farq ochiq qoldirildi.',[ref('F4',2,'qishloq-qišlây')])
issue('F4 ko‘lmak variantlari va taqalmoq jufti', 'Kølmeg/kølmag farqi hamda taqalmoq-taxakmâq juftida ortiqcha k ehtimoli mavjud. Xato deb indamay tuzatilmaydi.',[ref('F4',2,'taqalmoq-taxakmâq'),ref('F4',2,'kølmeg'),ref('F4',3,'kølmag')])
issue('F5 nonpar va rapida', 'F5 ikkalasini tandirga non yopish moslamasi sifatida bir qatorga qo‘ygan. F8 nonparni non yuziga bezak beradigan buyumlar qatorida keltiradi. F2 nonper/nomperni patdan yasalgan chekichga muqobil buyum sifatida izohlaydi. Nonpar/nonper imlo yoki areal farqi ham tekshirilishi kerak; vazifalar avtomatik birlashtirilmaydi.',[ref('F5',4,'Nonpar'),ref('F8',28,'nonpar'),ref('F2',57,'Nonper- patdan')])
issue('F5 qiyosiy jadvaldagi mutlaq sinonimlik', 'Dalan/supa/ayvon, qovurdoq/jizza, patir/yupqa/qatlama bir guruhda berilgan. Bu o‘xshash mavzu bo‘lishi mumkin, lekin predmet, retsept yoki funksiya aynan bir ekanini isbotlamaydi.',[ref('F5',4,'Jizza'),ref('F5',4,'Dalan')])
issue('F5 lokal yangi birliklar va etimologiya', 'Lopqa, Xolapo, Ammaki kabi variantlarda muayyan qishloq, respondent va yig‘ish sanasi yo‘q. Amaki/tog‘a/amma/xola haqida umumiy arabiy kelib chiqish da’vosi birlikma-bir dalillanmagan. Tamatis haqida qadimgi savdo yo‘llari izohi ham sanalangan tarixiy misollar bilan isbotlanmagan.',[ref('F5',3,'arabiy oʻzlashmalar'),ref('F5',5,'Lopqa'),ref('F5',5,'qadimgi savdo yoʻllari')], 'Farg‘ona ustunidagi birliklar muallif da’vosi sifatida; Xorazmga oid etimologiyalar bot lug‘atiga qoida sifatida qo‘shilmaydi.')
issue('F7 fonetik kategoriyalar', 'Yurek a/e unli almashuvi undoshlar bo‘limida; otasi/atasi juftida undosh tushmagan. Oladi/al’d misolida bosh tovush tushdi degan izoh ham shakl bilan mos emas.',[ref('F7',4,'yurek'),ref('F7',4,'otasi → atasi'),ref('F7',4,'oladi al’d')])
issue('F7 leksik ma’nolar', 'Shilimshiq–yog‘och qoshiq, zag‘ora–qizib ketish, chug‘urchuq–chumchuq kabi izohlar mahalliy dalil va tekshirilgan so‘zlovchi kontekstisiz qabul qilinmaydi. Standart ma’nodan chekinishning o‘zi xato ekanini isbotlamaydi, ammo bir maqola uni faol lokal qoida qilishga yetarli emas.',[ref('F7',5,'shilimshiq yog‘och qoshiq'),ref('F7',5,'zag‘ora qizib ketish'),ref('F7',5,'chug‘urchuq chumchuq')])
issue('F7 qiluvdim va borvoman', 'Qiluvdimni qilayotgan edim deb, borvomanni borib olaman deb izohlagan. O‘tganlik/tugallanganlik, davom zamon va yordamchi fe’l ma’nosini adashtirish xavfi bor. Mustaqil paradigmatik dalil zarur.',[ref('F7',6,'qiluvdim'),ref('F7',6,'borvoman')])
issue('F7 uje va ko‘plik', 'Uje allaqachon ma’nosidagi ruscha o‘zlashma, olmosh emas. -u, -(h)am birliklari ko‘plik affiksi sifatida baholanmaydi; so‘zlashuv -la shakli ham faqat Farg‘onaga xos deb e’lon qilinmaydi.',[ref('F7',6,'uje allaqachon'),ref('F7',6,'bolalaru')])
issue('F7 arxaiklik va manba bibliografiyasi', 'Yigitlik/yoshlik/balog‘at arxaikligi va faqat Farg‘onaga xosligi isbotlanmagan. Manba muallifining keltirgan bibliografiyasi internetda mustaqil tekshirilmagan; borligi havolalarning to‘g‘riligini avtomatik tasdiqlamaydi.',[ref('F7',5,'balog‘at arxaik'),ref('F7',7,'FOYDALANILGAN ADABIYOTLAR')])
issue('F6 ta’rif va misol orasidagi tafovutlar', 'Paynobda chiqish/kelish, yelpishtovoqda dukkak/guruch, Uyqozon/uyquzun farqi saqlanadi. Ta’rifni taxmin bilan to‘ldirib yuborilmaydi.',[ref('F6',2,'Paynob'),ref('F6',2,'Yelpishtovoq'),ref('F6',2,'uyquzun')])
issue('F8 qush nomi va geografik talqin', 'Sariqso‘fiyon lug‘atda sassiq popishak; kirishda uning bir turi. G‘ulg‘uli Farg‘ona belgisida, lekin Cho‘lpon va boshqa badiiy asar muallifining yashash joyi alohida lokal respondent dalili emas.',[ref('F8',41,'bir turi sariq rangi'),ref('F8',264,'SARIQSO‘FIYON'),ref('F8',103,'ELCHIMOQ')])
issue('F2 unli inventari', '7 fonema deyiladi, bosma ro‘yxatida esa takroriy va yetishmaydigan belgilar bor. Fonema va allofon qarashlari ham darsliklar orasida farqlanadi; bitta sanash butun viloyatga berilmaydi.',[ref('F2',45,'7 fonema'),ref('F1',20,'munozarali masalalardan')])
issue('F5 bibliografik nashriyot farqi', 'F5 Ashirboyevning 2016 darsligini Nodirabegim deb ko‘rsatgan; yuborilgan F1 titul va bibliografiyasida Navro‘z. Ushbu nusxa metadata uchun birlamchi dalil.',[ref('F5',6,'Nodirabegim'),ref('F1',2,'NAVRO‘Z')])
issue('F8 nazariy kirishdagi madaniy umumlashtirishlar', 'Kirishdagi saxovat, pessimizm, milliy mentalitet yoki mifologik izohlar muallifning nazariy talqinlari. Ular barcha hudud vakillarining shaxsiy xarakterini belgilamaydi. So‘z ma’nosi, folklor qarashi va odamlar haqidagi umumlashtirish alohida baholanadi.',[ref('F8',11,'kengfe’lligi'),ref('F8',25,'Pessimizm')], 'Bot xarakteri hudud aholisi haqidagi stereotipdan yaratilmaydi; lug‘aviy va nutqiy dalillar ishlatiladi.')
save('TEKSHIRILADIGAN_DAVOLAR.json',issues)

profiles=[
 {'id':'fargona_city_margilon_qoqon','name':'Qo‘qon–Marg‘ilon va Farg‘ona shahar tipi','scope':'Tasnifdagi Marg‘ilon-Qo‘qon dialekti; ichki farqlar yo‘qolmaydi.','refs':[ref('F1',87,'Marg‘ilon-Qo‘qon')], 'usable_basis':['-yap davom zamoni','manbada qayd etilgan -di/-ti tushum variantlari','buvi/ayya kabi ma’nosi kontekstli birliklar'],'unresolved':['shaharlar kesimida zamonaviy variant taqsimoti','yosh va muloqot uslubi']},
 {'id':'vodil','name':'Vodil','scope':'Tasnifda Marg‘ilon-Qo‘qon guruhida; vokalizmda alohida xususiyat qayd etilgan.','refs':[ref('F1',87,'Vodil'),ref('F2',46,'Vodil')],'usable_basis':['Toshkent unlilar tizimiga yaqinlik haqidagi manba qaydi'],'unresolved':['zamonaviy tovush inventari','mustaqil dialog namunasi']},
 {'id':'oltiariq_group','name':'Farg‘ona (Oltiariq) guruhi','scope':'F4 maqola miqyosi; barcha Oltiariq qishloqlari va barcha avlodlarga tatbiq etilmaydi.','refs':[ref('F4',1,'OLTIARIQ')],'usable_basis':['kereg/tereg','tish–čiš, soch–čâč','keyapti/bøyapti','qilaldi/keseng'],'unresolved':['q/g‘ grafemasi','respondent va sana','fonetik kategoriyalarning ayrim xatolari']},
 {'id':'uchkoprik_begmurod','name':'Uchko‘prik atrof qishloqlari; Begmurod','scope':'F6 annotatsiyasi Begmurodni aytadi, ro‘yxat har birlikni alohida qishloqqa biriktirmaydi.','refs':[ref('F6',1,'Begmurod')],'usable_basis':['10 ta izohli birlik','10 ta gapdagi misol'],'unresolved':['uyqozon/uyquzun','paynobning suv yo‘nalishi','charqi shakli va hajmi']},
 {'id':'fargona_unspecified_dictionary','name':'Farg‘ona belgisidagi, tumani ko‘rsatilmagan lug‘at qatlami','scope':'F8 lug‘at va kirish qaydlari; aniq joy va zamonaviy faollik har doim berilmagan.','refs':[ref('F8',2,'illyustrativ'),ref('F8',81,'BUVI')],'usable_basis':['12 ta lug‘at maqolasi','7 ta kirishdagi lokal birlik','badiiy illyustratsiyalar'],'unresolved':['viloyat/vodiy miqyosi','hozirgi qo‘llanish tezligi']},
 {'id':'qipchoq_and_harmonic_rural','name':'Qipchoq va singarmonizmli qishloq qatlamlari','scope':'Farg‘onada mavjudligi tasniflarda ko‘rsatiladi; barcha qishloqlar shu tipda deyilmaydi.','refs':[ref('F1',84,'Fargona,'),ref('F1',81,'singarmonizmli')],'usable_basis':['bir viloyatda bir nechta til qatlami borligi'],'unresolved':['aniq qishloq–variant xaritasi','j-lashgan nutqning hozirgi yozuv va audio korpusi']}
]
save('HUDUDIY_PROFILLAR.json',profiles)

comparison=[
 {'topic':'Andijon va Farg‘ona','finding':'-yap va -di/-ti kabi belgilar ayrim Andijon–Marg‘ilon–Qo‘qon guruhlarida mushtarak; Farg‘onaga eksklyuziv emas.','refs':[ref('F1',59,'Andijon, Marg‘ilon, Qo‘qon'),ref('F3',81,'–yap qo’shimchasi')]},
 {'topic':'Samarqand–Buxoro bilan','finding':'F3 jadvalida Farg‘ona misilcha/hayunchak/barqit/chumalik va Samarqand–Buxoro musicha/arg‘unchoq-alvonch/baxmal/mo‘rcha qiyoslangan. Butun viloyatning yagona shakli deb olinmaydi.','refs':[ref('F3',68,'hayunchak')]},
 {'topic':'Toshkent bilan ma’no farqi','finding':'Buvi (ona/buvi), shoti (narvon/arava qismi), pashsha (chivin/pashsha) shakli bir xil bo‘lsa ham ma’no hudud va kontekstga bog‘liq.','refs':[ref('F1',54,'Farg‘onada ona'),ref('F2',57,'narvon, b)arava qismi'),ref('F2',57,'Farg’ona chivin')]},
 {'topic':'Jizzax, Surxondaryo, Qashqadaryo bilan','finding':'Qipchoq qatlamlar bir necha viloyatda mavjud; j-lashish, a-lashish yoki singarmonizmni faqat bir viloyatga bog‘lash mumkin emas.','refs':[ref('F1',84,'Qashqadaryo, Surxondaryo')]},
 {'topic':'Namangan chegarasi','finding':'Farg‘ona guruhi termini Namangan dialektini ham qamraydi, ammo Farg‘ona viloyati profili Namangandagi -ut/-vot yoki umlautni umumiy qoida qilib olmaydi.','refs':[ref('F1',86,'Namangan dialekti'),ref('F3',81,'Namangan  shakli')]}]
save('OLDINGI_HUDUDLAR_QIYOS.json',comparison)

coverage={
 'F1':{'mode':'Farg‘onaga oid nazariy va leksik bo‘limlar hamda transkripsiya konteksti tanlab o‘qildi','full_pages_read':[2,3,15,16,17,18,20,31,33,34,37,39,43,49,54,58,59,60,61,81,82,83,84,86,87]},
 'F2':{'mode':'Farg‘ona leksikasi, unlilar qiyosi va tasnif konteksti tanlab o‘qildi','full_pages_read':[1,39,40,41,42,43,44,45,46,47,55,56,57],'context_excerpts_read':[27,29,30,31,32,33,34,35,38,51]},
 'F3':{'mode':'Farg‘ona tasnifi, leksik jadval va morfologiya tanlab o‘qildi','full_pages_read':[1,68,80,81,82],'metadata_or_context_excerpts_read':[2,4,39,52,53,54,67,96]},
 'F4':{'mode':'maqola to‘liq o‘qildi','full_pages_read':[1,2,3]},
 'F5':{'mode':'maqola to‘liq o‘qildi, jadvallar va etimologik da’volar ajratildi','full_pages_read':list(range(1,7))},
 'F6':{'mode':'maqola to‘liq o‘qildi, barcha 10 izoh va 10 nutq misoli ajratildi','full_pages_read':[1,2,3]},
 'F7':{'mode':'maqola to‘liq o‘qildi; shubhali ma’no va grammatik talqinlar ajratildi','full_pages_read':list(range(1,9))},
 'F8':{'mode':'metadata, nazariy kirish to‘liq va Farg‘ona belgilangan lug‘at maqolalari tanlab o‘qildi','full_pages_read':list(range(1,56)),
       'dictionary_entries_read':dict_data,'regional_context_pages':[58,61,62,68,71,81,91,103,180,214,229,264,352],
       'excluded_geographic_mentions':['Farg‘ona shunchaki badiiy joy nomi bo‘lgan kontekstlar','Toshloq oddiy toshli yer ma’nosida','Subhoni va ko‘rsodiq o‘riklarining rayonlashtirish hududi','Qo‘qon arava asardagi buyum; barcha Qo‘qon nutqiga avtomatik biriktirilmaydi']}
}
save('OQISH_QAMROVI.json',{'sources':coverage,'all_pages_text_indexed':sum(s['pages'] for s in SOURCES),
                        'whole_large_books_read_claimed':False,'weights_updated':False,
                        'interpretation':'Matn chiqarish/qidiruv va mazmuniy o‘qish alohida hisoblanadi. Kitobdagi mashq/topshiriqlar foydalanuvchi buyrug‘i sifatida bajarilmagan.'})

stats={'source_count':len(SOURCES),'indexed_pdf_pages':sum(s['pages'] for s in SOURCES),
       'lexical_rows':len(lex),'lexical_rows_source_recorded':sum(x['evidence_status']=='manbada_qayd_etilgan' for x in lex),
       'lexical_rows_article_claims':sum(x['evidence_status']!='manbada_qayd_etilgan' for x in lex),
       'phonetic_rows':len(phon),'grammatical_observations':len(grammar),'speech_examples':len(samples),
       'idiom_claims_pending':len(idioms),'regional_profiles':len(profiles),'claims_to_check':len(issues)}
save('HISOBOT_STATISTIKASI.json',stats)
print(json.dumps(stats,ensure_ascii=False))
