import asyncio
import fcntl
import logging
from pathlib import Path
import time

from .engine import Engine
from .telegram import Telegram, UpstreamError

log = logging.getLogger('eshqozi')


class Runtime:
    def __init__(self, engine: Engine, telegram: Telegram | None):
        self.engine,self.telegram = engine,telegram
        self.store,self.settings = engine.store,engine.settings
        self.tasks = []
        self.last_poll = 0.0
        self.last_error = None
        self.stopping = False
        self.lock = None

    async def start(self):
        self.lock = open(self.settings.db_path+'.lock','a')
        try:
            fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            self.lock = None
            raise RuntimeError('Shu bazada boshqa Eshqo‘zi jarayoni ishlayapti') from None
        try:
            if self.telegram:
                await self.telegram.validate()
                with self.store.connection(write=True) as con:
                    con.execute("UPDATE inbox SET status='queued',leased_until=0 WHERE status='running'")
                self.tasks = [asyncio.create_task(self.poller(),name='telegram-poller')]
                self.tasks.extend(asyncio.create_task(self.worker(),name=f'worker-{i}') for i in range(self.settings.workers))
            self.tasks.append(asyncio.create_task(self.janitor(),name='retention'))
        except BaseException:
            self.lock.close()
            self.lock = None
            raise

    async def stop(self):
        self.stopping = True
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks,return_exceptions=True)
        if self.lock:
            self.lock.close()
            self.lock = None

    async def poller(self):
        delay = 1
        while not self.stopping:
            try:
                updates = await self.telegram.poll(self.store.offset()+1)
                self.store.enqueue_batch(updates)
                self.last_poll = time.monotonic()
                self.last_error = None
                delay = 1
                if not updates:
                    await asyncio.sleep(0.1)
            except UpstreamError as exc:
                self.last_error = exc.code
                log.warning('poll_failed code=%s',exc.code)
                await asyncio.sleep(max(exc.retry_after,delay))
                delay = min(delay*2,30)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.last_error = 'poll_internal'
                log.error('poll_failed type=%s',type(exc).__name__)
                await asyncio.sleep(5)

    async def process(self, job: dict):
        update_id = job['update_id']
        event = job['event']
        response = job['response']
        try:
            if response is None:
                try:
                    prepared = await self.engine.prepare(event,update_id)
                except UpstreamError as exc:
                    if exc.retryable and job['attempts'] < self.settings.max_attempts:
                        raise
                    prepared = self.engine.reply('Javob xizmatida vaqtinchalik muammo bor. Birozdan keyin qayta yozing.')
                    log.warning('generation_failed code=%s',exc.code)
                response = prepared.response
                self.store.save_response(update_id,response,prepared.turn,self.settings.history_turns)
                # Yaratish va yetkazish qayta urinishlari uchun alohida limit.
                job['attempts'] = 1
            if event.get('callback_id'):
                await self.telegram.acknowledge(event['callback_id'],response['acknowledgement'])
            for index in range(job['send_cursor'],len(response['messages'])):
                self.store.heartbeat(update_id,self.settings.lease_seconds)
                await self.telegram.send(event['chat_id'],response['messages'][index])
                self.store.sent(update_id,index+1)
            self.store.finish(update_id,forget=response.get('forget',False))
        except UpstreamError as exc:
            if exc.retryable and job['attempts'] < self.settings.max_attempts:
                self.store.retry(update_id,max(exc.retry_after,min(2**job['attempts'],60)),exc.code)
            else:
                self.store.finish(update_id,failed=True,forget=(response or {}).get('forget',False))
            log.warning('job_failed code=%s',exc.code)
        except asyncio.CancelledError:
            self.store.retry(update_id,0,'shutdown')
            raise
        except Exception as exc:
            if job['attempts'] < self.settings.max_attempts:
                self.store.retry(update_id,min(2**job['attempts'],60),'internal')
            else:
                self.store.finish(update_id,failed=True,forget=(response or {}).get('forget',False))
            log.error('job_failed type=%s',type(exc).__name__)

    async def worker(self):
        while not self.stopping:
            job = self.store.claim(self.settings.lease_seconds)
            if job is None:
                await asyncio.sleep(0.2)
                continue
            await self.process(job)

    async def janitor(self):
        while not self.stopping:
            self.store.cleanup(self.settings.retention_hours)
            await asyncio.sleep(60)

    def ready(self):
        alive = bool(self.tasks) and all(not task.done() for task in self.tasks)
        poll_ok = self.telegram is None or (self.last_poll>0 and time.monotonic()-self.last_poll < 90)
        return alive and poll_ok and self.store.status()['cards']>0
