# Oldingi researchdan bot javobigacha

Ushbu o‘zgarish yangi manba qidirishi yoki modelni qayta o‘qitish emas. Oldingi `/workspace/research` xulosalarini `data/knowledge.json`ga qayta yig‘adi. Runtime uchun shu bitta JSON yetarli. Bot `Knowledge.retrieve` bilan kerakli kartalarni, `Knowledge.context_profile` bilan tanlangan hududga tegishli uslub va joy cheklovlarini tanlaydi; AI adapteri ularni buyruq bo‘lmagan dalil ma’lumoti sifatida oladi.

| Oldingi research fayli | Runtime’da ishlatilishi | Asosiy chegara |
|---|---|---|
| `LUGAT.json`, `GRAMMATIKA.json` | Ma’no va grammatik kartalar, manba/sahifa bilan | Hudud va kontekstdan tashqariga yoyilmaydi. Omonim ma’nolar alohida saqlanadi. |
| `FONETIKA.json` | 210 qayd, talaffuzga oid savolda ustuvor qidiriladi | Audio tasdig‘isiz so‘zlarni avtomatik harfma-harf almashtirmaydi. |
| `NUTQ_NAMUNALARI.json` | Ma’nosi mavjud 97 namuna, uslub/ma’no uchun | 9 noaniq ma’noli namuna tashlab ketilib, sababi bundle’da qayd etiladi. Tarixiy iqtibos bugungi tabiiy nutq tasdig‘i emas. |
| `HUDUDIY_PROFILLAR.json` | Savolda aniq joy bo‘lsa o‘sha ichki variant konteksti | Butun viloyatni bitta qishloq yoki shahar shevasiga tenglashtirmaydi. |
| `USLUB_PROFILI.json`, Toshkent ko‘cha `YOZISHMA_USULLARI.json` | Murojaat, suhbat harakati, Xorazm ma’no/morfologiya siyosati | Chat kuzatuvi 2026-yil chastotasi, yoshi, jinsi yoki shaharlikligi dalili emas. |
| `USLUB_PROFILI_QORALAMA.json` | Xorazm ko‘cha profilining nol zamonaviy slang/dialog dalilini saqlaydi | Kitobdagi norasmiy birlik zamonaviy ko‘cha slengi deb ko‘rsatilmaydi; Toshkent slengi avtomatik ko‘chmaydi. |

Importer original PDFdan uzun sitata, xom Telegram xabari, muallif kodi, xabar IDsi va mahalliy fayl yo‘lini javob kontekstiga qo‘shmaydi. Bibliografiya va mavjud sahifa qoldiriladi. Karta metama’lumotida `audio_verified`, `modern_usage_verified`, `native_validated`, `chat_observed` faqat manbada aniq tasdiqlangan bo‘lsa `true`. Manba isbotlamagan joyi savolda paydo bo‘lsa, bot ma’noni saqlagan holda oddiy o‘zbekchada javob bera oladi.

Lug‘aviy aniq shaklni qidiruvda hudud nomi takrorlanadigan umumiy natijadan oldinga qo‘yish kerak: “Xiva hududida aka nima?” savolida `aka → ota` kartasi birinchi turadi. “Barak nima?”da chuchvara va kelin ko‘rdi ma’nolari bir-birini bosmaydi. Fonetika va namuna savoli o‘z karta turini afzal oladi; ular oddiy salomga tasodifiy qo‘shilmaydi. Aniq researchda qayd etilgan bir necha xavfli xato uchun javobda tor cheklov bor: Xorazmga foydalanuvchi so‘ramagan Toshkentcha murojaat kirsa olib tashlanadi, `barakmi` salom qolipiga aylanmaydi, Toshkent ko‘cha nutqidagi aniq `sen qvotti` shaxs xatosi tuzatiladi. Bu uch chegara barcha noma’lum fe’l paradigmasini avtomatik yasashga aylanmaydi. Mavjud maxfiylik, navbat, quota va buyruqlar o‘zgarmaydi.
