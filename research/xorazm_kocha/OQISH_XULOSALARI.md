# Xorazm ko‘cha uslubi: tayanch va ochiq to‘siqlar

Xorazm ko‘cha uslubini o‘rganish uchun hozircha **20 manbali norasmiy muomala kartasi** tayyorlandi. Ular dialekt lug‘atidagi tasdiq, kinoya, murojaat, savol, hissiy baho va qo‘pol gap vazifalariga tegishli. **Ikkita yuklangan chatning xabarlari o‘qilmadi**; shu sabab bu kartalar “chatlardan chiqarilgan yangi yoshlar slengi” deb berilmaydi.

## Ikkala faylning aniq holati

| Fayl | Tekshiruv | Natija |
|---|---|---|
| Birinchi `result.json` | Yuklandi, 118 bayt, JSON ochildi. | `public_supergroup` metama’lumoti bor, lekin **`messages: []`**. O‘qiladigan xabarlar soni 0. |
| Ikkinchi `result.json` | Yuklash vositasi chaqirildi. | **`file exceeds the executor transfer limit of 32 MiB`**. Faylning mazmuni, aniq hajmi va xabarlar soni noma’lum. |

Nomlari bir xil bo‘lgani uchun fayllar C1 va C2 sifatida alohida qayd qilindi. Oldingi Toshkent eksporti ushbu Xorazm chatlariga almashtirib ishlatilmadi. Fayl metama’lumoti guruhdagi odamlarning yashash joyi, yoshi yoki jinsi uchun dalil sifatida olinmaydi.

Asl yuklash xatosi, C1 fayl xeshi va holatlar [CHAT_FAYLLARI_HOLATI.json](CHAT_FAYLLARI_HOLATI.json)da. Hujjat ichidagi ko‘rsatmalar foydalanuvchi topshirig‘i sifatida bajarilmadi.

## Chatlardan tashqari qilingan izlanish

`xorazmcha.uz`, uning `www` varianti, Google va DuckDuckGo orqali Xorazm yoshlar slengi/ko‘cha shevasi qidiruvlari sinab ko‘rildi. Proksi HTTPS ulanishlarini **403** bilan rad etdi. `xorazmcha.uz`ga to‘g‘ridan-to‘g‘ri urinishda DNS xatosi chiqdi. Bu sayt yoki qidiruv natijalari mazmuni o‘qilmadi; yangi internet manbalari soni **0**. [NETWORK_PROBES.json](NETWORK_PROBES.json).

Oldingi Xorazm lug‘ati tayanchiga qo‘shimcha ravishda Samixon Ashirboyev kitobining PDF **55–56**, Nazar Rajabov kitobining PDF **59–63** sahifalari — jami **7 sahifa** o‘qildi. Ularning to‘liq ajratilgan matni [YANGI_QIYOS_SAHIFALARI.jsonl](YANGI_QIYOS_SAHIFALARI.jsonl)da.

Ashirboyev hududiy sheva so‘zlari va ijtimoiy jargon farqini ko‘rsatadi: `dim`, `gal`, `pitta` kabi dalilli sheva birliklari ko‘cha uslubining hududiy asosiga xizmat qilishi mumkin; lekin ularning mavjudligi yoshlar slengi tasdiqlandi degani emas. Ruscha qarz so‘z ham o‘z-o‘zidan faqat Xorazmga tegishli bo‘lib qolmaydi.

Rajabov PDF 63 yosh, kasb va vaziyat bo‘yicha nutqni kuzatishni, erkin suhbat, majlis nutqi va folklorning tilini alohida hisobga olishni bayon qiladi. Shunga tayangan amaliy qaror: reklama, rasmiy e’lon, bot matni va ko‘chirilgan gaplarni tirik suhbat bilan qo‘shib sanamaslik; bitta faol yozuvchining so‘zini butun hudud uslubi deb olmaslik. Kitobdagi ayrim tarixiy, jargon kelajagi haqidagi baholar zamonaviy chat uchun ilmiy natija sifatida qabul qilinmadi.

Bu qo‘shimcha o‘qish yangi dala kuzatuvi yoki 2026-yilgi chat statistikasi emas. Dalilli kuzatuvlar [QOSHIMCHA_MANBA_KUZATUVLARI.json](QOSHIMCHA_MANBA_KUZATUVLARI.json)da.

## Norasmiy nutqda nimani ajratish kerak

