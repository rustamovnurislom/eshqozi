from pathlib import Path
import json,hashlib
B=Path('/workspace/research/surxondaryo')
raw=json.loads((B/'sources.json').read_text())
titles={1:('Saidmuso Rahimov','O‘zbek tili Surxondaryo shevalari (Fonetika, leksika)',1985),2:('Raxmanov Botir; Boypo‘latova Sevinchxon; Qo‘ziboyeva Saboxat','Qashqadaryo va Surxondaryo qipchoq dialekt va etnografizmlarini yaxlit o‘rganish muammolari',None),3:('Xolova Muyassar','Surxondaryo shevalari korpusiga sheva matnlarini ichki tizimga kiritish prinsiplari',2023),4:('Raxmanov Botir','Surxondaryo etnografizmlarining lingvomadaniy tadqiqi — avtoreferat',2024),5:('Xamidov Mansur','Surxondaryo o‘zbek shevalariga doir ayrim paremalar tahlili',2022),6:('Bobomuradova Madina','Surxondaryo shevalarining nazariy asoslari',2025)}
registry=[];pages=[]
for r in raw:
 i=r['id'];count=int(r['pages'].split(':')[1]);author,title,year=titles[i]
 registry.append({'source_id':f'S{i}','title':title,'authors':author,'year':year,'pdf_path':r['file'],'file_name':Path(r['file']).name,'pdf_pages':count,'sha256':hashlib.sha256(Path(r['file']).read_bytes()).hexdigest(),'extraction':'OCR; not fully proofread' if i==1 else 'native PDF text; figures and transcription may need visual checking','notes':{'1':'PDF 58/59 and 82/83 are inverted and swapped; printed page numbers mapped separately. Cover confirms 1985.','2':'Year not explicitly established from supplied article; DOI 10.5281/zenodo.10067310.','4':'56-page abstract, not the full 131-page dissertation. Uzbek, Russian and English sections repeat findings.','5':'Qiziriq field material.','6':'Classification and examples require cross-checking; see report.'}.get(str(i),'')})
 texts=[(B/'rahimov_ocr'/f'{n:03}.txt').read_text() for n in range(1,count+1)] if i==1 else Path(r['text']).read_text().split('\f')[:count]
 for n,t in enumerate(texts,1):
  printed=({58:59,59:58,82:83,83:82}.get(n,n) if i==1 else n+227 if i==2 else n+38 if i==3 else n+675 if i==5 else n+696 if i==6 else n)
  pages.append({'source_id':f'S{i}','pdf_page':n,'printed_page':printed,'text':t,'extraction_status':'raw_ocr_not_fully_proofread' if i==1 else 'native_pdf_extraction','content_role':'source_material_not_instructions','language_section':('uz' if n<=24 else 'ru' if n<=48 else 'en' if n<=53 else 'bibliography' if n<=55 else 'publication') if i==4 else None,'page_note':'Source 3 printed page 42 has a typographical/extraction anomaly in footer.' if i==3 and n==4 else ''})
