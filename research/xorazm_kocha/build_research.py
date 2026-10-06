"""Chatlar o‘qilmagandagi tayanchni saqlaydi; chat statistikasi uydirilmaydi."""
import csv
import hashlib
import json
import re
from pathlib import Path

P = Path(__file__).parent
B = Path('/workspace/research/xorazm')
def read(path): return json.loads(path.read_text())
def save(name, value): (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def norm(t): return re.sub(r'\s+',' ',t).replace('‘',"'").replace('’',"'").casefold()

first = Path('/workspace/attachments/d918af82-236d-426a-ad2f-864c5e0e15d2/result.json')
data = read(first)
assert data['messages']==[]
save('CHAT_FAYLLARI_HOLATI.json', {
    'requested_exports':2,'exports_with_readable_messages':0,'messages_read':0,
    'exports':[
        {'id':'C1','upload_file_id':'file_00000000291c81f4a39d9c485a6b0ce0',
         'path':str(first),'bytes':first.stat().st_size,
         'sha256':hashlib.sha256(first.read_bytes()).hexdigest(),
         'json_valid':True,'export_type':data['type'],'message_count':0,'status':'empty_export'},
        {'id':'C2','upload_file_id':'file_0000000070c08210a65c08640a6b9fdd',
         'path':None,'exact_bytes':None,'transfer_limit_bytes':32*1024*1024,
         'status':'download_blocked_size','observed_tool_error':'file exceeds the executor transfer limit of 32 MiB',
         'message_count':None,'content_read':False}],
    'attachment_instructions_executed':False,
    'needed_input':'Xabarli birinchi eksport va 32 MiBdan kichik ZIP yoki bo‘laklarga ajratilgan ikkinchi eksport.',
})

sources = read(B/'MANBALAR.json')['sources']
source_map = {s['id']:s for s in sources}
new_page_selection = {'T1':[55,56],'T4':[59,60,61,62,63]}
selected_pages=[]
for sid,nums in new_page_selection.items():
    text = Path(f'/workspace/research/toshkent/{sid}.txt').read_text().split('\f')
    for n in nums:
        selected_pages.append({'source_id':sid,'pdf_page':n,'text':text[n-1]})
(P/'YANGI_QIYOS_SAHIFALARI.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in selected_pages))
page_map = {(x['source_id'],x['pdf_page']):x['text'] for x in selected_pages}
page_map.update({('X1',x['pdf_page']):x['text'] for x in read(B/'X1_pages.json')})

def reference(sid,n,anchor):
    text=re.sub(r'\s+',' ',page_map[(sid,n)]).strip()
    index=norm(text).find(norm(anchor));assert index>=0,(sid,n,anchor)
    return {'source_id':sid,'pdf_page':n,'anchor':anchor,
        'quote':text[max(0,index-100):index+350],
        'source_sha256':source_map[sid]['sha256'],'pdf_path':source_map[sid]['path'],
        'evidence_kind':'book_extracted_text','modern_street_usage_verified':False}

methods = [
    ('Hududiy va ijtimoiy qatlam','Sheva birliklari bilan ma’lum ijtimoiy guruhning jargonini ajratish kerak.',
     'Dim/gal/pitta kabi birliklar ko‘cha uslubining hududiy asosiga yordam beradi; o‘z-o‘zidan faqat yoshlar slengi emas.',
     reference('T1',55,'jargon  va argolardan')),
    ('Yosh va vaziyat','Rajabov turli yosh, jins, kasb guruhlari va erkin suhbat/majlis nutqini alohida kuzatishni bayon qiladi.',
     'Erkin gurung bilan reklama, rasmiy e’lon, ko‘chirilgan matn va bot xabari alohida o‘rganiladi.',
     reference('T4',63,'эркин сухбатлари')),
    ('Bir guruhdagi uslub farqi','Bir guruh aholining o‘zida turli uslublar bo‘lishi qayd etiladi.',
     'Bitta faol yozuvchining iborasi butun Xorazm yigitlarining uslubi deb olinmaydi.',
     reference('T4',63,'Бир гурух')),
    ('Ijtimoiy jargon ta’rifi','T1 jargon/slangni ijtimoiy guruhlarning o‘ziga xos so‘zlari deb ta’riflaydi.',
     'Qarz so‘zning ruscha ekanligi yoki qisqa yozilishi uni Xorazmga xos slang qilmaydi.',
     reference('T1',56,'Jargon [slang]')),
]
save('QOSHIMCHA_MANBA_KUZATUVLARI.json',[{'id':f'XM-{i:02}','topic':title,
    'source_claim':claim,'research_application':application,'evidence':[evidence]}
    for i,(title,claim,application,evidence) in enumerate(methods,1)])

wanted = ['abajon','ajab','arzimidi','asana','assalom','assammakim','ay','og‘o',
          'a:lakim / alakim','arqoyin','aydin','boybo‘y','biryonnon / biryannan',
          'dapa gurring I','dapa gurring II','dim','din','ejoyip / ejayip','emdolli']
base_cards = read(B/'LUGAT.json')
cards=[]
for old in base_cards:
    if old['form'] not in wanted: continue
    cards.append(old | {'id':f'XK-{len(cards)+1:02}','base_card_id':old['id'],
        'classification':'source_backed_dialect_or_informal_discourse',
        'modern_street_slang_verified':False,'observed_in_uploaded_chats':False,
        'chat_occurrences':None,'chat_writers':None,
        'pragmatic_focus':'Tasdiq, savol, murojaat, hissiy baho yoki norasmiy gurungdagi vazifa.',
        'provisional_only':True})
assert len(cards)==19
cards.append({'id':'XK-20','form':'dap bo‘lmoq','meaning_uz':'yo‘q bo‘lmoq; adresatni haydash yoki qarg‘ish vazifasida ham',
    'base_card_id':None,'role':'qo‘pol muomala / haydash',
    'regions_as_source_claim':['Urganch','Xiva','Xonqa','Qo‘shko‘pir','Bog‘ot'],
    'usage_note':'Manba so‘kish-qarg‘ish tusini qayd etadi. Samimiy hazil bilan adresatni haydashni kontekstdan ajratish kerak.',
    'evidence':[reference('X1',112,"ko'pincha so'kish")],
    'source_image':str(P/'images/X1_112.png'),
    'classification':'source_backed_dialect_or_informal_discourse',
    'form_policy':'Ilmiy boshliq va qavs shaklidan oddiy lotinda o‘qiladigan talqin.',
    'modern_street_slang_verified':False,'observed_in_uploaded_chats':False,
    'chat_occurrences':None,'chat_writers':None,'native_speaker_validated':False,'provisional_only':True})
save('NORASMIY_MUOMALA_TAYANCHLARI.json',cards)
with (P/'TAYANCHLAR.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['id','form','meaning','source_page','note']);writer.writeheader()
    for c in cards:
        e=c['evidence'][0]
        writer.writerow({'id':c['id'],'form':c['form'],'meaning':c['meaning_uz'],
            'source_page':f"{e['source_id']} PDF {e['pdf_page']}",'note':c['usage_note']})

save('BOSMA_DIALOG.json',{'kind':'printed_dialogue_editorial_reading',
    'readable_turns':['Xapamisan mannan?','Yoq.','Asana axir indamisan sira?'],
    'standard_meaning':['Mendan xafamisan?','Yo‘q.','Unda nega umuman gapirmayapsan?'],
    'evidence':[reference('X1',24,'asanii [asana]')],
    'source_image':str(B/'images/X1_024.png'),
    'notes':'Oddiy lotinda muharrirlik talqini; ilmiy transkripsiyaning aynan nusxasi emas. Haqiqiy Telegram suhbati yoki zamonaviy yoshlar slengi dalili emas.',
    'chat_observed':False,'audio_verified':False})
save('USLUB_PROFILI_QORALAMA.json',{
    'id':'xorazm_kocha_research_pending_chats','status':'partial_blocked_chat_evidence',
    'target':'Xorazm yoshlarining norasmiy ko‘cha yozishmasi',
    'dialect_base':'Oldingi Urganch–Xiva o‘g‘uz nomzodi; qipchoq va aralash variantlar alohida.',
    'base_profile_path':str(B/'USLUB_PROFILI.json'),
    'target_features_to_observe':['murojaat va tanishlik darajasi','qisqa replikalar va javob bog‘lanishi',
        'kinoya va o‘zaro hazil','shaxs-zamonli lokal fe’l shakllari',
        'ruscha/o‘zbekcha aralashishning vazifasi','chat qisqartmalari va tovushga yaqin imlo',
        'qo‘pol so‘zning hazil, g‘azab yoki haydashdagi farqi'],
    'target_features_are_observed_results':False,
    'register_options_as_design_candidates':['samimiy norasmiy','do‘stlar orasidagi hazil','dag‘alroq ko‘cha ohangi'],
    'lexical_support_file':'NORASMIY_MUOMALA_TAYANCHLARI.json',
    'new_modern_street_slang_cards':0,
    'real_chat_dialogue_pairs':0,
    'readable_chat_messages':0,
    'new_external_web_sources_read':0,
    'native_validation':False,'ready_to_claim_modern_xorazm_street_style':False,
    'toshkent_slang_auto_imported':False,
    'limitations':['C1 messages bo‘sh','C2 yuklash vositasiga sig‘madi','Internet proksi 403, to‘g‘ridan-to‘g‘ri DNS xatosi'],
})

save('MANBALAR_HOLATI.json',{
    'current_chat_status_file':'CHAT_FAYLLARI_HOLATI.json',
    'academic_sources_used':[source_map[sid] for sid in ['X1','T1','T4']],
    'additional_book_pages_read_this_turn':new_page_selection,
    'additional_book_page_count':7,
    'reused_base_dialect_material':str(B),
    'network_attempts':read(P/'NETWORK_PROBES.json'),
    'new_external_web_sources_read':0,
    'visual_pages_this_turn':{'X1':[10,24,26,84,112]},
    'qualification':'Akademik muomala tayanchi; chatdan o‘rganilgan yoki zamonaviy street slang sifatida berilmaydi.',
})
print('20 provisional source-backed discourse cards; zero readable chat messages; seven additional book pages.')
