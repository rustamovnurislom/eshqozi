import asyncio
from contextlib import asynccontextmanager
import hashlib
import hmac
from pathlib import Path
import secrets
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
from pydantic import BaseModel, Field

from .config import Settings
from .engine import Engine
from .knowledge import Knowledge
from .providers import DemoProvider, OpenAIProvider
from .runtime import Runtime
from .storage import Store
from .telegram import Telegram


class DemoRequest(BaseModel):
    text: str = Field(min_length=1,max_length=4000)
    dialect: str | None = None
    tone: Literal['samimiy','dostona','dagal'] = 'samimiy'


def create_app(settings: Settings | None = None, *, transport=None, provider=None):
    settings = settings or Settings.from_env()
    settings.validate()
    store = Store(settings.db_path)
    store.migrate()
    knowledge = Knowledge(store,settings.knowledge_path)
    session_secret = secrets.token_bytes(32)
    demo_locks = {}

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(transport=transport,follow_redirects=False,
                                    limits=httpx.Limits(max_connections=settings.workers+4)) as client:
            chosen = provider or (DemoProvider() if settings.mode=='demo' else OpenAIProvider(client,settings.openai_key,settings.model,settings.openai_base_url))
            engine = Engine(settings,store,knowledge,chosen)
            telegram = None if settings.mode=='demo' else Telegram(client,settings.telegram_token,settings.telegram_base_url)
            runtime = Runtime(engine,telegram)
            app.state.engine,app.state.runtime = engine,runtime
            await runtime.start()
            try:
                yield
            finally:
                await runtime.stop()

    app = FastAPI(title='Eshqo‘zi',version='0.1.0',lifespan=lifespan,
                  docs_url='/docs' if settings.mode=='demo' else None,
                  redoc_url=None,openapi_url='/openapi.json' if settings.mode=='demo' else None)
    app.state.store,app.state.knowledge = store,knowledge

    @app.get('/healthz')
    def health():
        return {'status':'ok','mode':settings.mode}

    @app.get('/readyz')
    def ready():
        runtime = getattr(app.state,'runtime',None)
        available = runtime is not None and runtime.ready()
        return JSONResponse({'ready':available,'mode':settings.mode,'cards':store.status()['cards']},status_code=200 if available else 503)

    @app.get('/api/dialects')
    def dialects():
        return list(knowledge.profiles.values())

    @app.get('/',response_class=HTMLResponse)
    def index():
        if settings.mode!='demo':
            return HTMLResponse('<!doctype html><html lang="uz"><meta charset="utf-8"><title>Eshqo‘zi</title><p>Eshqo‘zi Telegram orqali ishlaydi.</p></html>')
        return HTMLResponse((Path(__file__).parent/'static/index.html').read_text())

    @app.post('/api/demo')
    async def demo(payload: DemoRequest, request: Request, response: Response):
        if settings.mode!='demo':
            raise HTTPException(404)
        if payload.dialect is not None and payload.dialect not in knowledge.profiles:
            raise HTTPException(422,'Bunday sheva mavjud emas')
        token = request.cookies.get('eshqozi_demo','')
        if len(token)!=32 or any(c not in '0123456789abcdef' for c in token):
            token = secrets.token_hex(16)
        chat_id = int.from_bytes(hmac.digest(session_secret,token.encode(),'sha256')[:8],'big') & ((1<<63)-1)
        # Alohida brauzer seansi uchun boshqa chatning sozlamasi ochilmaydi.
        lock = demo_locks.setdefault(chat_id,asyncio.Lock())
        if len(demo_locks)>10000:
            for old in list(demo_locks)[:1000]:
                if old!=chat_id and not demo_locks[old].locked():
                    del demo_locks[old]
        async with lock:
            user = store.user(chat_id)
            if payload.dialect and payload.dialect!=user['dialect']:
                store.preference(chat_id,dialect=payload.dialect)
            store.preference(chat_id,tone=payload.tone)
            update_id = -secrets.randbits(62)-1
            prepared = await app.state.engine.prepare({'chat_id':chat_id,'text':payload.text},update_id)
            if prepared.turn:
                store.save_response(update_id,prepared.response,prepared.turn,settings.history_turns)
        if prepared.response.get('forget'):
            response.delete_cookie('eshqozi_demo')
        else:
            response.set_cookie('eshqozi_demo',token,httponly=True,samesite='strict',max_age=3600)
        return {'messages':prepared.response['messages'],'mode':'demo'}

    return app