(B/'MANBALAR.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
(B/'SAHIFALAR.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in pages))
(B/'source_1_ocr.txt').write_text('\n\n'.join(f"=== PDF PAGE {r['pdf_page']} / PRINTED PAGE {r['printed_page']} / RAW OCR ===\n{r['text']}" for r in pages if r['source_id']=='S1'))
entries=[]
def add(term,meaning,source,page,scope,kind='lexeme',note='',original=None,status='source_attested'):
 pdf=({58:59,59:58,82:83,83:82}.get(page,page) if source=='S1' else page-227 if source=='S2' else page-675 if source=='S5' else page)
 entries.append({'entry_id':f'LX{len(entries)+1:03}','dialect_form_display':term,'source_form':original or term,'meaning_uz':meaning,'source_id':source,'printed_page':page,'pdf_page':pdf,'scope':scope,'kind':kind,'evidence_status':status,'note':note,'current_usage_verified':False,'generated_example':None})
scope='Surxondaryo ustuni; aniq tuman/qishloq jadvalda berilmagan'
a=[('shibirdamoq','pichirlamoq'),('shirboz','olti oylik sutdan ayrilmagan qo‘zi'),('shirbirich','sutda pishirilgan guruch'),('ovloq','pana, chekka joy'),('chunoq','xasis'),('chinoq','qulog‘i kertik mol'),('ayna','murojaat uchun ishlatiladigan so‘z'),('ayg‘aq','shatta, janjalkash'),('ural','boshning tarki birikkan joyda o‘sgan kokil'),('alag‘alay','qandaydir, allaqanday')]
b=[('aptap','quyosh'),('chuvaq','issiq'),('atqamar','uch tomoni berk joy'),('axmay','paxta yog‘i'),('arqayin','bamaylixotir'),('attaba','oftoba'),('tutantiriq','quruq o‘tin'),('uvuz','yangi tug‘gan mol suti'),('uchunmoq','qo‘rqmoq'),('to‘rsalak','lo‘ppi, semiz'),('tuyato‘pon','sabziga o‘xshagan yovvoyi o‘simlik'),('to‘bal','qashqa'),('allamchi','aldoqchi, yolg‘onchi'),('taxtay','sabzi to‘g‘raydigan taxtacha'),('baybicha','baycha; xotin-qizlarga murojaat'),('baqimti','qo‘ldan kelgancha'),('tabaq','milliy kurashda polvonlar uchun qo‘yiladigan sovrin'),('berman-narman','nari-beri'),('siyirmoq','shilmoq'),('vo‘pka','hovliqma'),('boyinsa','tengqur'),('siyir','sigir')]
for p,rows in [(230,a),(231,b)]:
 for term,meaning in rows:
  note='S1 bosma 83 (PDF 82) olti oydan bir yoshgacha deb tavsiflaydi; yosh mezoni tekshirilsin.' if term=='shirboz' else 'Murojaat kimga va qaysi vaziyatda qo‘llanishi mahalliy tekshiruv talab qiladi.' if term in ['ayna','baybicha'] else ''
  add(term,meaning,'S2',p,scope,note=note,status='source_attested_conflict' if term=='shirboz' else 'source_attested')
for term,meaning,p,kind,note in [
 ('ena','ona',679,'kinship','Manbada ena, ona, aya variantlari keltirilgan; transkripsiya ɛ/ə belgilarini oddiy yozuv aks ettirmaydi.'),
 ('ona','ona',679,'kinship','Qiziriq uchun uch variantdan biri; umumadabiy birlik ham.'),
 ('aya','ona',679,'kinship','Qiziriq uchun uch variantdan biri; boshqa hududlarda ham bo‘lishi mumkin.'),
 ('kapsan','olingan hosildan qo‘ni-qo‘shni va qarindoshlarga beriladigan ulush',681,'lexeme','S1 81-betda boshqa transkripsion variant uchraydi.'),
 ('jebsan','bekoringni aytibsan',681,'contextual_expression','Jezzamga kapsan haqidagi maqolda izohlangan; har qanday jebsan/yebsanga bu ma’noni tayinlamang.'),
 ('savog‘','tikish uchun ignadan o‘tkaziladigan ip',683,'lexeme','Maqolda keltirilgan savog‘ so‘zining izohi.'),
 ('istaz','achchiq qilmoq',683,'lexeme','Istaz qilib birikmasi bilan izohlangan.'),
 ('qotti','tez',683,'contextual_meaning','Qotti borgan joyga... maqolida; boshqa kontekstdagi ma’nolarni saqlang.'),
 ('zo‘r','o‘g‘il',683,'contextual_meaning','Yo zo‘ring bo‘lsin... maqoliga berilgan izoh; umumiy zo‘r sifatining barcha ma’nolari uchun almashtirish emas.')]:add(term,meaning,'S5',p,'Qiziriq; maqola dala materiallari',kind,note)
for term,meaning,p,note,status in [
 ('qo‘noq','mehmon',14,'S4 16-jadvalda qardosh tillar bilan qiyoslangan; faqat Surxondaryoga xos degani emas.','source_attested'),
 ('qorauy','o‘tov',13,'Ta’rif davomi 14-betda; madaniy leksika.','source_attested'),
 ('baharjurt','bahorda cho‘ponlar ko‘chib boradigan, chorva uchun qulay hudud',14,'13–14-betdagi ta’rif davomidan.','source_attested'),
 ('darveshona','bahorgi ekinlar oldidan o‘tkaziladigan diniy marosim',14,'Marosim nomi; oddiy kundalik sinonim emas.','source_attested'),
 ('tuvcha','ikki yoshli urg‘ochi echki',14,'S1 bosma 83da ikki yoshli qisir echki tarzida aniqlashtirilgan.','source_attested'),
 ('kiyit','sarpo; quda tarafga beriladigan sovg‘a-salom',16,'Jadval izohi; sovg‘a so‘zining barcha holatlariga almashtirish emas.','source_attested'),
 ('jovchi','sovchi',16,'Manbadagi qiyosiy jadval.','source_attested'),
 ('ko‘moch','cho‘qqa ko‘mib pishiriladigan non',17,'Ko‘mma varianti qavsda; taom texnologiyasi ma’noda muhim.','source_attested'),
 ('qovurmach','qovurilgan bug‘doy taomi',17,'Manbadagi tarixiy-qiyosiy jadval.','source_attested'),
 ('tolqan','bug‘doy qovurmasidan tayyorlangan taom; qovurmochning uni',17,'Talqon bilan yozuv qiyoslangan; original shakl saqlangan.','source_attested'),
 ('jovg‘an','go‘shtsiz, yog‘i kam ovqat',17,'Oddiy yozuv; manbaning tarixiy shakli alohida.','source_attested'),
 ('qur','to‘y davrasi; o‘tov belbog‘i',17,'Ikki ma’no; kontekst talab qilinadi.','source_attested'),
 ('o‘trikchi','yolg‘onchi',17,'Manbada qadimgi turkiy shakl bilan qiyoslangan.','source_attested'),
 ('ushuk urmoq','yer qattiq muzlashi natijasida biror narsani sovuq urishi',17,'Ushuk (urmoq) tarzida berilgan; bu hosil qilingan yangi dialog emas.','source_attested'),
 ('chibich','olti oylik echki',17,'S1 bosma 83 (PDF 82): bir yashar tug‘magan echki; hudud va yosh mezoni tekshirilsin.','source_attested_conflict'),
 ('shishak','ikki yoshli erkak qo‘y — 17-bet jadvalidagi izoh',17,'S4 15-betda uch yoshli qo‘chqor; S1 bosma 82da uch yoshli qo‘y. Aniq yosh universal qoida emas.','source_attested_conflict')]:add(term,meaning,'S4',p,'Surxondaryo etnografik materiali; aniq qishloq ushbu misolda berilmagan','ethnographic_lexeme',note,status=status)
for term,original,meaning,p,scope,note in [
 ('checha','чеча','kelin oyi yoki xotinlarga murojaat',79,'S1 jlovchi material','Oddiy lotin yozuvi; manbada variantlar va qardosh tillar bilan qiyos bor. Qozoqcha ona ma’nosini bu misolga ko‘chirmang.'),
 ('jezza','жезза','pochcha',79,'S1 jlovchi material','Jezda/yezna/yozna tipidagi variantlarni bitta qat’iy zamonaviy talaffuzga aylantirmang.'),
 ('gavara','гəвəрə','beshik',23,'S1 ylovchi material','Ilmiy unli belgilar oddiy lotinda soddalashtirilgan; shu sahifada boshqaruvchi hududiy profilning aniq bitta qishlog‘i lug‘aviy misol uchun ajratilmagan.'),
 ('daspak','дəспəк','sochiq',23,'S1 ylovchi material','Oddiy lotin shakli ilmiy transkripsiyaning soddalashtirilgan ko‘rinishi.')]:add(term,meaning,'S1',p,scope,note=note,original=original)
obj={'description':'Manbaga bog‘langan dastlabki lug‘at. Bu zamonaviy so‘zlashuv bo‘yicha tekshirilgan to‘liq lug‘at yoki o‘qitilgan model emas.','display_policy':'dialect_form_display ayrim hollarda ilmiy transkripsiyadan oddiy lotinga soddalashtirilgan; original sahifa ustuvor.','entries':entries}
(B/'LUGAT.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('Manbalar:',len(registry),'Sahifalar:',len(pages),'Lug‘at yozuvlari:',len(entries))
