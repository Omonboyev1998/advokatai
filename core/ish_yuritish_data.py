"""
core/ish_yuritish_data.py — O'zbek tilida ish yuritish va hujjatshunoslik bo'yicha
me'yoriy qoidalar, rekvizitlar tartibi va namunaviy hujjatlar korpusi.

O'zbekiston Respublikasining "Davlat tili haqida"gi Qonuni, Vazirlar Mahkamasining
davlat tilida ish yuritish bo'yicha qarorlari va O'zDSt standartlari asosida tuzilgan.
"""

ISH_YURITISH_RULES = [
    {
        "category": "umumiy_qoidalar",
        "doc_type": "ish_yuritish_standartlari",
        "title": "Davlat tilida ish yuritishning asosiy talablari va rekvizitlari",
        "procedure": (
            "1. Hujjat tili: O'zbekiston Respublikasida barcha korxona, muassasa va tashkilotlarda "
            "ish yuritish davlat tilida (lotin yozuviga asoslangan o'zbek alifbosida) olib boriladi.\n"
            "2. Standart rekvizitlar tarkibi:\n"
            "   - Tashkilotning to'liq nomi va blankasi (logotipi, manzili, STIR/INN, tel);\n"
            "   - Hujjat turi nomi (BUYRUQ, ARIZA, DALOLATNOMA, BAYONNOMA);\n"
            "   - Hujjat sanasi (masalan: 2026-yil 9-oktabr yoki 09.10.2026);\n"
            "   - Ro'yxatdan o'tkazish raqami (№);\n"
            "   - Hujjat tuzilgan joy (shahar/tuman);\n"
            "   - Manzil egasi (kimga yuborilayotgani);\n"
            "   - Hujjat sarlavhasi (hujjat nima haqidaligi);\n"
            "   - Hujjat matni (kirish, asos va xulosa/farmoyish qismlari);\n"
            "   - Ilovalar mavjudligi haqida belgi;\n"
            "   - Imzo, familiyasi va bosh harflari;\n"
            "   - Kelishuv vizalari (yurist, kadr, hisobchi);\n"
            "   - Ijrochi haqida ma'lumot (familiyasi, telefon raqami).\n"
            "3. Hoshiya o'lchamlari: Chap tomon — kamida 3.0 sm (tikish uchun), o'ng tomon — 1.5 sm, "
            "yuqori va quyi tomonlar — 2.0 sm."
        ),
        "keywords": "davlat tili ish yuritish qoidalari rekvizitlar blanka sana imzo hoshiya o'zdst"
    },
    {
        "category": "buyruqlar",
        "doc_type": "ishga_qabul_qilish_buyrugi",
        "title": "Ishga qabul qilish to'g'risida buyruq rasmiylashtirish tartibi",
        "procedure": (
            "1. Yuridik asosi: O'zbekiston Respublikasi Mehnat kodeksining 127-moddasi. "
            "Ishga qabul qilish ish beruvchining buyrug'i bilan rasmiylashtiriladi. Buyruq mehnat shartnomasiga "
            "qat'iy muvofiq holda chiqariladi va xodimga 3 kunlik muddatda imzo qo'ydirib tanishtiriladi.\n"
            "2. Buyruq tuzilishi:\n"
            "   - Korxona nomi va sarlavhasi;\n"
            "   - Sanasi va raqami;\n"
            "   - 'Ishga qabul qilish to'g'risida' sarlavhasi;\n"
            "   - Farmoyish so'zi: 'BUYURAMAN:';\n"
            "   - 1-band: Xodimning F.I.Sh., qaysi sanadan, qaysi bo'limga va qaysi lavozimga qabul qilingani, "
            "sinov muddati (agar belgilangan bo'lsa), oylik maoshi yoki razryadi ko'rsatiladi;\n"
            "   - 2-band: Bosh hisobchiga oylik maosh tayinlash topshirig'i;\n"
            "   - 3-band: Nazorat va asos: xodim arizasi va mehnat shartnomasi raqami/sanasi;\n"
            "   - Rahbar imzosi va xodimning 'Buyruq bilan tanishdim' imzosi."
        ),
        "keywords": "ishga qabul qilish buyruq mehnat kodeksi 127 modda kadrlar buyrugi namunasi"
    },
    {
        "category": "buyruqlar",
        "doc_type": "mehnat_tatili_buyrugi",
        "title": "Yillik asosiy mehnat ta'tili berish to'g'risida buyruq tartibi",
        "procedure": (
            "1. Yuridik asosi: Mehnat kodeksining 216-228 moddalari. Har bir xodimga kamida 21 kalendar kun "
            "yillik asosiy mehnat ta'tili kafolatlanadi. Ta'tillar jadvali yoki xodimning arizasi asosida chiqariladi.\n"
            "2. Buyruq tuzilishi:\n"
            "   - 'BUYURAMAN:';\n"
            "   - 1-band: Xodimga (lavozimi, F.I.Sh.) qaysi ish yili uchun, necha kalendar kun mehnat ta'tili "
            "qaysi sanadan qaysi sanagacha berilayotgani, ishga chiqish sanasi ko'rsatiladi;\n"
            "   - 2-band: Bosh hisobchiga qonunda belgilangan muddatda (ta'til boshlanishidan kamida 3 kun oldin) "
            "ta'til pullarini (otpusk) hisoblab to'lash topshiriladi;\n"
            "   - Asos: Xodimning arizasi yoki tasdiqlangan ta'tillar grafigi."
        ),
        "keywords": "mehnat tatili buyruq otpusk yillik asosiy tatil 21 kun ta'tillar grafigi"
    },
    {
        "category": "buyruqlar",
        "doc_type": "ishdan_boshatish_buyrugi",
        "title": "Mehnat shartnomasini bekor qilish (ishdan bo'shatish) buyrug'i",
        "procedure": (
            "1. Yuridik asosi: Mehnat kodeksining 168, 169, 170, 171-moddalari. Buyruqda mehnat shartnomasi "
            "MKning qaysi moddasi va qaysi bandiga asosan bekor qilingani aniq ko'rsatilishi shart.\n"
            "2. Buyruq tuzilishi:\n"
            "   - Kirish: Mehnat shartnomasini bekor qilish sababi va qonuniy asosi;\n"
            "   - 'BUYURAMAN:';\n"
            "   - 1-band: Falonchi lavozimidagi F.I.Sh. bilan tuzilgan mehnat shartnomasi falon sanadan "
            "Mehnat kodeksining falon moddasi (masalan, 160-moddasi o'z xohishiga ko'ra) asosida bekor qilinsin;\n"
            "   - 2-band: Bosh hisobchiga foydalanilmagan barcha mehnat ta'tillari uchun pulli kompensatsiya va "
            "ish haqini to'liq to'lab, yakuniy hisob-kitobni amalga oshirish topshirilsin (MK 172-modda);\n"
            "   - Asos: Xodimning yozma arizasi yoki korxona kasaba uyushmasi roziligi/ogohlantirish xati;\n"
            "   - Xodimning tanishganlik imzosi (oxirgi ish kunida mehnat daftarchasi yoki elektron yozuv topshiriladi)."
        ),
        "keywords": "ishdan boshatish buyrugi mehnat shartnomasini bekor qilish mk 160 161 170 kompensatsiya"
    },
    {
        "category": "buyruqlar",
        "doc_type": "intizomiy_jazo_buyrugi",
        "title": "Intizomiy jazo qo'llash (hayfsan, jarima) buyrug'i tartibi",
        "procedure": (
            "1. Yuridik asosi: Mehnat kodeksining 312, 313, 314, 315-moddalari.\n"
            "2. Muhim qoidalar:\n"
            "   - Intizomiy jazo turlari: hayfsan, jarima (o'rtacha oylik ish haqining 30% igacha, ichki qoidalarda ko'rsatilgan bo'lsa 50% igacha), mehnat shartnomasini bekor qilish (MK 312-modda);\n"
            "   - Majburiy talab: Jazodan oldin xodimdan yozma ravishda Tushuntirish xati olinishi SHART. Xodim tushuntirish berishdan bosh tortsa, 3 kishilik dalolatnoma tuziladi (MK 313-modda);\n"
            "   - Muddat: Nojo'ya xatti-harakat aniqlangandan keyin 1 oy ichida va sodir etilgandan keyin 6 oy ichida qo'llanilishi mumkin;\n"
            "3. Buyruq tuzilishi:\n"
            "   - Xodimning qanday mehnat majburiyatini buzgani holati bayoni;\n"
            "   - 'BUYURAMAN:';\n"
            "   - Qo'llanilgan jazo chorasi (Hayfsan e'lon qilinsin yoki jarima ushlab qolinsin);\n"
            "   - Asos: Bildirgi, dalolatnoma va xodimning tushuntirish xati."
        ),
        "keywords": "intizomiy jazo buyruq hayfsan jarima mk 312 313 tushuntirish xati intizomiy chora"
    },
    {
        "category": "arizalar",
        "doc_type": "ishga_kirish_arizasi",
        "title": "Ishga qabul qilish to'g'risida ariza yozish tartibi",
        "procedure": (
            "1. Hujjat rekvizitlari:\n"
            "   - O'ng burchakda: Tashkilot rahbari lavozimi, F.I.Sh. (Kimga: '... direktori falonchiga');\n"
            "   - Fuqaroning F.I.Sh., yashash manzili, telefon raqami, pasport/ID ma'lumotlari (Kimdan);\n"
            "   - O'rtada: 'ARIZA';\n"
            "   - Matn: 'Meni 2026-yil __-______dan boshlab [korxona nomi] ning [bo'lim nomi] ga [lavozim nomi] lavozimiga ishga qabul qilishingizni so'rayman.';\n"
            "   - Ilova qilingan hujjatlar: Pasport nusxasi, diplom nusxasi, rezyume (obyektivka), mehnat daftarchasi;\n"
            "   - Chap tomonda sana, o'ng tomonda shaxsiy imzo va F.I.Sh."
        ),
        "keywords": "ishga kirish arizasi ariza namunasi ishga qabul qilish arizasi rekvizitlari"
    },
    {
        "category": "arizalar",
        "doc_type": "ishdan_boshash_arizasi",
        "title": "O'z xohishiga ko'ra ishdan bo'shash to'g'risida ariza yozish tartibi",
        "procedure": (
            "1. Yuridik asosi: Mehnat kodeksining 160-moddasi. Xodim noaniq muddatli mehnat shartnomasini "
            "ham, muddati tugashidan oldin muddatli mehnat shartnomasini ham 14 kalendar kun oldin ish beruvchini "
            "yozma ravishda ogohlantirib, bekor qilishga haqli.\n"
            "2. Matn namunasi:\n"
            "   'O'zbekiston Respublikasi Mehnat kodeksining 160-moddasiga asosan men bilan tuzilgan mehnat shartnomasini "
            "o'z xohishimga ko'ra 2026-yil __-______dan boshlab bekor qilishingizni va men bilan to'liq hisob-kitob "
            "qilishingizni so'rayman.'\n"
            "3. Muhim jihat: 14 kunlik muddat davomida xodim arizasini istalgan vaqtda qaytarib olishga haqli."
        ),
        "keywords": "ishdan boshash arizasi oz xohishi bilan ariza mk 160 modda 14 kun ogohlantirish"
    },
    {
        "category": "arizalar",
        "doc_type": "mehnat_tatili_arizasi",
        "title": "Mehnat ta'tili (yillik yoki ish haqi saqlanmaydigan) arizasi",
        "procedure": (
            "1. Yillik ta'til arizasi: 'Menga 2026-yil __-______dan boshlab 20__ - 20__ ish yili uchun navbatdagi "
            "yillik asosiy mehnat ta'tili berishingizni so'rayman.'\n"
            "2. Ish haqi saqlanmaydigan ta'til (MK 241-modda): Oila sharoiti yoki boshqa uzrli sabablar ko'rsatiladi: "
            "'Oilaviy sharoitim tufayli menga 2026-yil __-______dan 2026-yil __-______gacha (__ kalendar kunga) "
            "ish haqi saqlanmagan holda ta'til berishingizni so'rayman.'"
        ),
        "keywords": "mehnat tatili arizasi otpusk arizasi ish haqi saqlanmagan tatil oyliksiz tatil mk 241"
    },
    {
        "category": "axborot_hujjatlari",
        "doc_type": "bildirgi_dokladnaya",
        "title": "Bildirgi (Bildirishnoma / Dokladnaya zapiska) yozish tartibi",
        "procedure": (
            "1. Maqsadi: Xodim yoki tarkibiy bo'linma rahbari tomonidan yuqori turuvchi rahbarga biror "
            "voqea, bajarilgan ish, muammo, moddiy-texnik ta'minot zarurati yoki taklif haqida rasmiy xabar berish.\n"
            "2. Rekvizitlari:\n"
            "   - Rahbar lavozimi va F.I.Sh. (Kimga);\n"
            "   - Bildirgi beruvchining lavozimi va F.I.Sh. (Kimdan);\n"
            "   - 'BILDIRGI' sarlavhasi;\n"
            "   - Kirish qismi: Holat yoki fakt bayoni (masalan, bo'limda kompyuter nosozligi, xodimning intizom buzishi, xizmat safari natijasi);\n"
            "   - Asoslantirish: Nima sababdan bu masala muhimligi;\n"
            "   - Xulosa/Taklif: Rahbardan nima qilinishi so'ralayotgani ('Shu munosabat bilan ... choralar ko'rishingizni so'rayman');\n"
            "   - Sana va imzo."
        ),
        "keywords": "bildirgi bildirishnoma dokladnaya xizmat bildirgisı rahbarga xat xodim bildirgisı"
    },
    {
        "category": "axborot_hujjatlari",
        "doc_type": "tushuntirish_xati",
        "title": "Tushuntirish xati (Obyasnitelnaya zapiska) yozish tartibi",
        "procedure": (
            "1. Maqsadi va yuridik asosi: Mehnat intizomi buzilganda (ishga kechikish, kelmaslik, topshiriqni "
            "bajarmaslik), xodimdan sabablarini bayon qilish uchun olinadi (Mehnat kodeksining 313-moddasi).\n"
            "2. Rekvizitlari:\n"
            "   - Rahbar lavozimi va F.I.Sh.;\n"
            "   - Xodimning lavozimi va F.I.Sh.;\n"
            "   - 'TUSHUNTIRISH XATI' sarlavhasi;\n"
            "   - Holat bayoni: qachon, nima sodir bo'lgani;\n"
            "   - Sabablari: uzrli yoki ob'ektiv sabablar ko'rsatilishi (masalan, yo'l-transport hodisasi, sog'lig'i yomonlashgani, shifokor ma'lumotnomasi ilova qilinishi);\n"
            "   - Xulosa: kelgusida bunday holatga yo'l qo'yilmasligi yoki vaziyatni to'g'irlash choralari;\n"
            "   - Sana, xodim imzosi va F.I.Sh."
        ),
        "keywords": "tushuntirish xati obyasnitelniy ishga kechikish intizom buzilishi uzrli sabab mk 313"
    },
    {
        "category": "axborot_hujjatlari",
        "doc_type": "dalolatnoma_akt",
        "title": "Dalolatnoma (Akt) tuzish va rasmiylashtirish tartibi",
        "procedure": (
            "1. Maqsadi: Bir necha shaxslar (kamida 3 kishilik komissiya) tomonidan aniqlangan fakt, "
            "voqea yoki harakatni (moddiy boyliklarni topshirish-qabul qilish, texnik nosozlik, inventarizatsiya, "
            "hujjatlarni yo'q qilish, ishga kelmaganlik) rasman tasdiqlovchi hujjat.\n"
            "2. Rekvizitlari:\n"
            "   - Korxona nomi;\n"
            "   - Tasdiqlash ustxati: O'ng yuqorida: 'TASDIQLAYMAN' Tashkilot rahbari imzosi, muhri va sana;\n"
            "   - Hujjat nomi: 'DALOLATNOMA', sanasi va raqami, tuzilgan joyi;\n"
            "   - Tuzuvchilar tarkibi: 'Asos: Rahbarning falon sonli buyrug'i. Komissiya raisi: [F.I.Sh.], Komissiya a'zolari: [F.I.Sh., F.I.Sh.]';\n"
            "   - Matn: 'Biz, quyida imzo chekuvchilar, ushbu dalolatnomani tuzdik shu haqdakim, ...' (faktlar aniq ko'rsatiladi);\n"
            "   - Xulosa: Komissiyaning xulosasi yoki tavsiyasi;\n"
            "   - Barcha komissiya a'zolarining shaxsiy imzolari (rais va a'zolar)."
        ),
        "keywords": "dalolatnoma akt tuzish komissiya akti moddiy boyliklarni topshirish yaroqsizlik akti"
    },
    {
        "category": "kollegial_hujjatlar",
        "doc_type": "bayonnoma_protokol",
        "title": "Yig'ilish / Majlis bayonnomasi (Protokol) yuritish tartibi",
        "procedure": (
            "1. Maqsadi: Kollegial organlar (umumiy majlis, boshqaruv kengashi, ta'sischilar yig'ilishi, "
            "ilmiy yoki mehnat jamoasi yig'ilishi) muhokamasi va qabul qilgan qarorlarini qayd etish.\n"
            "2. Rekvizitlari:\n"
            "   - Tashkilot nomi, 'BAYONNOMA' so'zi, sanasi va raqami, o'tkazilgan joyi;\n"
            "   - Majlis raisi va kotibi F.I.Sh.;\n"
            "   - Qatnashdilar: ishtirokchilar ro'yxati yoki soni (kvorum mavjudligi);\n"
            "   - 'KUN TARTIBI:': 1. ... 2. ... (ko'riladigan masalalar);\n"
            "   - 'ESHITILDI:': Asosiy ma'ruzachining nutqi bayoni;\n"
            "   - 'SO'ZGA CHIQDILAR:': Muhokamada qatnashganlarning fikr-mulohazalari;\n"
            "   - 'QAROR QILINDI:' (yoki 'QAROR QILADI:'): Qabul qilingan aniq qarorlar, mas'ullar va muddatlar;\n"
            "   - Majlis raisi va kotibining imzolari."
        ),
        "keywords": "bayonnoma protokol majlis bayonnomasi yigilish kun tartibi eshitildi qaror qilindi"
    },
    {
        "category": "rasmiy_xatlar",
        "doc_type": "kafolat_xati",
        "title": "Kafolat xati (Garantiynoye pismo) rasmiylashtirish tartibi",
        "procedure": (
            "1. Maqsadi: Bir tashkilot ikkinchi tashkilotga to'lovni o'z vaqtida amalga oshirish, "
            "ishlarni bajarish, tovarlarni yetkazib berish yoki ish o'rni bilan ta'minlash majburiyatini "
            "yuridik jihatdan kafolatlash uchun beriladi.\n"
            "2. Rekvizitlari:\n"
            "   - Tashkilotning rasmiy blankasida (barcha bank rekvizitlari, hisob-raqam, MFO, INN bilan);\n"
            "   - Xat raqami va sanasi;\n"
            "   - Manzil egasi (Hamkor tashkilot rahbari nomiga);\n"
            "   - Matn: 'Sizdan [shartnoma predmeti/xizmat nomi] ni amalga oshirishingizni so'raymiz. O'z navbatida, ushbu xizmatlar/tovarlar uchun to'lovni 2026-yil __-______gacha to'liq to'lashni kafolatlaymiz. To'lov kechiktirilgan taqdirda, amaldagi qonunchilikka muvofiq javobgarlikni zimmamizga olamiz.';\n"
            "   - Korxona rahbari va Bosh hisobchining imzolari (ikkalasi ham imzo qo'yishi shart);\n"
            "   - Tashkilot muhri."
        ),
        "keywords": "kafolat xati garantiyniy pismo tolov kafolati bosh hisobchi imzosi bank rekvizitlari"
    },
    {
        "category": "rasmiy_xatlar",
        "doc_type": "xizmat_xati_sorov_xati",
        "title": "Rasmiy xizmat xati (So'rov xati / Javob xati) yozish tartibi",
        "procedure": (
            "1. Maqsadi: Tashkilotlar, vazirliklar, idoralar va korxonalar o'rtasida rasmiy muloqot, "
            "axborot yoki hujjat almashish, so'rov yuborish yoki javob qaytarish.\n"
            "2. Qoidalari:\n"
            "   - Rasmiy blankada chiqariladi, sanasi va chiquvchi raqami qo'yiladi;\n"
            "   - Agar javob xati bo'lsa, kiruvchi xat raqami va sanasiga havola qilinadi ('Sizning 2026-yil __-_____dagi __-sonli xatingizga javoban...');\n"
            "   - Matn: Bir masalaga bag'ishlanadi, rasmiy-idoraviy tilda bayon qilinadi;\n"
            "   - Hujjat oxirida ijrochining ismi-sharifi va telefon raqami ko'rsatiladi (masalan: Ijrochi: A.Karimov, Tel: +998 71 123-45-67)."
        ),
        "keywords": "xizmat xati rasmiy xat sorov xati javob xati idoraviy yozishma delovoye pismo ijrochi"
    },
    {
        "category": "shaxsiy_hujjatlar",
        "doc_type": "tilxat_va_ishonchnoma",
        "title": "Tilxat (Raspiska) va Ishonchnoma (Doverennost) tuzish tartibi",
        "procedure": (
            "1. Tilxat tuzish tartibi:\n"
            "   - Maqsadi: Pul, qimmatbaho mulk yoki hujjat olinganligini tasdiqlovchi shaxsiy yozma dalil;\n"
            "   - 'TILXAT' sarlavhasi;\n"
            "   - Pul/mulk oluvchining to'liq pasport ma'lumotlari (F.I.Sh., JSHSHIR, pasport seriyasi, yashash manzili);\n"
            "   - Kimdan olingani (beruvchining pasport ma'lumotlari);\n"
            "   - Olingan summa raqam va so'z bilan aniq yoziladi (masalan: 10 000 000 (o'n million) so'm);\n"
            "   - Qaytarish sanasi va shartlari;\n"
            "   - Guvohlar mavjud bo'lsa, ularning ma'lumotlari va imzolari;\n"
            "   - Oluvchining shaxsiy imzosi va to'liq ismi-sharifi (o'z qo'li bilan yozilishi maqsadga muvofiq).\n"
            "2. Ishonchnoma tuzish tartibi:\n"
            "   - Beruvchi (ishonch bildiruvchi) va ishonchli vakil ma'lumotlari;\n"
            "   - Vakolat doirasi aniq sanab o'tiladi (tashkilot nomidan shartnoma tuzish, tovarlarni qabul qilish, sudlarda vakillik qilish);\n"
            "   - Amal qilish muddati (agar muddat ko'rsatilmasa, Fuqarolik kodeksining 139-moddasiga binoan 1 yil amal qiladi);\n"
            "   - Berilgan sana (sanasi ko'rsatilmagan ishonchnoma haqiqiy emas!)."
        ),
        "keywords": "tilxat raspiska ishonchnoma doverennost pul olish qarz tilxati vakillik fk 139"
    },
    {
        "category": "shaxsiy_hujjatlar",
        "doc_type": "tavsifnoma_va_tavsiyanoma",
        "title": "Tavsifnoma (Xarakteristika) va Tavsiyanoma yozish tartibi",
        "procedure": (
            "1. Tavsifnoma (Xarakteristika):\n"
            "   - Xodimning xizmat va ijtimoiy faoliyati, kasbiy malakasi, jamoada tutgan o'rni rasmiy baholanadi;\n"
            "   - Tuzilishi: Sarlavha: 'TAVSIFNOMA', kimga berilgani (lavozimi, F.I.Sh., tug'ilgan yili, ma'lumoti);\n"
            "   - Mehnat faoliyati: Korxonada qaysi yildan beri ishlaydi, qanday yutuqlarga erishdi;\n"
            "   - Kasbiy va shaxsiy fazilatlari: mas'uliyatliligi, tashabbuskorligi, jamoa bilan munosabati;\n"
            "   - Xulosa: Attestatsiyadan o'tkazish, lavozimini oshirish yoki taqdirlash uchun tavsiya etilishi;\n"
            "   - Tashkilot rahbari imzosi va muhri.\n"
            "2. Tavsiyanoma (Tavsiya xati):\n"
            "   - Xodim yangi ishga, o'qishga yoki xalqaro dasturga topshirganda beriladigan ijobiy tavsiya xati."
        ),
        "keywords": "tavsifnoma xarakteristika tavsiyanoma tavsiya xati xodim fazilatlari attestatsiya"
    }
]
