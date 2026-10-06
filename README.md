# Eshqo‘zi

O‘zbek shevalarida suhbatlashadigan Telegram bot. Foydalanuvchi hudud va ohangni tanlaydi; bot shu tanlovni saqlaydi, manbali sheva kartalarini topadi va ularni AI javobiga tayanch qilib beradi.

**13 profil, 1 204 bilim kartasi:** adabiy o‘zbekcha, Surxondaryo, Qashqadaryo, Samarqand, Buxoro, Jizzax, Andijon, Farg‘ona, Namangan, Toshkent, Xorazm, Toshkent ko‘cha va Xorazm ko‘cha. Xorazm ko‘cha profili sinov bosqichida; uning zamonaviy chat dalili hali yetarli emas.

Python 3.12, FastAPI, HTTPX, SQLite WAL va FTS5. Bitta bot jarayoni ichida to‘rtta ishchi xabarlarni qayta ishlaydi. Bilim bazasi repoda saqlangan; bot ishlashi uchun oldingi `/workspace/research` katalogi talab qilinmaydi. To‘liq chat eksportlari va suhbatdoshlarning shaxsiy metama’lumotlari repoga kiritilmagan.

## Mahalliy sinov

```sh
uv sync --frozen --cache-dir /tmp/eshqozi-uv-cache --link-mode copy
.venv/bin/python -m eshqozi init
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m eshqozi serve
```

Sinov rejimi kalitlarsiz ishlaydi. Mahalliy HTTP port 8000da sheva tanlash va ma’no izlash interfeysi mavjud. Bu rejimdagi javoblar aniq belgilangan manbali demonstratsiya; AI bilan erkin suhbat deb ko‘rsatilmaydi. Holat tekshiruvlari: `GET /healthz`, `GET /readyz`, `GET /api/dialects`.

## Telegramga ulash

```sh
cp .env.example .env
# .env ichida ESHQOZI_MODE=production va ikki kalitni sozlang.
.venv/bin/python -m eshqozi serve
```

Kerakli sirlar:

| Nomi | Vazifasi |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram BotFather orqali yaratilgan botning tokeni. |
| `ESHQOZI_AI_KEY` | OpenAI API kaliti; faqat AI xizmatiga yuboriladi. |

`OPENAI_API_KEY` mahalliy muhit uchun muqobil nom sifatida ham o‘qiladi. Cloud muhitining sir sozlamalarida `OPENAI_` prefiksi rezervlanganligi uchun asosiy nom `ESHQOZI_AI_KEY`. Kalitlarni Gitga yoki chatga yozmang; cloud muhitida xavfsiz environment settings orqali kiriting. Sozlamada kalitlarning borligi yoki qoralama saqlanishi jonli xizmat tekshirildi degani emas.

Model standart qiymati `gpt-4.1-mini`; `OPENAI_MODEL` bilan o‘zgartiriladi. `OPENAI_BASE_URL` OpenAI bilan mos HTTPS xizmatni ko‘rsatishi mumkin. Tanlangan model Chat Completions, `temperature` va `max_tokens` parametrlarini qo‘llashi kerak.

Bot shaxsiy Telegram chatlarda ishlaydi. `/start`, `/sheva`, `/uslub`, `/manba`, `/clear`, `/forget`, `/help` buyruqlari va inline tugmalar mavjud. Har AI javobiga 👍/👎 baho berish mumkin. Tashqi APIga ulanish uchun `api.telegram.org` va `api.openai.com` ochiq bo‘lishi kerak. Avvaldan o‘rnatilgan webhook aniqlansa bot uni o‘zi o‘chirib yubormaydi.

## Docker

```sh
docker compose up -d --build
docker compose logs --tail=50 bot
```

Port faqat hostning loopback manziliga bog‘langan, baza `bot-data` volume’da. Konteyner root sifatida ishlamaydi, root fayl tizimi o‘qish rejimida. Kalitlar tasvirga qo‘shilmaydi. Bitta SQLite volume uchun bitta bot nusxasi kerak.

Ushbu cloud muhitida Docker build ichidagi DNS ishlamagani sabab xeshlari tekshirilgan wheel paketlaridan yig‘ish yo‘li ham bor:

```sh
sh scripts/build_offline.sh
docker compose up -d --no-build
```

Bu yo‘l TLS va paket xeshlarini tekshirishni saqlaydi. Python bazasi digest bilan, barcha Python paketlari `uv.lock` va `requirements.lock` bilan mahkamlangan. Oddiy internetli muhit uchun online Docker build yo‘li mavjud; cloudda tekshirilgan yo‘l offline builddir.

## Zaxiralash

```sh
.venv/bin/python -m eshqozi backup --destination var/backups/eshqozi.sqlite3
```

Compose’da alohida xizmat kunlik backup va 7 kunlik retentionni avtomatik bajaradi. SQLite online backup ishlatiladi: faol WAL bazasini oddiy `cp` bilan nusxalash kerak emas. Zaxira suhbat ma’lumotlarini ham saqlaydi; saqlash muddati va kirish huquqini operator boshqaradi. Batafsil tiklash tartibi [ishga tushirish yo‘riqnomasi](docs/OPERATIONS.md)da.

## Arxitektura va dalil sifati

[Arxitektura](docs/ARCHITECTURE.md), [operatsion yo‘riqnoma](docs/OPERATIONS.md), [bilim bazasi siyosati](docs/KNOWLEDGE.md), [tekshiruv natijasi](docs/VALIDATION.md).

Bu model vaznlarini qayta o‘qitish emas: manbalar javob yaratish paytida tanlab beriladi. Kitobdagi qayd zamonaviy kundalik nutq yoki butun viloyat aholisining bir xil shevasini tasdiqlamaydi. Avtomatik testlar integratsiya va ma’no tayanchlari izchilligini tekshiradi; mahalliy so‘zlovchining tabiiylik bahosini almashtirmaydi.
