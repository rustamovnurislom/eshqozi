# Bilim bazasining kelib chiqishi

`data/knowledge.json` oldingi sheva tadqiqotlaridan yig‘ilgan version 1 snapshot. 13 profil va 1 204 karta: 1 017 lug‘aviy, 187 grammatik. Karta mustaqil, hududga mutlaqo xos va bugungi nutqda tasdiqlangan so‘z degani emas; ma’nolar va variantlar alohida kartalar bo‘lishi mumkin.

| Profil | Karta |
|---|---:|
| Surxondaryo | 61 |
| Qashqadaryo | 79 |
| Samarqand | 72 |
| Buxoro | 88 |
| Jizzax | 35 |
| Andijon | 122 |
| Farg‘ona | 85 |
| Namangan | 214 |
| Toshkent | 94 |
| Xorazm | 233 |
| Toshkent ko‘cha | 101 |
| Xorazm ko‘cha · sinov | 20 |
| Adabiy | Maxsus dialekt kartasi kerak emas |

Kitob kartalarida manba nomi, mavjud bo‘lsa muallif/yil, PDF va bosma sahifa, xesh saqlanadi. Ba’zi eski qaydlarda manbaning to‘liq bibliografiyasi yoki xeshi yo‘q; importer ularni o‘zi to‘ldirib uydirmaydi. Qaydlardagi hudud va foydalanish chegaralari saqlangan. Ilmiy transkripsiyaning soddalashtirilishi fonetik yozuv bilan aynan teng emas.

Toshkent ko‘cha kartalari oldingi foydalanuvchi eksportidagi leksik kuzatuvlarga asoslanadi. To‘liq xabarlar, sender IDlari, author kodlari, Telegram message IDlari, ism va telefonlar import qilinmagan. Chatdan olingan qayd 2026-yildagi chastota yoki butun Toshkentga xoslik dalili emas.

Xorazm ko‘cha uchun birinchi eksport bo‘sh, ikkinchisi transfer chegarasidan katta bo‘lgani sabab bu snapshotda haqiqiy yoshlar ko‘cha chati tahlili mavjud emas. 20 karta kitobdagi norasmiy muomala asosidir. Profil foydalanuvchiga **sinov** deb ko‘rsatiladi. Toshkent slengi unga avtomatik ko‘chirilmadi.

`scripts/import_research.py` turli tadqiqot formatlarini umumiy sxemaga yig‘adi. Har kiruvchi JSONning xeshi `provenance.inputs`da; bundle xeshi va hisoblar `data/import-report.json`da. Script maydonlari yetishmagan kartani jim tashlamasdan xato beradi.

Tadqiqotlar yana mavjud bo‘lsa snapshotni yangilash:

```sh
python scripts/import_research.py --research-root /workspace/research
.venv/bin/python -m unittest discover -s tests -v
```

Sonlarga bog‘langan testlar yangi snapshot bo‘yicha **ongli ravishda** yangilanadi; eski sonni qondirish uchun yangi manbalarni olib tashlamang. Bilim bazasi o‘zgarganda serverni qayta ishga tushiring. Model vaznlari qayta o‘qitilmagan: dalillar promptga tanlab qo‘shiladi.

Sifatni keyingi rivojlantirishda mahalliy so‘zlovchi suhbat tabiiyligi, variantning hududi, shaxs-zamon-inkor saqlanishi va baho/hazil ohangini tekshirishi kerak. Hozirgi avtomatik tekshiruvlar noto‘g‘ri manba-hudud aralashishi va omonim yo‘qolishini ushlaydi, native tabiiylikni o‘lchamaydi.
