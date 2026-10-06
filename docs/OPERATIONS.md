# Ishga tushirish va xizmatni yuritish

## Birinchi ishga tushirish

Linux, Python 3.12 va lokal persistent disk kerak. `uv sync --frozen` va `python -m eshqozi init` kutubxonalar hamda bazani tayyorlaydi. Demo kalitsiz ishlaydi. Production uchun Telegram bot tokeni va AI kaliti xavfsiz environment settings yoki Gitdan tashqaridagi `.env`ga kiritiladi. `ESHQOZI_MODE=production` tokenlardan biri yo‘q bo‘lsa aniq xato bilan to‘xtaydi.

Standart ishga tushirish: `.venv/bin/python -m eshqozi serve`. Container uchun `docker compose up -d --build`; cloudning Docker DNS cheklovida `sh scripts/build_offline.sh`, keyin `docker compose up -d --no-build`. Offline yo‘l hostda xesh tekshiruvli paketlarni yuklaydi, keyin tarmoqsiz container buildga beradi. TLS va checksum tekshiruvi o‘chirilmaydi.

Clouddagi Docker CLI konfiguratsiyasi read-only katalogga yozishga urinsa `DOCKER_CONFIG=/tmp/eshqozi-docker` qo‘llang. Python cache uchun `/tmp/eshqozi-uv-cache`; `/home`ga yozish talab qilinmaydi. Ikkinchi bot nusxasi ayni bazada ishga tushsa process lock xatosi beradi. Uvicorn ko‘p worker rejimini ishlatmang.

Polling uchun HTTPS outbound `api.telegram.org` va AI provider domeni kerak; inbound ommaviy port shart emas. HTTP holat porti Compose’da faqat host loopback’iga chiqarilgan. Productionda demo chat API va OpenAPI docs o‘chiriladi. Telegramda oldingi webhook bor bo‘lsa operator avval uning qaysi servisga tegishli ekanini tekshiradi; ilova mavjud webhookni o‘zi olib tashlamaydi.

## Holat va xatolar

- `/healthz`: jarayon HTTP so‘rovni qabul qilmoqda.
- `/readyz`: baza va kartalar mavjud, worker tasklari tirik, productionda oxirgi polling 90 soniyadan eski emas.
- `python -m eshqozi check`: lokal baza va profil sonini tekshiradi; tashqi API kalitlarini sinamaydi.

Readiness AI modeli bilan jonli savol-javob o‘tdi degani emas. Kalitlar kiritilgach botga `/start`, profil tanlovi va oddiy savol yuborib real provider javobi tekshiriladi. Hozirgi validation transportlarining tashqi API o‘rniga mock ishlatgani aniq belgilangan.

Loglar matn yoki tokenni saqlamaydi. Misollar: `telegram_429` — Telegram limiti; `openai_401` — AI credential muammosi; `telegram_409` — boshqa polling instance/webhook to‘qnashuvi; `*_transport` — ulanish; `*_invalid_response` — javob formati. Kunlik budjet UTCda yangilanadi. `/forget` umumiy shaxssiz budjetni tiklamaydi.

## Restart va yangilash

`docker compose restart bot` pending xabarlarni diskdan tiklaydi. Yangilashda avval backup, keyin testlar, yangi image va `docker compose up -d`. Volume’ni o‘chiruvchi `down -v` oddiy restart sifatida ishlatilmaydi. Baza fayli va WAL bir xil lokal volume’da qoladi. Bir vaqtda eski va yangi bot nusxasini bitta tokenda ishga tushirmang.

## Zaxira va tiklash

```sh
.venv/bin/python -m eshqozi backup --destination var/backups/eshqozi.sqlite3
```

Backup SQLite online backup API bilan yaratiladi, faol WAL yozuvlarini ham izchil ko‘chiradi. Containerda:

```sh
docker compose exec bot python -m eshqozi backup --destination /app/var/backups/eshqozi.sqlite3
```

Zaxira chat tarixini saqlashi mumkin; kirish huquqlarini cheklang. Compose’dagi `backup` xizmati har 24 soatda SQLite online backup yaratadi, integrity tekshiradi va 7 kundan eski nusxalarni o‘chiradi. `ESHQOZI_BACKUP_DAYS` bilan muddat o‘zgaradi. Nusxa avval `.partial` faylga yoziladi, tekshiruvdan keyin atomik nomlanadi. Hostdan tashqaridagi shifrlangan saqlash uchun operatorning storage akkaunti kerak; bu akkaunt yaratilmagan.

Tiklashda botni to‘xtating, asl baza va `-wal`/`-shm` fayllarini alohida saqlang, izchil backupni asosiy baza joyiga yozing, eski WAL/SHMni qayta ishlatmang. Egasi container UID/GID 10001 uchun yozish huquqiga ega bo‘lsin. `check` bajaring, keyin botni boshlang. Test suite backupdan profil va bilim bazasining tiklanishini tekshiradi.

## Kalitlarni almashtirish

Telegram yoki AI kaliti almashtirilganda xavfsiz sozlamani yangilang va botni restart qiling. `.env`ni source controlga qo‘shmang. Cloud proxy sirlarining placeholder qiymatlarini boshqa faylga nusxalash kerak emas; muhit bergan bindinglardan foydalaniladi. Saved environment draft runtime’ga darhol qo‘llanmaydi; platformada saqlash/publish jarayoni alohida.
