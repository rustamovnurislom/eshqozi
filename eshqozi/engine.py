from dataclasses import dataclass
import hashlib

from .config import Settings
from .knowledge import Knowledge
from .storage import Store
from .telegram import split_text
from .providers import TONES

HELP = """Men Eshqo‘zi — o‘zbek shevalarida suhbatlashadigan botman.

/sheva — hudud yoki ko‘cha uslubini tanlash
/uslub — samimiy, do‘stona yoki dag‘alroq ohang
/manba — oxirgi javobga berilgan sheva manbalari
/clear — suhbat tarixini o‘chirish
/forget — sozlamalar va shaxsiy ma’lumotlarni o‘chirish
/help — yordam

AI ulangan rejimda xabarlaringiz javob tayyorlash uchun AI xizmatiga yuboriladi. Faol tarix ko‘pi bilan 72 soat, zaxira nusxalari 7 kun saqlanadi. /clear va /forget faol ma’lumotlarni o‘chiradi; zaxiralar muddati tugaganda o‘chadi."""


@dataclass
class Prepared:
    response: dict
    turn: dict | None = None


class Engine:
    def __init__(self, settings: Settings, store: Store, knowledge: Knowledge, provider):
        self.settings,self.store,self.knowledge,self.provider = settings,store,knowledge,provider

    def dialect_keyboard(self):
        buttons = [{'text':p['label'],'callback_data':'d:'+p['id']} for p in self.knowledge.profiles.values()]
        return {'inline_keyboard':[buttons[i:i+2] for i in range(0,len(buttons),2)]}

    def tone_keyboard(self):
        return {'inline_keyboard':[[{'text':label,'callback_data':'t:'+key}] for key,label in
                [('samimiy','Samimiy'),('dostona','Do‘stona'),('dagal','Dag‘alroq')]]}

    @staticmethod
    def reply(text: str, keyboard: dict | None = None, *, acknowledgement: str = 'Qabul qilindi', forget: bool = False):
        messages = [{'text':part} for part in split_text(text)]
        if keyboard:
            messages[-1]['reply_markup'] = keyboard
        return Prepared({'messages':messages,'acknowledgement':acknowledgement,'forget':forget})

    async def prepare(self, event: dict, update_id: int) -> Prepared:
        chat_id = event['chat_id']
        callback = event.get('callback_data','')
        text = event.get('text','').strip()
        if event.get('unsupported_media'):
            return self.reply('Hozir matn orqali suhbatlashaman. Savolingizni yozib yuboring.')
        if callback.startswith('d:'):
            dialect = callback[2:]
            if dialect not in self.knowledge.profiles:
                return self.reply('Bu tanlov mavjud emas. /sheva orqali qayta tanlang.')
            self.store.preference(chat_id,dialect=dialect)
            profile = self.knowledge.profile(dialect)
            result = profile['label']+' tanlandi. Nima haqida gaplashamiz?'
            if profile['trial']:
                result += '\nBu uslub hozircha sinov bosqichida.'
            return self.reply(result)
        if callback.startswith('t:'):
            tone = callback[2:]
            if tone not in TONES:
                return self.reply('Uslub tanlovi eskirgan. /uslub orqali qayta tanlang.')
            self.store.preference(chat_id,tone=tone)
            return self.reply({'samimiy':'Samimiy','dostona':'Do‘stona','dagal':'Dag‘alroq'}[tone]+' ohang tanlandi.')
        if callback.startswith('f:'):
            parts = callback.split(':')
            if len(parts)!=3 or parts[2] not in {'up','down'}:
                return self.reply('Bahoni qabul qilib bo‘lmadi.')
            accepted = self.store.feedback(chat_id,parts[1],1 if parts[2]=='up' else -1)
            return self.reply('Fikringiz uchun rahmat!' if accepted else 'Bu javobga baho berish muddati tugagan.')
        if callback:
            return self.reply('Tugma eskirgan. /help orqali davom eting.')
        command = text.split()[0].split('@')[0].casefold() if text.startswith('/') else ''
        if command in {'/start','/help'}:
            prefix = 'Sinov rejimi: AI xizmati ulanmagan.\n\n' if self.settings.mode=='demo' else ''
            help_text = HELP.replace('72 soat',f'{self.settings.retention_hours} soat')
            help_text = help_text.replace('7 kun',f'{self.settings.backup_days} kun')
            return self.reply(prefix+help_text,self.dialect_keyboard())
        if command in {'/sheva','/dialect'}:
            return self.reply('Qaysi uslubda gaplashamiz?',self.dialect_keyboard())
        if command == '/uslub':
            return self.reply('Suhbat ohangini tanlang.',self.tone_keyboard())
        if command == '/clear':
            self.store.clear(chat_id)
            return self.reply('Suhbat tarixi o‘chirildi. Tanlagan shevangiz saqlandi.')
        if command == '/forget':
            self.store.forget(chat_id,current_update=update_id)
            return self.reply('Sozlamalaringiz, suhbat tarixi va baholaringiz o‘chirildi. /start bilan yangidan boshlashingiz mumkin.',forget=True)
        if command == '/manba':
            cards = self.store.last_sources(chat_id)
            if not cards:
                return self.reply('Hali ko‘rsatiladigan sheva manbasi yo‘q. Avval hududni tanlab, savol yozing.')
            lines = ['Oxirgi javobni tayyorlashga berilgan sheva tayanchlari:']
            seen = set()
            for card in cards:
                for evidence in card['evidence']:
                    title = evidence['title']
                    page = evidence.get('pdf_page')
                    line = title+(f' — PDF sahifa {page}' if page else '')
                    if line not in seen:
                        seen.add(line)
                        lines.append('• '+line)
            return self.reply('\n'.join(lines[:10])+'\n\nBu sheva tayanchlari javobdagi har bir umumiy faktning manbasi degani emas.')
        if command:
            return self.reply('Bu buyruq mavjud emas. /help orqali buyruqlarni ko‘ring.')
        if not text:
            return self.reply('Savolingizni matn qilib yozing.')
        if len(text)>self.settings.max_input_chars:
            return self.reply(f'Xabaringiz uzun. Uni {self.settings.max_input_chars} belgidan kichik qismlarga bo‘lib yuboring.')
        if not self.store.reserve(update_id,chat_id,self.settings.per_minute,self.settings.per_day,self.settings.global_per_day):
            return self.reply('Hozirgi xabar limiti tugadi. Birozdan keyin yana yozing.')
        user = self.store.user(chat_id)
        profile = self.knowledge.context_profile(user['dialect'],text)
        cards = self.knowledge.retrieve(profile['id'],text)
        history = self.store.history(chat_id,self.settings.history_turns,self.settings.retention_hours)
        answer = await self.provider.answer(profile,user['tone'],cards,history,text)
        turn_id = hashlib.sha256(f'{chat_id}:{update_id}'.encode()).hexdigest()[:20]
        keyboard = {'inline_keyboard':[[{'text':'👍','callback_data':f'f:{turn_id}:up'},
                                      {'text':'👎','callback_data':f'f:{turn_id}:down'}]]}
        prepared = self.reply(answer,keyboard)
        prepared.turn = {'id':turn_id,'chat_id':chat_id,'question':text,'answer':answer,
                         'sources':[{k:c[k] for k in ('id','form','meaning','evidence')} for c in cards]}
        return prepared
