import asyncio
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
import os

from fastapi.testclient import TestClient
import httpx

from eshqozi.app import create_app
from eshqozi.backup import snapshot
from eshqozi.config import Settings
from eshqozi.engine import Engine
from eshqozi.knowledge import Knowledge, normalize
from eshqozi.providers import DemoProvider, OpenAIProvider, prompt, clean_answer
from eshqozi.runtime import Runtime
from eshqozi.storage import Store
from eshqozi.telegram import Telegram, UpstreamError, parse_update, split_text

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = str(ROOT/'data/knowledge.json')


def update(uid, chat=101, text='salom'):
    return {'update_id':uid,'message':{'chat':{'id':chat,'type':'private'},'from':{'id':chat,'is_bot':False},'text':text}}


class Fixture:
    def init(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = Settings(db_path=str(Path(self.tmp.name)/'bot.sqlite3'),knowledge_path=BUNDLE)
        self.store = Store(self.settings.db_path)
        self.store.migrate()
        self.kb = Knowledge(self.store,BUNDLE)

    def cleanup(self):
        self.tmp.cleanup()


class StorageTests(Fixture,unittest.TestCase):
    def setUp(self): self.init()
    def tearDown(self): self.cleanup()

    def test_migration_and_import_repeat_without_duplicates(self):
        self.store.migrate()
        Knowledge(self.store,BUNDLE)
        self.assertEqual(self.store.status()['cards'],1511)
        self.assertEqual(len(self.kb.profiles),13)

    def test_duplicate_batch_and_offset_are_durable(self):
        self.assertEqual(self.store.enqueue_batch([update(1),update(2)]),2)
        self.assertEqual(self.store.enqueue_batch([update(1),update(2)]),0)
        self.assertEqual(Store(self.settings.db_path).offset(),2)

    def test_unsupported_group_advances_offset_without_job(self):
        u=update(3)
        u['message']['chat']['type']='supergroup'
        self.assertEqual(self.store.enqueue_batch([u]),0)
        self.assertEqual(self.store.offset(),3)
        self.assertIsNone(self.store.claim())

    def test_per_chat_order_and_parallel_different_chats(self):
        self.store.enqueue_batch([update(1,101),update(2,101),update(3,202)])
        self.assertEqual(self.store.claim()['update_id'],1)
        self.assertEqual(self.store.claim()['update_id'],3)
        self.assertIsNone(self.store.claim())
        self.store.finish(1)
        self.assertEqual(self.store.claim()['update_id'],2)

    def test_retry_delay_blocks_later_message_same_chat(self):
        self.store.enqueue_batch([update(1),update(2)])
        self.store.claim()
        self.store.retry(1,60,'telegram_429')
        self.assertIsNone(self.store.claim())

    def test_expired_lease_recovers(self):
        self.store.enqueue_batch([update(1)])
        self.store.claim()
        with self.store.connection(write=True) as c:
            c.execute('UPDATE inbox SET leased_until=0')
        self.assertEqual(self.store.claim()['attempts'],2)

    def test_rate_limits_survive_restart_and_retry_cost_counted(self):
        self.assertTrue(self.store.reserve(1,101,1,10,2))
        self.assertFalse(Store(self.settings.db_path).reserve(2,101,1,10,2))
        self.assertTrue(self.store.reserve(1,101,1,10,2))
        self.assertFalse(self.store.reserve(1,101,1,10,2))

    def test_forget_does_not_reset_global_budget(self):
        self.assertTrue(self.store.reserve(1,101,8,100,1))
        self.store.forget(101)
        self.assertFalse(self.store.reserve(2,101,8,100,1))

    def test_backup_restores_knowledge_and_preferences(self):
        self.store.preference(101,dialect='xorazm')
        backup=str(Path(self.tmp.name)/'backup.sqlite3')
        self.store.backup(backup)
        restored=Store(backup)
        self.assertEqual(restored.user(101)['dialect'],'xorazm')
        self.assertEqual(restored.status()['cards'],1511)

    def test_cleanup_removes_expired_sensitive_turns(self):
        self.store.user(101)
        with self.store.connection(write=True) as c:
            c.execute('INSERT INTO turns VALUES(?,?,?,?,?,?)',('old',101,'private','answer','[]',time.time()-73*3600))
        self.store.cleanup(72)
        self.assertEqual(self.store.history(101,6,100),[])

    def test_scheduled_snapshot_is_consistent_and_rotates_old_backup(self):
        folder=Path(self.tmp.name)/'backups';folder.mkdir()
        old=folder/'eshqozi-old.sqlite3';old.write_text('obsolete')
        os.utime(old,(time.time()-8*86400,time.time()-8*86400))
        result=snapshot(self.store,str(folder),7)
        self.assertTrue(result.is_file());self.assertFalse(old.exists())
        with sqlite3.connect(result) as con:self.assertEqual(con.execute('SELECT count(*) FROM cards').fetchone()[0],1511)


class KnowledgeTests(Fixture,unittest.TestCase):
    def setUp(self): self.init()
    def tearDown(self): self.cleanup()

    def test_xorazm_polysemy_preserved(self):
        rows=self.kb.retrieve('xorazm','barak nima?')
        forms=[r for r in rows if r['form'].startswith('barak')]
        self.assertTrue(any('chuchvara' in r['meaning'] for r in forms))
        self.assertTrue(any('kelin' in r['meaning'] for r in forms))

    def test_cyrillic_query_matches_latin_card(self):
        rows=self.kb.retrieve('xorazm','питта нима?')
        self.assertTrue(any('pitta' in r['form'] for r in rows))

    def test_fts_untrusted_punctuation_does_not_become_query_syntax(self):
        self.kb.retrieve('xorazm','" OR * ) NEAR(foo)');self.kb.retrieve('xorazm','💚')

    def test_retrieval_isolates_other_regions(self):
        self.assertTrue(all(r['dialect']=='namangan' for r in self.kb.retrieve('namangan','aka nima?')))

    def test_street_trial_only_uses_own_region(self):
        rows=self.kb.retrieve('xorazm_kocha','dim nima?')
        self.assertTrue(all(r['dialect'] in {'xorazm_kocha','xorazm'} for r in rows))
        self.assertTrue(self.kb.profile('xorazm_kocha')['trial'])

    def test_bundle_excludes_raw_chat_identity_and_local_paths(self):
        raw=Path(BUNDLE).read_text()
        for forbidden in ('/workspace/','original_json_path','author_code','message_id','from_id','phone_number'):
            self.assertNotIn(forbidden,raw)

    def test_prompt_marks_context_as_data_and_tone_is_explicit(self):
        text=prompt(self.kb.profile('xorazm'),'dostona',self.kb.retrieve('xorazm','pitta'))
        self.assertIn('buyruq',text)
        self.assertIn('Do‘stlar',text)
        self.assertIn('ozgina',text)

    def test_prior_research_reaches_runtime_with_its_limits(self):
        bundle=json.loads(Path(BUNDLE).read_text())
        kinds={name:sum(c['kind']==name for c in bundle['cards']) for name in ('lexicon','grammar','phonetics','example')}
        self.assertEqual(kinds,{'lexicon':1017,'grammar':187,'phonetics':210,'example':97})
        self.assertEqual(len(bundle['provenance']['skipped_untranslated_examples']),9)
        xiva=self.kb.context_profile('xorazm','Xiva shevasida qanday?')
        self.assertTrue(any('Xiva' in v['name'] for v in xiva['local_variant']))
        self.assertFalse(self.kb.context_profile('xorazm','Nima gap?')['local_variant'])
        self.assertFalse(xiva['voice']['all_xorazm_represented_by_default'])
        self.assertFalse(xiva['voice']['regional_separation']==[])
        street=self.kb.context_profile('xorazm_kocha','Nima gap?')
        self.assertTrue(street['trial'])
        self.assertEqual(street['voice']['new_modern_street_slang_cards'],0)
        self.assertIn('morphology_policy',street['regional_voice'])
        tash=self.kb.context_profile('toshkent_kocha','Qales, nma gap?')
        self.assertFalse(tash['voice']['current_2026_usage_verified'])
        self.assertTrue(tash['voice']['interaction_patterns'])
        p=prompt(street,'dostona',self.kb.retrieve('xorazm_kocha','pitta nima?'))
        self.assertIn('Toshkent ko‘cha kartalarini unga qo‘shma',p)
        self.assertNotIn('/workspace/',p)

    def test_phonetic_and_example_cards_are_sourced_but_not_global_rules(self):
        phonetics=[c for c in self.kb.retrieve('namangan','mālim umlaut talaffuz') if c['kind']=='phonetics']
        self.assertTrue(phonetics)
        self.assertTrue(all(not c['meta']['audio_verified'] for c in phonetics))
        examples=[c for c in self.kb.retrieve('xorazm','nutq namunasi qanday?') if c['kind']=='example']
        self.assertTrue(examples)
        self.assertTrue(all('bugungi umumiy nutq' in c['note'] for c in examples))

    def test_dialect_output_preserves_research_word_and_person_limits(self):
        xor=self.kb.context_profile('xorazm','Xivada aka nima?')
        self.assertEqual(clean_answer(xor,'Xivada aka nima?',
            'Aka ota, dada ma’nosida ishlatiladi, brat.'),
            'Aka ota, dada ma’nosida ishlatiladi.')
        street=self.kb.context_profile('xorazm_kocha','Salom ber')
        self.assertEqual(clean_answer(street,'Salom ber','Assalom, barakmi?'),
                         'Assalom, yaxshimi?')
        tash=self.kb.context_profile('toshkent_kocha','Qales?')
        self.assertEqual(clean_answer(tash,'Qales?','Sen qvotti?'),'sen qvosan?')


class ParserTests(unittest.TestCase):
    def test_private_sender_ownership(self):
        u=update(1);u['message']['from']['id']=999
        self.assertIsNone(parse_update(u))

    def test_malformed_nested_update(self):
        self.assertIsNone(parse_update({'message':{'chat':None,'from':None}}))
        self.assertIsNone(parse_update({'callback_query':{'message':None}}))

    def test_media_event_is_explicit(self):
        u=update(1);del u['message']['text'];u['message']['photo']=[]
        self.assertTrue(parse_update(u)['unsupported_media'])

    def test_emoji_split_obeys_utf16_limit_and_preserves_content(self):
        text='🙂'*5000+'x'*3000
        parts=split_text(text)
        self.assertEqual(''.join(parts),text)
        self.assertTrue(all(len(p.encode('utf-16-le'))//2<=3500 for p in parts))


class EngineTests(Fixture,unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.init();self.engine=Engine(self.settings,self.store,self.kb,DemoProvider())
    def tearDown(self): self.cleanup()

    async def process(self,text,uid=1,chat=101,callback=''):
        prepared=await self.engine.prepare({'chat_id':chat,'text':text,'callback_data':callback},uid)
        if prepared.turn:self.store.save_response(uid,prepared.response,prepared.turn)
        return prepared

    async def test_start_has_13_choices_and_privacy_controls(self):
        p=await self.process('/start')
        self.assertIn('/forget',p.response['messages'][0]['text'])
        buttons=p.response['messages'][-1]['reply_markup']['inline_keyboard']
        self.assertEqual(sum(map(len,buttons)),13)

    async def test_selection_is_persistent_and_resets_old_history(self):
        await self.process('salom')
        await self.process('',2,callback='d:xorazm')
        self.assertEqual(self.store.user(101)['dialect'],'xorazm')
        self.assertEqual(self.store.history(101,6,72),[])

    async def test_meaning_and_source_command(self):
        await self.process('',1,callback='d:xorazm')
        p=await self.process('pitta nima?',2)
        self.assertIn('ozgina',p.turn['answer'])
        source=await self.process('/manba',3)
        self.assertIn('Xorazm shevalari lug‘ati',source.response['messages'][0]['text'])

    async def test_clear_preserves_dialect(self):
        self.store.preference(101,dialect='xorazm')
        await self.process('pitta nima?',1)
        await self.process('/clear',2)
        self.assertEqual(self.store.user(101)['dialect'],'xorazm')
        self.assertEqual(self.store.history(101,6,72),[])

    async def test_forget_removes_preferences_history_feedback(self):
        p=await self.process('salom',1)
        self.assertTrue(self.store.feedback(101,p.turn['id'],1))
        await self.process('/forget',2)
        with self.store.connection() as c:
            for table in ('users','turns','feedback','usage'):
                self.assertEqual(c.execute(f'SELECT count(*) FROM {table}').fetchone()[0],0)

    async def test_feedback_cannot_target_other_chat(self):
        p=await self.process('salom',1)
        self.assertFalse(self.store.feedback(202,p.turn['id'],-1))
        self.assertTrue(self.store.feedback(101,p.turn['id'],-1))

    async def test_long_input_never_calls_provider(self):
        p=await self.process('x'*4001)
        self.assertIsNone(p.turn)
        self.assertIn('uzun',p.response['messages'][0]['text'])

    async def test_user_history_isolated(self):
        await self.process('private 101',1,101)
        await self.process('private 202',2,202)
        self.assertEqual(self.store.history(101,6,72)[0]['question'],'private 101')
        self.assertEqual(self.store.history(202,6,72)[0]['question'],'private 202')


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_openai_http_contract_history_and_source_context(self):
        captured=[]
        def handle(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200,json={'choices':[{'message':{'content':'Assalom!'}}]})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            provider=OpenAIProvider(client,'test-key','model','https://api.openai.com/v1')
            result=await provider.answer({'id':'xorazm'},'samimiy',[],[{'question':'old','answer':'reply'}],'new')
        self.assertEqual(result,'Assalom!')
        self.assertEqual([m['role'] for m in captured[0]['messages']],['system','user','assistant','user'])
        self.assertEqual(captured[0]['messages'][-1]['content'],'new')

    async def test_openai_429_retry_and_key_not_in_error(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(429,headers={'retry-after':'7'},json={}))) as client:
            provider=OpenAIProvider(client,'test-secret','model','https://api.openai.com/v1')
            with self.assertRaises(UpstreamError) as cm:
                await provider.answer({},'samimiy',[],[],'salom')
        self.assertEqual(cm.exception.retry_after,7)
        self.assertNotIn('test-secret',str(cm.exception))

    async def test_invalid_llm_success_response_is_retried(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'choices':[]}))) as client:
            with self.assertRaises(UpstreamError):
                await OpenAIProvider(client,'key','model','https://api.openai.com/v1').answer({},'samimiy',[],[],'hi')

    async def test_existing_webhook_is_not_deleted(self):
        methods=[]
        def handle(request):
            method=request.url.path.rsplit('/',1)[-1];methods.append(method)
            return httpx.Response(200,json={'ok':True,'result':{'is_bot':True} if method=='getMe' else {'url':'https://example.test/webhook'}})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            with self.assertRaises(UpstreamError) as cm:await Telegram(client,'token').validate()
        self.assertEqual(cm.exception.code,'telegram_existing_webhook')
        self.assertNotIn('deleteWebhook',methods)


