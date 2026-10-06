"""Source-based Samarkand research; all reading forms are editorial, not audio data."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def save(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
sources=json.loads((ROOT/'download_manifest.json').read_text())
meta={
 'M1':dict(title='O‘zbek dialektologiyasi',author='Samixon Ashirboyev',year=2016,publisher='Navro‘z, Toshkent',read_pages=[9,20,38,54,55,60,61,86,87,106,107],scope='Umumiy darslik; Samarqandga tegishli qismlar qayta o‘qildi. Qashqadaryo Q3 nusxasi bilan SHA-256 aynan bir xil.',visual_pages=[38,54,55,60,61,106,107]),
 'M2':dict(title='O‘zbek dialektologiyasi fanidan o‘quv-uslubiy majmua',author='Sh. Xudoyqulova',year=2008,publisher='Guliston davlat universiteti',read_pages=[30,31,32,33,34,42,45],scope='Umumiy kurs; tasnif va Samarqand qiyoslari o‘qildi. Qashqadaryo Q2 bilan SHA-256 aynan bir xil.',visual_pages=[42]),
 'M3':dict(title='Samarqand shevasining adabiy muhitdagi o‘rni',authors=['Jumashov Davlatyor','Abdurahmonova Marjona Farhod qizi'],year=2026,doi='10.5281/zenodo.19945184',printed_pages=[435,436,437],read_pages=[1,2,3],scope='3 sahifali maqola to‘liq o‘qildi. Hudud tasnifi va ayrim grammatik/ma’noviy tenglashtirishlar tekshirishni talab qiladi.'),
 'M4':dict(title='O‘zbek shevalari tadqiqotlari: amaliyot, metodologiya va yangicha yondashuv',editor='Sh. Sirojiddinov',year=2022,publisher='Donishmand ziyosi, Toshkent',conference_date='2022-05-21',read_pages=[20,21,22,23,85,86,87,204,205,206],context_reviewed_pages=[81,82,83,84,88,89],scope='216 sahifali to‘plamdan Samarqandga bag‘ishlangan ikki maqola to‘liq va hududga taalluqli uch qiyosiy sahifa o‘qildi; barcha maqolalar Samarqandga oid emas.',visual_pages=[21,22,205,206],articles=[dict(id='M4-A',title='Samarqand o‘g‘uzlari nutqidagi so‘z hosil bo‘lishining ayrim xususiyatlariga doir',authors=['M. Abdiyev','S. Rahmonov'],pdf_pages=[20,21,22,23],fieldwork='2019–2021 dialektologik ekspeditsiya materiallari'),dict(id='M4-B',title='Samarqand shahar o‘zbek shevalarida qo‘llaniladigan taom nomlari to‘g‘risida',author='Zilola Raxmatillayevna Tillabayeva',pdf_pages=[204,205,206],fieldwork='2017–2021 dala materiallari'),dict(id='M4-C',title='O‘zbek shevalarida so‘z yasalishi (Navoiy viloyati shevalari misolida)',author='Navro‘z Sattorovich Raxmonov',pdf_pages=list(range(83,90)),scope='Faqat Samarqand/Narpay deb aniq belgilangan qiyoslar olindi.')]),
 'M5':dict(title='O‘zbek shevashunosligi',authors=['T. J. Enazarov','V. A. Karimjonova','M. S. Enazarova','Sh. S. Mahmadiyev','K. G‘. Rixsiyeva'],year=2012,publisher='Universitet, Toshkent',read_pages=[2,3,29,31,80,81,82,95],context_reviewed_pages=[11,13,14,15,16,18],visual_pages=[2,3,29,31,80,81,82,95],scope='Skan kitob. Ko‘pchilik PDF sahifasi ikki bosma sahifadan iborat. Tuzilishi, hududiy qidiruv natijalari, tegishli grammatika va lug‘at namunalari ko‘rildi. To‘liq OCR qidiruv indeksi; kitobning barcha sahifalari to‘liq o‘qilgan emas.'),
}
save('MANBALAR.json',[{**s,**meta[s['id']]} for s in sources])
with (ROOT/'SAHIFALAR.jsonl').open('w') as out:
 for s in sources:
    path=Path(s.get('ocr_text_path',s['text_path']))
    pages=path.read_text().split('\f')
    assert len(pages)>=s['pages']
    for n in range(1,s['pages']+1):
     printed=[434+n] if s['id']=='M3' else [n] if s['id'] in ['M2','M4'] else [n-1] if s['id']=='M1' and 9<=n<=107 else [2*n-4,2*n-3] if s['id']=='M5' and 3<=n<=95 else []
     out.write(json.dumps(dict(source_id=s['id'],pdf_page=n,printed_pages=printed,text=pages[n-1],extraction='OCR (uzb); tuzatilmagan, ikki sahifa matni aralashishi mumkin.' if s['id']=='M5' else 'PDF matn qatlami; transkripsiya/shrift xatolari mumkin.'),ensure_ascii=False)+'\n')

entries=[]
def add(form,meaning,region,branch,sid,page,printed,article=None,note='',genre='lug‘aviy birlik'):
 entries.append(dict(id=f'ML{len(entries)+1:03}',form=form,meaning_uz=meaning,region=region,dialect_branch=branch,source_id=sid,pdf_page=page,printed_page=printed,article_id=article,genre=genre,note=note,evidence_status='Manbada qayd etilgan; bugungi tabiiy ishlatilishi alohida tasdiqlanmagan.',writing_status='Manba lotin yozuvi yoki fonetik yozuvdan tahririy o‘qilish; aniq audio transkripsiya emas.',exclusive_to_region=False))

for form,meaning,page,note in [
 ('hayla','hu ana',38,''),('morcha','chumoli',54,''),('matal','ertak',54,'Adabiy tildagi matalning barcha ma’nolari bilan tenglashtirilmasin.'),('nonpar','parranda patidan yasaladigan nonni naqshlash asbobi',55,'Toshkent chakichi bilan vazifasi yaqin; materiali farqlanadi.')]:
 add(form,meaning,'Samarqand (darslik belgisi)','Aniq ichki hudud ko‘rsatilmagan','M1',page,page-1,note=note)
for form,meaning in [('qalampur','qalampir'),('o‘g‘ur','o‘g‘ir')]:
 add(form,meaning,'Samarqand (darslik qiyosi)','Qarluq bo‘limidagi misol','M2',42,42,note='Qiyos jadvalidan olindi; barcha Samarqand shevalariga majburiy shakl emas.')

ER='Samarqand shahri: maqolada «eronilar» deb atalgan o‘g‘uz jamoasi'
TU='Samarqand: turkman o‘g‘uzlari'
UR='Samarqand: urganji o‘g‘uzlari'
XI='Samarqand: xidireli turkman o‘g‘uzlari'
for form,meaning,region,page,note in [
 ('og‘a','tug‘ishgan, qondosh; aka va hurmatli murojaat',ER,21,'Maqola bu xususiyatni o‘g‘uzlar uchun umumiy deb bayon qiladi.'),
 ('isti-bisti','turgan-bitgani',ER,21,''),
 ('turan-biteni','turgan-bitgani',TU,21,''),
 ('duran-durushi','turgan-bitgani',TU,21,''),
 ('moshichiri','moshdan tayyorlangan quyuq yoki suyuq taom',ER,21,''),
 ('moshova / kichiri','moshdan tayyorlangan taom',TU+'; '+UR,21,'Maqola ikki jamoani birga keltiradi; variantlarni bittadan jamoaga majburan biriktirmadim.'),
 ('nozbo‘y','rayhon bilan nomdosh ishlatiladigan o‘simlik nomi',ER,21,'Maqolaning izohiga tayangan; aniq botanika turi mustaqil tasdiqlanmagan.'),
 ('bo‘roni','moyda qovurib pishirilgan ko‘katli ovqat',ER,21,''),
 ('lublo shurak','tuz solib qaynatilgan loviya va makkajo‘xori',ER,21,''),
 ('hulba shula','hilba solib pishirilgan shavla',ER,21,''),
 ('jig‘-jig‘ halbo','qovurib pishirilgan, moyi chiqib turgan shilimsimon halvo',ER,21,''),
 ('chorma fatir','mayda qovoq qo‘shib pishirilgan fatir non',ER,21,''),
 ('boyinjon murobbo','shakar, murch, yong‘oq va baqlajondan tayyorlangan murabbo',ER,21,''),
 ('pamdor murobbo','po‘sti qalin pomidordan tayyorlangan murabbo',ER,21,''),
 ('piskalpasta','kaltakesak',ER,21,'Hazil aralash haqorat ma’nosida ham ishlatilishi qayd etilgan; oddiy suhbatda odamga avtomatik qo‘llanmasin.'),
 ('asalzombir','asalari',ER,22,''),
 ('aselari / ori','asalari',TU,22,''),
 ('nuqra po‘pak','kelinchak sochiga uzun ip bilan taqiladigan kumush taqinchoq',ER,22,''),
 ('gupponcha','paxtalik nimcha',ER,22,''),
 ('nimche','nimcha',TU+'; '+UR,22,''),
 ('kaltacha','ayollarning motamda kiyadigan, chetlari bezatilgan uzun ustki kiyimi',ER,22,'Shu maqoladagi boshqa o‘g‘uzlarning keltecha varianti nimche bilan tenglashtirilgan. Farqli ma’nolar birlashtirilmadi.'),
 ('bazak ko‘rpacha','bezakli, quroq ko‘rpacha',ER,22,''),
 ('quroq go‘rpe','quroq ko‘rpacha','Samarqand: maqoladagi boshqa o‘g‘uz jamoalari',22,'Eronilar bazak ko‘rpachasiga qiyos; shahar qarluq profiliga avtomatik o‘tkazilmasin.'),
 ('g‘uncha yubormoq','nikoh to‘yi kuni yoki oldin kelin tomonidan kuyovlik liboslarini jo‘natish marosimi',ER,22,''),
 ('qo‘lba-qo‘l / dastba-das','to‘y kechasida oynada kelin-kuyovni bir-biriga ko‘rsatish marosimi',ER,22,''),
 ('hinobandon','qiz tomonida o‘tkaziladigan nikoh to‘yi',ER,22,'Manba yaqin o‘tmishdagi qo‘llanish deydi.'),
 ('pushtaboshi','marhum vafotidan keyingi ikkinchi jumada qarindosh ayollarning qabrni ziyoratga chiqishi',ER,22,''),
 ('gug girmoq','yaqin qarindosh ayolning marhum yil marosimigacha ko‘k libosda yurishi',ER,22,''),
 ('go‘k giymoq','motamda ko‘k libos kiyish','Samarqand: maqoladagi boshqa o‘g‘uz jamoalari',22,''),
 ('qirxa o‘tirmoq','qarindosh ayolning marhum qirq marosimigacha ko‘k libosda yurishi','Samarqand: maqoladagi o‘g‘uz jamoalari',22,'Yil va qirq muddatlari alohida; gug girmoq bilan ma’nosi to‘liq teng emas.'),
 ('ko‘cha jo‘ra','ulfat','Samarqand Turkman qishloq: urganji shevasi',22,''),
 ('shapat pul','katta pul',XI+'; '+UR,22,''),
 ('gartak','ozgina',XI,22,''),
 ('gitek','ozgina',UR,22,'Maqola boshqa shevalarda ham uchrashini qayd etadi.'),
 ('kurtik','zog‘ara undan tayyorlangan xamir ovqat',TU+'; '+UR,22,'O‘g‘uz taomi konteksti. Maqola 23-sahifada qipchoqda qor to‘planishi ma’nosi borligini aytadi; jamoalarni aralashtirmaslik kerak.')]:
 add(form,meaning,region,'O‘g‘uz','M4',page,page,'M4-A',note=note)

for form,meaning,page,note in [
 ('chalamafatir','ichiga qovoq, piyoz solib yopiladigan yupqa non',205,''),
 ('bichak','yupqa xamir ichiga qovoq yoki o‘t solib pishirilgan taom',205,'Kadubichak, alafinbichak, kabachkibichak variantlari sanalgan; har biri uchun alohida retsept berilmagan.'),
 ('barak','ichiga qiyma solib tugiladigan xamir ovqat, chuchvara varianti',205,'Pudinabarak, kadubarak, go‘shbarak, havobarak turlari keltiriladi.'),
 ('g‘elak sho‘rbo','go‘sht asosiy masalliq bo‘lgan sho‘rva turi',205,'Maqola tarkibini batafsil ajratmaydi; taxminiy retsept qo‘shilmadi.'),
 ('naxo‘t sho‘rbo','go‘sht asosiy masalliq bo‘lgan sho‘rva turi',205,'Nomi bo‘yicha to‘liq retsept chiqarilmaydi.'),
 ('biyron sho‘rbo','go‘sht asosiy masalliq bo‘lgan sho‘rva turi',205,''),
 ('piyova','go‘sht solinmaydigan, masallig‘i kam suyuq ovqat',205,''),
 ('atali biyron','qizdirilgan yog‘ga un va suv qo‘shib pishiriladigan atala',205,''),
 ('halboyitar','shakar solib tayyorlangan atala',205,''),
 ('g‘ilmindi','ichiga un va sutdan tayyorlangan oq atala solinadigan xamirli taom',206,'M3 ning g‘ilmindini jupqa bilan tenglashtirishi shu izoh bilan alohida tekshirilishi kerak.'),
 ('chivot','suzmaga rayhon, achchiq qalampir, tuz va ko‘kat solingan taom',206,''),
 ('o‘moch','ichiga uvalangan xamir solib pishiriladigan suyuq osh',206,'O‘mochi shirdor, o‘mochi moshdor turlari sanalgan.'),
 ('halisa','bug‘doy yormasi, go‘sht va yog‘ bilan pishiriladigan halim',206,'Maqoladagi halim/sheva nomi qiyosi.')]:
 add(form,meaning,'Samarqand shahri','Qarluq','M4',page,page,'M4-B',note=note,genre='taom nomi')

for form,meaning,page,note in [
 ('ilgir','kinnachi, suq chiqaruvchi shaxs',85,'Narpay tumani Mehrjon qishlog‘i va Navoiy Xatirchi tumani Mirdosh qishlog‘i'),
 ('o‘tirik','yolg‘on',86,'Samarqand sharqiy qipchoq shevalari; Doniyorov 1979:92 dan ikkilamchi dalil.'),
 ('p‘char','unashtiruv',87,'Narpay tumani Mehrjon qishlog‘i. Qo‘shni Xatirchidagi p‘chuv bilan qiyos. Maxsus unli belgisi oddiy lotin shakliga aylantirilmadi.')]:
 add(form,meaning,'Samarqand: '+note,'Qipchoq','M4',page,page,'M4-C',note=note)
for form,meaning,page,printed,note in [
 ('boshi qatti','sog‘lig‘i yaxshi',80,157,'Manbada Samarqand va Jizzax belgisi; sodda o‘qilish.'),
 ('bosh baylov','qizning unashtirilishi',80,157,'Manbada Yakkabog‘, Samarqand, Jizzax belgisi. Tahririy o‘qilish.'),
 ('salqi odam','ishni orqaga tashlaydigan, quntsiz odam',81,158,'Manbada Jizzax/Samarqand belgisi; tahririy o‘qilish.')]:
 add(form,meaning,'Samarqand va manbada birga ko‘rsatilgan hududlar','Ichki sheva ko‘rsatilmagan','M5',page,printed,note=note,genre='ibora')
save('LUGAT.json',dict(description='Manbasi, jamoasi va ma’nosi ko‘rsatilgan ishchi lug‘at. Manbada uchrashi bugungi tabiiylikni yoki hududga mutlaq xoslikni tasdiqlamaydi.',entry_count=len(entries),entries=entries))

candidate_rows=[
 ('avacha','bolakay','Pastdarg‘om'),('cho‘lpak','cho‘mich','Pastdarg‘om'),('patinjon','baqlajon','Pastdarg‘om'),('hiy','nima uchun','Pastdarg‘om'),('iytib','unday qilib','Pastdarg‘om'),
 ('bultirgi','o‘tgan yilgi','Qo‘shrabot qishloqlari'),('trama','kuz fasli','Qo‘shrabot qishloqlari'),('billa','birga','Qo‘shrabot qishloqlari'),('katata','buva','Qo‘shrabot qishloqlari'),('ana','buvi','Qo‘shrabot qishloqlari'),('dostiq','yostiq','Qo‘shrabot qishloqlari'),('duvol','devor','Qo‘shrabot qishloqlari'),('gitak','ozgina','Qo‘shrabot qishloqlari'),('iyarib','ergashib','Qo‘shrabot qishloqlari'),('ko‘ppala','ko‘p','Qo‘shrabot qishloqlari'),('makkai','makkajo‘xori','Qo‘shrabot qishloqlari'),('shibirtqi','supurgi','Qo‘shrabot qishloqlari'),('ul','o‘g‘il','Qo‘shrabot qishloqlari'),('avramoq','ishontirmoq','Qo‘shrabot qishloqlari'),('beqiliq','shum','Qo‘shrabot qishloqlari'),('bo‘xcha','kiyim-kechak','Qo‘shrabot qishloqlari'),('chakki','suzma','Qo‘shrabot qishloqlari'),('do‘ng','tepa','Qo‘shrabot qishloqlari'),('gitgitcha','kuchuk bolasi','Qo‘shrabot qishloqlari'),('pishak','mushuk','Qo‘shrabot qishloqlari'),('taypish','hovliqma','Qo‘shrabot qishloqlari'),('xamsiya','qo‘shni','Qo‘shrabot qishloqlari'),('xaymi','xo‘pmi','Qo‘shrabot qishloqlari'),('zardoli','o‘rik','Qo‘shrabot qishloqlari'),
 ('lo‘ppi','tez qizishadigan kishining laqabi; boshqa ma’noda to‘ladan kelgan kishi','Pastdarg‘om: chandir o‘g‘uz shevasi'),('pizze','sal narsaga ko‘tarilib ketadigan kishining laqabi','Pastdarg‘om: chandir o‘g‘uz shevasi'),('guppi','qila olmasa ham men qilaman deydigan kishining laqabi','Pastdarg‘om: chandir haqidagi bayon')]
save('TEKSHIRILADIGAN_BIRLIKLAR.json',dict(description='M3 dagi birliklar: tashlab yuborilmagan, lekin asosiy lug‘atga tasdiqsiz qo‘shilmagan. Aniq qishloq, ma’no va bugungi ishlatilish bo‘yicha qo‘shimcha dalil kerak. Lahja tuman nomidan chiqarilmadi.',entry_count=len(candidate_rows),entries=[dict(form=f,meaning_as_claimed=m,region_as_claimed=reg,source_id='M3',pdf_page=2,printed_page=436,status='Shu maqoladagi da’vo; mustaqil tasdiq va sheva vakili tekshiruvi kerak.') for f,m,reg in candidate_rows]))

rules=[]
for standard,reading,page,explanation in [
 ('xotin','xotun',60,'Ikkinchi bo‘g‘inda i → u.'),('dori','doru',60,'Ikkinchi bo‘g‘inda i → u.'),('uyqu','oyqu',60,'Darslikning maxsus unli sifatlari oddiy yozuvga soddalashtirilgan.'),('suhbat','sohbat',60,'Undoshlar oldidagi unli o‘zgarishi; umumiy barcha u larni almashtirish qoidasi emas.'),('guruh','guroh',60,'Leksik misol doirasi.'),('mix','mex',60,'Ayrim so‘zlarda i → e.'),('umid','umed',60,'Ayrim so‘zlarda i → e.'),('oldim','allim',60,'ld → ll assimilatsiyasi.'),('keldim','kellim',60,'ld → ll assimilatsiyasi.'),('kelyapman','kelappan',61,'Davom fe’li -ap; guruh bayonidagi misol.'),('kelar edim','kelayidim',61,'Sifatdoshdagi r → y.'),('kelmas edim','kelmayidim',61,'Bo‘lishsiz sifatdoshdagi s → y.')]:
 rules.append(dict(standard=standard,dialect_reading=reading,source_id='M1',pdf_page=page,printed_page=page-1,scope='Samarqand-Buxoro guruhi; darslik Qarshi, Koson, Chust, Xo‘jandni ham sanaydi. Butun viloyatga universal emas.',explanation=explanation,writing_status='Tahririy sodda o‘qilish; fonetik diakritikalar to‘liq saqlanmagan.'))
save('GRAMMATIKA.json',dict(description='Guruhga xos darslik misollari; gap ma’nosini saqlagan holda hududga mos qo‘llanishi tekshiriladi.',rules=rules,additional_observations=[dict(source_id='M5',pdf_page=29,printed_pages=[54,55],observation='Samarqand-Buxoro guruhida jo‘nalish va o‘rin-payt shakllari almashinishi; darslik -ga/-da, borish/yashash ma’nosi va Qarshi misollarini alohida beradi. Har bir -da ni -ga ga aylantirish qoidasi olinmadi.'),dict(source_id='M1',pdf_pages=[106,107],printed_pages=[105,106],region='Samarqand viloyati Qulota qishlog‘i',genre='Xalq qo‘shig‘i',observation='Yaxshi/jaxshi, yomon/jaman, yigit/jigit, yer/jer kabi so‘z boshidagi farqlar qo‘shiq matnida qayd etilgan; oddiy chatga tayyor dialog sifatida olinmaydi.')],rejected_direct_substitutions=[dict(source_id='M3',pdf_page=2,printed_page=436,claim='aytdi → aytyatir',reason='O‘tgan zamon va davom etayotgan harakat ma’nolari teng emas.'),dict(source_id='M3',pdf_page=2,printed_page=436,claim='bordim/keldim → boribedim/kelibedim',reason='Murakkab o‘tgan zamon ma’nosi ham qo‘shilishi mumkin; birma-bir neytral almashtirish emas.')]))

save('HUDUDIY_PROFILLAR.json',dict(profiles=[
 dict(name='Samarqand shahar qarluq nutqi',sources=['M1:60–61','M4-B:204–206'],notes='Tojik tili bilan uzoq aloqalar qayd etilgan. Taom nomlari butun kundalik grammatika tavsifi emas.'),
 dict(name='Samarqand viloyati qipchoq nutqi',sources=['M1:106–107 (Qulota)','M4-C:85–87 (Mehrjon va sharqiy qipchoq qiyoslari)'],notes='Aniq tuman/qishloq darajasidagi dalil talab qilinadi; viloyatning hammasi bitta j-lovchi profil emas.'),
 dict(name='Samarqanddagi o‘g‘uz jamoalari',sources=['M4-A:20–23'],subgroups=['eroni','urganji','xidireli/turkman'],notes='Maqola ichidagi nomlar va variantlar saqlandi. «Eroni» jamoa nomi umumiy «eronlashgan» tarixiy tasnif atamasi bilan bir xil emas.'),
 dict(name='M3 dagi Qo‘shrabot/Pastdarg‘om kundalik birliklar',sources=['M3:436'],notes='Nomzod material; ichki lahja va bugungi tabiiylik mustaqil tekshirilmagan.')],source_conflicts=[dict(source_id='M3',pdf_page=2,claim='Tumanlarni butunlay qipchoq/qarluq guruhlariga ajratish',issue='O‘sha maqolaning o‘zi Qo‘shrabotda j-lovchilar va Pastdarg‘omda chandir o‘g‘uz shevasini ham tasvirlaydi. M1/M4 ko‘p profilni tasdiqlaydi; qat’iy tuman = bitta lahja jadvali olinmadi.')]))

save('OLDINGI_HUDUDLAR_QIYOS.json',dict(description='Bu qiyoslar umumiylashuv va manba farqini ko‘rsatadi; viloyatning barcha so‘zlari uchun mexanik o‘zgartirish qoidasi emas.',comparisons=[
 dict(concept='Guruh grammatikasi',samarkand_source='M1:60–61',qashqadaryo_source='/workspace/research/qashqadaryo/GRAMMATIKA.json',finding='Bir xil Ashirboyev darsligi ikkala hudud tahlilida ishlatilgan; ikki mustaqil dalil deb sanalmasin.'),
 dict(concept='Qo‘shni',samarkand_form='xamsiya',samarkand_source='M3:436, qo‘shimcha tekshirish kerak',qashqadaryo_form='hamsoya',qashqadaryo_source='Q4:285',finding='Fonetik va hududiy farq mumkin; Samarqand shakli shu maqola bilan cheklangan.'),
 dict(concept='Xo‘pmi',samarkand_form='xaymi',samarkand_source='M3:436, qo‘shimcha tekshirish kerak',qashqadaryo_form='hayme',qashqadaryo_source='Q4:276',finding='Yaqin shakllar; eksklyuziv viloyat belgisi deb olinmasin.'),
 dict(concept='Ozgina',samarkand_forms=['gartak','gitek'],samarkand_source='M4-A:22',finding='Maqola xidireli/urganji va boshqa lahjalardagi variantlarni birga muhokama qiladi. Hudud ichidagi jamoa muhim.')]))
print('Lexical entries:',len(entries),'Candidates:',len(candidate_rows),'Grammar examples:',len(rules),'Indexed PDF pages:',sum(s['pages'] for s in sources))
