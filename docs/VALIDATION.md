# Tekshiruv natijasi

2026-10-06 kuni `/workspace/eshqozi` checkoutida tekshirildi. Quyidagi natijalar shu cloud mashinasiga tegishli; kelajakdagi yangi muhit va jonli Telegram xizmatining natijasi deb talqin qilinmaydi.

| Tekshiruv | Natija |
|---|---|
| `uv sync --frozen --cache-dir /tmp/eshqozi-uv-cache --link-mode copy` | Python 3.12 muhitida mahkamlangan paketlar o‘rnatildi. |
| `python -m eshqozi init` va qayta import | 13 profil, 1 204 karta; takroriy import nusxalarni ko‘paytirmadi. |
| `python -m unittest discover -s tests -v` | 45 test bajarildi, hammasi o‘tdi; tashlab ketilgan test yo‘q. |
| Native HTTP servis | `/healthz`, `/readyz`, `/api/dialects` va haqiqiy demo so‘rovi ishladi. |
| Demo mazmuni | Xorazm profili `pitta nima?` uchun `ozgina` ma’nosini qaytardi; `/manba` tayanch manbalarni ko‘rsatdi. |
| Docker image | `sh scripts/build_offline.sh` muvaffaqiyatli bajarildi; TLS va paket xeshlari tekshiruvi saqlandi. |
| Docker Compose | Bot va backup xizmatlari ishga tushdi; bot konteyneri `healthy`. |
| Konteyner ichidagi HTTP | Readiness, 13 profil va `pitta` so‘rovining kutilgan javobi tekshirildi. |
| Konteyner ruxsatlari | UID/GID 10001, root fayl tizimi read-only, barcha Linux capabilitylar olib tashlangan. |
| Docker restart | Xorazm va do‘stona ohang tanlovi persistent volume’dan saqlanib qoldi; readiness qayta ishladi. |
| Backup | Avtomatik xizmat birinchi SQLite nusxasini yaratdi; `integrity_check=ok`, 1 204 karta. Testlar retention va tiklashni ham tekshirdi. |
| Git diff | `git diff --check` o‘tdi. |

Docker build dastlab konteyner DNS chekloviga duch keldi; hostda TLS va xesh orqali tekshirilgan wheel paketlari bilan tarmoqsiz yig‘ish yo‘li qo‘llandi. Keyin kod fayllari konteyner foydalanuvchisiga tegishli qilib ko‘chirilishi tuzatildi. Yakuniy Compose va funksional tekshiruvlar ushbu tuzatishdan keyin o‘tdi.

## Testlar nimani tekshiradi

- Migratsiya, import, FTS5, lotin/kirill qidiruvi, hududlarni ajratish va Xorazm omonimlarining ma’nolarini saqlash.
- Xabar va polling offsetini atomik saqlash, update dublikatlari, chat ichidagi tartib, boshqa chatlarning parallel ishlashi, lease va restartdan tiklash.
- Profil/ohang, alohida foydalanuvchi tarixi, `/clear`, `/forget`, o‘z javobiga feedback va maxfiy ma’lumotlarni tozalash.
- Doimiy quota, retry xarajatlarini hisoblash, AI javobini delivery retryda qayta yaratmaslik va qisman yuborilgan uzun javobni davom ettirish.
- OpenAI va Telegram HTTP adapterlari, 429 va noto‘g‘ri response, UTF-16 bo‘yicha xabar bo‘lish, oldingi webhookni saqlash, tokenni xatoda oshkor qilmaslik.
- Production rejimida to‘liq startup → Telegram polling → sheva tanlovi → AI so‘rovi → Telegram javobi. Ushbu testda tashqi HTTPS endpointlar **mock transport** bilan almashtirilgan; haqiqiy AI yoki Telegram akkauntiga ulanilmagan.
- Demo HTTP seansi, input tekshiruvi, productionda demo/docsni yopish, backup yaxlitligi va saqlash muddatini boshqarish.

## Saqlangan cloud sozlamalari

`cloud-environment-onboarding:setup` orqali takrorlanadigan `install_script` va servisni boshlash bo‘yicha `start_skill` qoralamaga saqlandi. Mavjud package-manager tarmoq presetiga qo‘shimcha `api.telegram.org` va `api.openai.com` domenlari, `TELEGRAM_BOT_TOKEN` va `ESHQOZI_AI_KEY` sir talablari qo‘shildi. Sir qiymatlari qo‘shilmadi.

Saqlangan qoralama joriy runtime sozlamasini avtomatik o‘zgartirmaydi. Jonli rejim uchun ikki kalitni environment settings’da xavfsiz kiritish, qoralamani saqlash va publish qilish kerak. Keyingi muhitda install/startup hamda jonli `/start` → profil → savol tekshiruvini qayta bajarish talab qilinadi. Jarayonlar snapshot bilan saqlanmaydi va yangi muhitda qayta boshlanadi.