class RuntimeTests(Fixture,unittest.IsolatedAsyncioTestCase):
    def setUp(self):self.init()
    def tearDown(self):self.cleanup()

    async def test_delivery_retry_does_not_regenerate_llm_answer(self):
        class Spy:
            calls=0
            async def answer(self,*args):self.calls+=1;return 'Javob'
        spy=Spy();requests=[]
        def handler(request):
            requests.append(request)
            if len(requests)==1:return httpx.Response(429,json={'ok':False,'error_code':429,'parameters':{'retry_after':1}})
            return httpx.Response(200,json={'ok':True,'result':{'message_id':7}})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            runtime=Runtime(Engine(self.settings,self.store,self.kb,spy),Telegram(client,'token'))
            self.store.enqueue_batch([update(1)])
            await runtime.process(self.store.claim())
            with self.store.connection(write=True) as c:c.execute('UPDATE inbox SET next_attempt=0')
            await runtime.process(self.store.claim())
        self.assertEqual(spy.calls,1)
        self.assertEqual(self.store.status()['queued'],0)
        self.assertEqual(len(self.store.history(101,6,72)),1)

    async def test_partial_send_resumes_from_cursor(self):
        class Spy:
            calls=0
            async def answer(self,*args):self.calls+=1;return 'x'*5000
        spy=Spy();lengths=[]
        def handler(request):
            payload=json.loads(request.content);lengths.append(len(payload['text']))
            if len(lengths)==2:return httpx.Response(500,json={'ok':False,'error_code':500})
            return httpx.Response(200,json={'ok':True,'result':{}})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            runtime=Runtime(Engine(self.settings,self.store,self.kb,spy),Telegram(client,'token'))
            self.store.enqueue_batch([update(1)])
            await runtime.process(self.store.claim())
            with self.store.connection(write=True) as c:c.execute('UPDATE inbox SET next_attempt=0')
            await runtime.process(self.store.claim())
        self.assertEqual(lengths,[3500,1500,1500])
        self.assertEqual(spy.calls,1)

    async def test_failed_forget_delivery_still_removes_user_record(self):
        self.store.user(101)
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(403,json={'ok':False,'error_code':403}))) as client:
            runtime=Runtime(Engine(self.settings,self.store,self.kb,DemoProvider()),Telegram(client,'token'))
            self.store.enqueue_batch([update(1,text='/forget')])
            await runtime.process(self.store.claim())
        with self.store.connection() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM users').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM inbox').fetchone()[0],0)

    async def test_singleton_lock_prevents_two_pollers(self):
        one=Runtime(Engine(self.settings,self.store,self.kb,DemoProvider()),None)
        two=Runtime(Engine(self.settings,self.store,self.kb,DemoProvider()),None)
        await one.start()
        try:
            with self.assertRaises(RuntimeError):await two.start()
        finally:await one.stop()


