# Loyihani ko‘chirish

Joriy ishchi checkout botning dastur kodlari, HTML interfeysi, SQLite migratsiyasi, 13 profil va 1 511 kartali bilim bazasi, testlari, dependency lockfilelari, Docker/Compose, CI va hujjatlarini o‘z ichiga oladi. Oldingi topshirish arxivlari yaratilgan paytdagi snapshot bo‘lib, ulardagi karta soni farq qilishi mumkin.

## Paket tarkibi

- `eshqozi/` — ishlaydigan repository. Asosiy yo‘riqnoma `README.md`.
- `database/eshqozi-initial.sqlite3` — migratsiyadan o‘tgan, bilim bazasi yuklangan yangi SQLite baza; foydalanuvchi va suhbat yozuvlari yo‘q. Ilova birinchi ishga tushganda bunday bazani o‘zi ham yaratadi.
- `infrastructure/cloud-environment.json` — kalitlarsiz cloud install/startup yo‘riqnomasi, tarmoq domenlari va sir nomlari. Boshqa platformaga avtomatik import qilinadigan format deb talqin qilinmaydi.
- `MANIFEST.json` — paketdagi fayllar ro‘yxati, o‘lchami va SHA-256 xeshi.
- `research/` — kengaytirilgan paketdagi o‘qish natijalari, lug‘atlar, tahlillar, OCR matnlari, tekshirish rasmlari va tadqiqot skriptlari.
- `attachments/` — kengaytirilgan paketdagi original PDFlar; takror yuklangan nomlar alohida kataloglarda saqlangan.

## Sinov rejimini boshlash

Python 3.12 va `uv` talab qilinadi. Arxivni oching, `eshqozi` katalogiga kiring:

```sh
uv sync --frozen --cache-dir /tmp/eshqozi-uv-cache --link-mode copy
ESHQOZI_MODE=demo .venv/bin/python -m eshqozi init
.venv/bin/python -m unittest discover -s tests -v
ESHQOZI_MODE=demo .venv/bin/python -m eshqozi serve
```

Demo rejimi AI ulanmaganligini ochiq ko‘rsatadi. Jonli bot uchun `.env.example`dan `.env` yarating, `ESHQOZI_MODE=production` va ikki sirni xavfsiz sozlang. Cloud muhitida esa mavjud xavfsiz environment bindinglardan foydalaning:

```sh
ESHQOZI_MODE=production .venv/bin/python -m eshqozi serve
```

Kerakli sirlar: `TELEGRAM_BOT_TOKEN`, `ESHQOZI_AI_KEY`. Paketda haqiqiy kalitlar yo‘q. Providerga chiqish uchun `api.telegram.org` va `api.openai.com` ruxsati kerak. Bir token yoki SQLite volume uchun bir bot jarayoni ishlatiladi.

## Docker va doimiy ishlash

```sh
docker compose up -d --build
docker compose logs --tail=50 bot
```

Compose `.env` sozlamalarini o‘qiydi. Jonli xizmat uchun undagi rejimni `production` qiling. Baza persistent volume’da, alohida xizmat har kuni backup yaratadi. Cloud build DNS cheklovida `sh scripts/build_offline.sh` orqali yig‘ish mumkin; avval `.venv`ni o‘rnating. Tafsilotlar `docs/OPERATIONS.md`da.

Cloud ish muhiti doimiy hosting emas: muhit to‘xtasa bot jarayoni ham to‘xtaydi. Uzluksiz bot uchun doimiy Linux server kerak.

## Bazani ishlatish

Odatiy ishga tushirish `var/eshqozi.sqlite3`ni yaratadi va bilim bazasini import qiladi. Paketdagi tayyor boshlang‘ich bazani ishlatmoqchi bo‘lsangiz, bot to‘xtagan va yangi baza hali mavjud bo‘lmagan paytda `database/eshqozi-initial.sqlite3`ni shu joyga nusxalang. Ishlayotgan baza yoki mavjud foydalanuvchi ma’lumotini ustidan yozmang. Dockerda fayl egasi UID/GID 10001 bo‘lishi kerak.

## Tadqiqotni qayta ishlash

Runtime uchun `data/knowledge.json` yetarli. Kengaytirilgan paketdagi research materiallari bilan qayta import qilish uchun:

```sh
.venv/bin/python scripts/import_research.py --research-root ../research --output data/knowledge.json
```

Tadqiqotning eski skriptlarida `/workspace/research` va `/workspace/attachments` yo‘llari saqlangan bo‘lishi mumkin; boshqa kompyuterda ularni moslashtirish zarur. PDF OCR ishlari uchun tashqi PDF/Tesseract vositalari talab qilinishi mumkin; bot runtime’iga ular kerak emas. Chat dalillari olib tashlangan variantdan shaxsiy korpusning barcha hisoblarini qayta tiklab bo‘lmaydi.

## Paketdan chiqarilgan ma’lumotlar

Haqiqiy `.env` va sir qiymatlari, ishchi bazadagi shaxsiy suhbatlar, backup va loglar, `.git`, `.venv`, Python cache fayllari hamda xom Telegram chat eksportlari kiritilmadi. Tadqiqotdagi ko‘cha shevasi JSONlaridan xabar/muallif identifikatorlari va xom chat sitatalari olib tashlandi. Yig‘ma statistikalar va tilga oid tahlillar saqlandi. Aniq chiqarilgan fayllar kengaytirilgan paketning `EXPORT-NOTES.json` faylida ko‘rsatilgan.

Dependencylar lockfilelar orqali qayta o‘rnatiladi; virtual muhitni boshqa kompyuterga nusxalash talab qilinmaydi. Kalitlar faqat environment settings yoki Gitdan tashqaridagi `.env`da saqlanadi.

Hozirgi profil sifatiga oid chegaralar `docs/KNOWLEDGE.md`da, sinov dalillari `docs/VALIDATION.md`da. Xorazm ko‘cha profili sinov bosqichida; avtomatik testlar ona sheva so‘zlovchisining tabiiylik bahosini almashtirmaydi.