## Hali tekshirilmagan ishlar

- Haqiqiy shaxsiy Telegram chatdagi `/start` → profil → suhbat oqimi: dastlab kalitlar mavjud emas edi. Keyingi jonli API tekshiruvi quyida; foydalanuvchi chatiga sun’iy sinov xabari yuborilmadi.
- GitHub Actions: CI fayli tayyorlangan, GitHubda workflow ishga tushirilmagan.
- Standart online Docker build: ushbu muhitda DNS ishlamadi; tasdiqlangan yo‘l offline builddir.
- Mahalliy so‘zlovchilarning tabiiylik bahosi: avtomatik testlar buni kafolatlamaydi. Xorazm ko‘cha profili sinov sifatida belgilangan; o‘qilgan zamonaviy chat dalili yo‘q.
- Tashqi serverga deploy va serverdan tashqaridagi backup saqlash: hosting/storage akkaunti yoki credential berilmagan.

Tekshiruv uchun ochilgan Compose xizmatlari ish yakunida to‘xtatildi; volume o‘chirilmadi. Native demo servis joriy muhitda ishlatib ko‘rildi. Loyiha kodlari, lockfilelar va bilim bazasi kelajakdagi ishga tushirish uchun yetarli; oldingi research katalogi runtime uchun zarur emas.

## Jonli ulanish va botni tiklash — 2026-10-06

Foydalanuvchi bot ishlamayotganini bildirganidan keyin yangi cloud muhitida tekshirildi. Ikki sir bindingi mavjud va API domenlari ruxsat etilgan edi, ammo bot jarayoni ishlamayotgan edi. Oldingi muhitning jarayoni snapshot orqali yangi muhitga ko‘chmaydi.

`ESHQOZI_MODE=production .venv/bin/python -m eshqozi serve` bilan bot boshlandi. Telegram `getMe` haqiqiy API orqali `@eshqozibot`ni tasdiqladi. OpenAI `gpt-4.1-mini` modeliga qisqa so‘rov HTTP 200 va haqiqiy javob qaytardi. `/healthz` va `/readyz` HTTP 200, `mode=production`, `ready=true`, `cards=1204`; readiness muvaffaqiyatli pollingni ham talab qiladi. Navbatda yoki navbat yozuvlarida xato yo‘q edi. Kalit qiymatlari hujjat va loglarga yozilmadi.

Bot ushbu faol cloud muhitida ishlayapti. Cloud muhitining to‘xtashi doimiy hosting o‘rnini bosmaydi; keyingi muhitda saved startup yo‘riqnomasi bo‘yicha jarayon qayta boshlanishi kerak. Uzluksiz xizmat uchun Compose doimiy serverda ishga tushiriladi.

## Oldingi researchni runtime’ga ulash — 2026-10-07

`scripts/import_research.py` mavjud research JSONlaridan yangi manba qidirmasdan 1 511 kartali bundle yaratdi: 1 017 lug‘aviy, 187 grammatik, 210 fonetik qayd va 97 nutq namunasi. Standart ma’nosi tasdiqlanmagan 9 namuna alohida skip ro‘yxatiga tushdi. Ichki hudud profillari, Xorazmning ma’no/morfologiya chegaralari hamda Toshkent ko‘cha yozishma usullari prompt kontekstiga tanlab uzatiladi. Xorazm ko‘cha zamonaviy slang dalili `0` bo‘lib qoladi.

48 avtomatik test o‘tdi. Yangi regression tekshiruvida Xiva savoli tegishli ichki hududni tanlashi, oddiy savol uni avtomatik tanlamasligi, fonetik/namuna kartalari tegishli so‘rovda kelishi, manba statusi, chat maxfiyligi va tor hudud/shaxs cheklovi saqlanishi tekshirildi. Production bazasining eski holati backup qilindi; bot yangi bundle bilan restart qilindi. `/readyz` HTTP 200 va `cards=1511` qaytardi.

Jonli AI adapteri bilan sintetik uch savol tekshirildi: Xivada `aka` ma’nosi `ota, dada` bo‘lib qoldi; Toshkent ko‘cha javobi o‘z uslubida chiqdi; Xorazm ko‘cha salomida uydirma `barakmi` va Toshkentcha `brat` ishlatilmadi. Oldingi sinovda model aynan shu xatolarni qilgani uchun qidiruv va aniq cheklovlar tuzatildi. Bu mahalliy so‘zlovchining tabiiylik bahosini yoki Telegramdagi haqiqiy chat bilan end-to-end tekshiruvni almashtirmaydi.
