import httpx


class UpstreamError(Exception):
    def __init__(self, code: str, *, retryable: bool = True, retry_after: float = 0):
        super().__init__(code)
        self.code = code
        self.retryable = retryable
        self.retry_after = min(max(retry_after,0),3600)


def parse_update(update: dict):
    message = update.get('message')
    callback = update.get('callback_query')
    if isinstance(callback,dict):
        message = callback.get('message')
        sender = callback.get('from',{})
    elif isinstance(message,dict):
        sender = message.get('from',{})
    else:
        return None
    if not isinstance(message,dict):
        return None
    chat = message.get('chat',{})
    if not isinstance(chat,dict) or not isinstance(sender,dict):
        return None
    chat_id = chat.get('id')
    if chat.get('type') != 'private' or type(chat_id) is not int or chat_id <= 0 or sender.get('id') != chat_id or sender.get('is_bot'):
        return None
    text = message.get('text') if callback is None else ''
    return {'chat_id':chat_id,'text':text if isinstance(text,str) else '',
            'callback_data':callback.get('data','') if callback and isinstance(callback.get('data'),str) else '',
            'callback_id':callback.get('id') if callback and isinstance(callback.get('id'),str) else None,
            'unsupported_media':callback is None and not isinstance(text,str)}


def split_text(text: str, limit: int = 3500):
    """Telegram limitini UTF-16 birliklarida ham buzmaydi."""
    parts, chunk, size = [], [], 0
    for char in text:
        width = 2 if ord(char)>0xffff else 1
        if size+width > limit:
            parts.append(''.join(chunk))
            chunk, size = [], 0
        chunk.append(char)
        size += width
    if chunk:
        parts.append(''.join(chunk))
    return parts or ['…']


class Telegram:
    def __init__(self, client: httpx.AsyncClient, token: str, base_url: str = 'https://api.telegram.org'):
        self.client = client
        self.base = base_url.rstrip('/')+'/bot'+token

    async def call(self, method: str, payload: dict, timeout: float = 40):
        try:
            response = await self.client.post(self.base+'/'+method,json=payload,timeout=timeout)
        except httpx.HTTPError:
            raise UpstreamError('telegram_transport') from None
        try:
            data = response.json()
        except ValueError:
            raise UpstreamError('telegram_invalid_json') from None
        if not isinstance(data,dict) or not data.get('ok'):
            code = int(data.get('error_code',response.status_code)) if isinstance(data,dict) else response.status_code
            retry = data.get('parameters',{}).get('retry_after',0) if isinstance(data,dict) else 0
            raise UpstreamError(f'telegram_{code}',retryable=code==429 or code>=500,retry_after=float(retry))
        return data.get('result')

    async def validate(self):
        me = await self.call('getMe',{})
        if not isinstance(me,dict) or not me.get('is_bot'):
            raise UpstreamError('telegram_invalid_bot',retryable=False)
        webhook = await self.call('getWebhookInfo',{})
        if isinstance(webhook,dict) and webhook.get('url'):
            raise UpstreamError('telegram_existing_webhook',retryable=False)

    async def poll(self, offset: int):
        result = await self.call('getUpdates',{'offset':offset,'timeout':25,'limit':100,
                  'allowed_updates':['message','callback_query']},timeout=35)
        if not isinstance(result,list):
            raise UpstreamError('telegram_invalid_updates')
        return result

    async def send(self, chat_id: int, message: dict):
        return await self.call('sendMessage',{'chat_id':chat_id,**message})

    async def acknowledge(self, callback_id: str, text: str):
        try:
            await self.call('answerCallbackQuery',{'callback_query_id':callback_id,'text':text[:180]})
        except UpstreamError as exc:
            # Eski callback javobining xatosi asosiy sendMessage'ni to‘xtatmaydi.
            if exc.retryable:
                raise