class HTTPTests(Fixture,unittest.TestCase):
    def setUp(self):self.init()
    def tearDown(self):self.cleanup()

    def test_demo_http_flow_and_cookie(self):
        with TestClient(create_app(self.settings)) as client:
            self.assertEqual(client.get('/healthz').status_code,200)
            self.assertEqual(client.get('/readyz').status_code,200)
            self.assertEqual(len(client.get('/api/dialects').json()),13)
            r=client.post('/api/demo',json={'text':'pitta nima?','dialect':'xorazm'})
            self.assertIn('ozgina',r.json()['messages'][0]['text'])
            self.assertIn('eshqozi_demo',client.cookies)
            r=client.post('/api/demo',json={'text':'/forget'})
            self.assertEqual(r.status_code,200)
            self.assertNotIn('eshqozi_demo',client.cookies)

    def test_invalid_dialect_and_input(self):
        with TestClient(create_app(self.settings)) as client:
            self.assertEqual(client.post('/api/demo',json={'text':'hi','dialect':'unknown'}).status_code,422)
            self.assertEqual(client.post('/api/demo',json={'text':'x'*4001}).status_code,422)

    def test_page_escapes_messages_in_browser(self):
        with TestClient(create_app(self.settings)) as client:
            html=client.get('/').text
            self.assertIn('n.textContent=text',html)
            self.assertNotIn('innerHTML',html)

    def test_production_end_to_end_with_mocked_remote_services(self):
        sent=[];model_requests=[];polled=False
        callback={'update_id':2,'callback_query':{'id':'cb2','from':{'id':101,'is_bot':False},
            'message':{'chat':{'id':101,'type':'private'}},'data':'d:xorazm'}}
        def handle(request):
            nonlocal polled
            method=request.url.path.rsplit('/',1)[-1]
            if method=='getMe':result={'is_bot':True}
            elif method=='getWebhookInfo':result={'url':''}
            elif method=='getUpdates':
                result=[] if polled else [update(1,text='/start'),callback,update(3,text='pitta nima?')]
                polled=True
            elif method=='chat':raise AssertionError('Wrong OpenAI route')
            elif method=='completions':
                model_requests.append(json.loads(request.content))
                return httpx.Response(200,json={'choices':[{'message':{'content':'Pitta — ozgina.'}}]})
            elif method=='sendMessage':sent.append(json.loads(request.content));result={'message_id':len(sent)}
            elif method=='answerCallbackQuery':result=True
            else:raise AssertionError(method)
            return httpx.Response(200,json={'ok':True,'result':result})
        settings=replace(self.settings,mode='production',telegram_token='test-token',openai_key='test-key')
        with TestClient(create_app(settings,transport=httpx.MockTransport(handle))) as client:
            deadline=time.time()+3
            while len(sent)<3 and time.time()<deadline:time.sleep(0.03)
            self.assertEqual(len(sent),3)
            self.assertIn('Pitta',sent[-1]['text'])
            self.assertEqual(len(model_requests),1)
            self.assertIn('ozgina',model_requests[0]['messages'][0]['content'])
            self.assertEqual(client.get('/readyz').status_code,200)
            self.assertEqual(client.post('/api/demo',json={'text':'hi'}).status_code,404)
            self.assertEqual(client.get('/docs').status_code,404)


class ConfigTests(unittest.TestCase):
    def test_missing_live_credentials_fail_explicitly(self):
        with self.assertRaisesRegex(ValueError,'TELEGRAM_BOT_TOKEN'):
            Settings(mode='production').validate()

    def test_provider_url_must_be_secure(self):
        with self.assertRaises(ValueError):Settings(openai_base_url='http://example.test').validate()

    def test_secret_not_in_config_repr(self):
        self.assertNotIn('test-secret',repr(Settings(openai_key='test-secret',telegram_token='test-secret')))


if __name__=='__main__':unittest.main()
