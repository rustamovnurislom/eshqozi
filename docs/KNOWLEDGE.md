# Bilim bazasining kelib chiqishi

`data/knowledge.json` oldingi sheva tadqiqotlaridan yig‘ilgan version 1 snapshot. 13 profil va 1 511 karta: 1 017 lug‘aviy, 187 grammatik, 210 fonetik qayd, 97 nutq namunasi. Karta mustaqil, hududga mutlaqo xos va bugungi nutqda tasdiqlangan so‘z degani emas; ma’nolar va variantlar alohida kartalar bo‘lishi mumkin.

| Profil | Karta |
|---|---:|
| Surxondaryo | 61 |
| Qashqadaryo | 79 |
| Samarqand | 72 |
| Buxoro | 96 |
| Jizzax | 41 |
| Andijon | 129 |
| Farg‘ona | 215 |
| Namangan | 286 |
| Toshkent | 149 |
| Xorazm | 262 |
| Toshkent ko‘cha | 101 |
| Xorazm ko‘cha · sinov | 20 |
| Adabiy | Maxsus dialekt kartasi kerak emas |

Kitob kartalarida manba nomi, mavjud bo‘lsa muallif/yil, PDF va bosma sahifa, xesh saqlanadi. Ba’zi eski qaydlarda manbaning to‘liq bibliografiyasi yoki xeshi yo‘q; importer ularni o‘zi to‘ldirib uydirmaydi. Qaydlardagi hudud va foydalanish chegaralari saqlangan. Ilmiy transkripsiyaning soddalashtirilishi fonetik yozuv bilan aynan teng emas.

Yangi fonetik kartalar ilmiy kuzatuv sifatida beriladi, avtomatik talaffuz yoki global harf almashtirish qoidasi sifatida emas. Nutq namunalaridan faqat standarti/ma’nosi mavjud 97 tasi kiritildi; ma’nosi aniqlanmagan 9 tasi `provenance.skipped_untranslated_examples`da qayd etilgan. Kartaning `meta` qismida mavjud dalil darajasi, yozuv holati, qo‘llanish chegarasi va audio/zamonaviy/native tasdiq bayroqlari saqlanadi. Yo‘q bayroqni bot ijobiy tasdiqqa aylantirmaydi.

Tuzilgan uslub xulosalari va ichki hudud profillari ham runtime profiliga biriktirilgan. Masalan, Xorazmning Urganch–Xiva nomzodi butun viloyat uchun universal emas; foydalanuvchi Xivani tilga olgandagina tegishli ichki hudud qaydi uzatiladi. Toshkent ko‘cha yozishma usullari va murojaat rotatsiyasi saqlangan, ammo mavjud eksport 2026-yilgi dolzarblik yoki butun shahar uchun xoslikni tasdiqlamaydi.

Toshkent ko‘cha kartalari oldingi foydalanuvchi eksportidagi leksik kuzatuvlarga asoslanadi. To‘liq xabarlar, sender IDlari, author kodlari, Telegram message IDlari, ism va telefonlar import qilinmagan. Chatdan olingan qayd 2026-yildagi chastota yoki butun Toshkentga xoslik dalili emas.

Xorazm ko‘cha uchun birinchi eksport bo‘sh, ikkinchisi transfer chegarasidan katta bo‘lgani sabab bu snapshotda haqiqiy yoshlar ko‘cha chati tahlili mavjud emas. 20 karta kitobdagi norasmiy muomala asosidir. Profil foydalanuvchiga **sinov** deb ko‘rsatiladi. Toshkent slengi unga avtomatik ko‘chirilmadi.

`scripts/import_research.py` turli tadqiqot formatlarini umumiy sxemaga yig‘adi. Har import qilinadigan JSONning xeshi `provenance.inputs`da; bundle xeshi va hisoblar `data/import-report.json`da. Lug‘at/grammatika kartasi shakl yoki ma’nosiz bo‘lsa xato beradi; nutq namunasida standart ma’no bo‘lmasa uni avtomatik to‘ldirmaydi, alohida skip ro‘yxatida qayd etadi.

Tadqiqotlar yana mavjud bo‘lsa snapshotni yangilash:

```sh
python scripts/import_research.py --research-root /workspace/research
.venv/bin/python -m unittest discover -s tests -v
```

Sonlarga bog‘langan testlar yangi snapshot bo‘yicha **ongli ravishda** yangilanadi; eski sonni qondirish uchun yangi manbalarni olib tashlamang. Bilim bazasi o‘zgarganda serverni qayta ishga tushiring. Model vaznlari qayta o‘qitilmagan: dalillar promptga tanlab qo‘shiladi.

Sifatni keyingi rivojlantirishda mahalliy so‘zlovchi suhbat tabiiyligi, variantning hududi, shaxs-zamon-inkor saqlanishi va baho/hazil ohangini tekshirishi kerak. Hozirgi avtomatik tekshiruvlar noto‘g‘ri manba-hudud aralashishi va omonim yo‘qolishini ushlaydi, native tabiiylikni o‘lchamaydi.