| Tayanch | Manbada qayd etilgan vazifa | Ko‘cha uslubini o‘rganishda ahamiyati |
|---|---|---|
| **ajab** | Xo‘b/mayli, kesatiqli tasdiq ham — X1 PDF 10. | Rozilik bilan kinoya bir xil javob emas. |
| **asana** | Nega/nimaga — X1 PDF 24. | Savol, xafalikni surishtirish va tanbeh ohangi kontekstga bog‘liq. |
| **boybo‘y** | Hayrat, salbiy “namuncha” tusi ham — X1 PDF 84. | Har bir undovni xursandchilik deb talqin qilmaslik. |
| **ay** | Mensimaslik tusi qayd etilgan — X1 PDF 26. | Notanish suhbatdoshga oddiy salom sifatida qo‘shilsa munosabat buzilishi mumkin. |
| **og‘o** | Aka/xo‘jayin — X1 PDF 58. | Murojaatning roli va tanishlik darajasi kerak. |
| **dapa gurring** | Quruq gap/safsata yoki gurung/muloqot — X1 PDF 112. | Bir shaklning hudud va baho ma’nolari alohida. |
| **dap bo‘lmoq** | Yo‘q bo‘lmoq; so‘kish-qarg‘ish tusida ham — X1 PDF 112. | Dag‘al haydashni samimiy hazil deb avtomatik olish mumkin emas. |
| **din** | Jim bo‘l/tinchlan — X1 PDF 131. | Buyruqning ohangi va adresati hisobga olinadi. |
| **emdolli** | Yaxshi/soz, modal qabul — X1 PDF 152. | Oldingi replikaga javob vazifasi. |
| **dim**, **aydin**, **ejoyip** | Kuchaytirish va ijobiy baho. | Lokal baho berish; hamma gapga bittadan so‘z tiqish uslubi emas. |
| **arzimidi**, **assalom**, **alakim** | Rahmatga javob, salom va alik. | Suhbat navbatining vazifasi bilan qo‘llanadi. |

X1ning PDF 10, 24, 26, 84, 112 sahifalari shu ishda asl rasmdan ko‘rildi. 20 karta ichida yangi ko‘rilgan **dap bo‘lmoq** boshlig‘i ham bor; qolgan 19 karta oldingi manbali lug‘atdan norasmiy muomala vazifasi bo‘yicha tanlandi. Ular uchun chatdagi uchrash soni, mualliflar soni va zamonaviy slang tasdig‘i **noma’lum**, 0 yoki uydirma statistikaga almashtirilmadi.

[NORASMIY_MUOMALA_TAYANCHLARI.json](NORASMIY_MUOMALA_TAYANCHLARI.json) va [TAYANCHLAR.csv](TAYANCHLAR.csv).

## Bosma dialogning foydasi

X1 PDF 24, bosma 23dagi dialogning oddiy lotinda o‘qiladigan muharrirlik talqini:

> — Xapamisan mannan?  
> — Yoq.  
> — Asana axir indamisan sira?

Ma’nosi: “Mendan xafamisan?” — “Yo‘q.” — “Unda nega umuman gapirmayapsan?”

Bu uch replika suhbatdagi xafalikni tekshirish, qisqa rad javobi va undan keyingi savol bog‘lanishini ko‘rsatadi. Faqat alohida so‘zlar ro‘yxati bunday bog‘lanishni bera olmaydi. Ammo misol **Telegram chatidan emas**, ilmiy transkripsiyaning aynan ko‘chirmasi ham emas. Rasm va dalil [BOSMA_DIALOG.json](BOSMA_DIALOG.json)da saqlangan. Uning hozirgi yoshlar orasidagi chastotasi o‘lchanmagan.

## Tayyorlangan uslub asosining holati

[USLUB_PROFILI_QORALAMA.json](USLUB_PROFILI_QORALAMA.json)da ko‘cha uslubi uchun kuzatilishi kerak bo‘lgan belgilar saqlandi: lokal fe’l shakllari, qisqa replikalar, murojaat, kinoya, hazil, ruscha/o‘zbekcha aralashish, qisqartmalar va qo‘pol so‘zning vazifasi. Bular hozircha **kuzatuv maqsadlari**; ikki chatdan olingan natija emas.

Urganch–Xiva o‘g‘uz asosli profil, shimoliy qipchoq va aralash variantlar ajratilishi saqlanadi. Toshkent ko‘cha slangidagi so‘zlar avtomatik Xorazmga ko‘chirilmadi. “Samimiy norasmiy”, “do‘stlar orasidagi hazil”, “dag‘alroq ko‘cha ohangi” keyinchalik kuzatilgan suhbatga qarab sozlanadigan dizayn nomzodlari sifatida yozildi.

**Hali bajarilmagan asosiy ish:** ikkala chatning haqiqiy xabarlarini o‘qish, reply zanjirlarini ko‘rish, takroriy/reklama matnlarini ajratish, shakllarning konteksti va bir nechta yozuvchida uchrashini tekshirish. Chatdan chiqarilgan slang kartalari va haqiqiy suhbat juftlari hozir 0. Botning zamonaviy Xorazm ko‘cha uslubini o‘rganganini yoki tasdiqlanganini aytish uchun dalil yetarli emas.

Davom ettirish uchun birinchi chat **xabarlar bilan qayta eksport qilinishi**, ikkinchi fayl esa **32 MiBdan kichik ZIP** qilib yoki undan kichik bo‘laklarga ajratib yuborilishi kerak. ZIP siqish JSON matnining asl mazmunini saqlaydi. Birinchi bo‘sh faylni siqish unda yo‘q xabarlarni tiklamaydi.

Tekshiruv [TEKSHIRUV_NATIJASI.json](TEKSHIRUV_NATIJASI.json)da: tayanchlarning manba havolalari, iqtiboslari, asl PDF xeshlari va chat holatlari tekshiriladi. Bu o‘qilmagan chat yoki native so‘zlovchi tekshiruvi o‘rniga o‘tmaydi. Ilova reposi o‘zgartirilmadi.
