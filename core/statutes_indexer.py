"""
core/statutes_indexer.py — O'zbekiston Respublikasi Kodekslari va Oliy Sud Plenumi Qarorlari Korpusi.

Mehnat kodeksi (yangi tahrir), Fuqarolik kodeksi, Oila kodeksi, Jinoyat kodeksi,
Ma'muriy javobgarlik to'g'risidagi kodeks, Fuqarolik protsessual kodeksi moddalarining
rasmiy matni hamda Oliy Sud Plenumi qarorlarini 'legal_statutes' jadvaliga yuklaydi.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "memory" / "advokat_knowledge.db"

STATUTES_DATA = [
    # ── 1. MEHNAT KODEKSI (YANGI TAHRIR, 2023) ──────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "161-modda",
        "title": "Mehnat shartnomasini ish beruvchining tashabbusi bilan bekor qilish asoslari",
        "content": (
            "Mehnat shartnomasi ish beruvchining tashabbusi bilan quyidagi asoslar bo'yicha bekor qilinishi mumkin:\n"
            "1) tashkilot (uning alohida bo'linmasi) o'z muassislari (ishtirokchilari) yoki ta'sis hujjatlari bilan vakolat berilgan "
            "organ qaroriga ko'ra tugatilganligi yoki yakka tartibdagi tadbirkor tomonidan faoliyat to'xtatilganligi;\n"
            "2) xodimlar soni (shtati) o'zgarganligi;\n"
            "3) xodimning malakasi yetarli emasligi sababli egallab turgan lavozimiga yoki bajarayotgan ishiga nomuvofiqligi;\n"
            "4) xodim tomonidan o'z mehnat majburiyatlari muntazam ravishda buzilganligi (avval intizomiy jazo qo'llanilgan bo'lsa);\n"
            "5) xodim tomonidan o'z mehnat majburiyatlari bir marta qo'pol ravishda buzilganligi (ichki mehnat tartibi qoidalarida ko'rsatilgan ro'yxat bo'yicha);\n"
            "6) o'rindoshlik asosida ishlamaydigan boshqa xodimning ishga qabul qilinishi munosabati bilan;\n"
            "7) xodim bilan tuzilgan mehnat shartnomasida nazarda tutilgan alohida asoslar bo'yicha.\n"
            "Xodim vaqtincha mehnatga qobiliyatsiz bo'lgan davrda hamda ta'tilda bo'lgan vaqtda mehnat shartnomasini ish beruvchining tashabbusi bilan bekor qilishga yo'l qo'yilmaydi."
        ),
        "keywords": "mehnat shartnomasi ishdan bo'shatish shtat qisqarishi malaka intizom qo'pol buzish ta'til kasallik"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "163-modda",
        "title": "Xodimning aybli harakatlari uchun mehnat shartnomasini bekor qilish tartibi",
        "content": (
            "Xodimning mehnat majburiyatlarini buzganligi munosabati bilan mehnat shartnomasini bekor qilishda intizomiy jazoni "
            "qo'llash qoidalariga rioya etilishi shart. Intizomiy jazo qo'llanilishidan oldin xodimdan yozma ravishda tushuntirish xati "
            "talab qilinishi lozim. Xodimning tushuntirish xati berishdan bosh tortishi intizomiy jazo qo'llash uchun to'siq bo'lmaydi "
            "va bu haqda tegishli dalolatnoma tuziladi. Intizomiy jazo nojo'ya xatti-harakat aniqlangan kundan boshlab bir oydan kechiktirmay "
            "qo'llaniladi."
        ),
        "keywords": "tushuntirish xati intizomiy jazo dalolatnoma muddat bir oy ayb ishdan bo'shatish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "164-modda",
        "title": "Mehnat shartnomasini kasaba uyushmasi qo'mitasi roziligi bilan bekor qilish",
        "content": (
            "Jamoa shartnomasida yoki jamoa kelishuvida mehnat shartnomasini ish beruvchining tashabbusi bilan bekor qilish uchun "
            "kasaba uyushmasi qo'mitasining oldindan roziligini olish nazarda tutilgan bo'lsa, shartnomani bunday roziliksiz bekor qilishga "
            "yo'l qo'yilmaydi. Kasaba uyushmasi qo'mitasi yozma taqdimnoma olingan kundan e'tiboran o'n kun ichida qaror qabul qiladi."
        ),
        "keywords": "kasaba uyushmasi profsoyuz rozilik taqdimnoma noqonuniy bekor qilish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "173-modda",
        "title": "Ishdan bo'shatish nafaqasi (Vixodnoye posobiye)",
        "content": (
            "Ishdan bo'shatish nafaqasining miqdori ushbu ish beruvchidagi ish stajiga bog'liq bo'ladi va quyidagilardan kam bo'lishi mumkin emas:\n"
            "- 3 yilgacha stajga ega bo'lgan xodimlarga — o'rtacha oylik ish haqining 50 foizi;\n"
            "- 3 yildan 5 yilgacha stajga ega bo'lganlarga — 75 foizi;\n"
            "- 5 yildan 10 yilgacha stajga ega bo'lganlarga — 100 foizi;\n"
            "- 10 yildan 15 yilgacha stajga ega bo'lganlarga — 150 foizi;\n"
            "- 15 yildan ortiq stajga ega bo'lganlarga — o'rtacha oylik ish haqining 200 foizi."
        ),
        "keywords": "ishdan bo'shatish nafaqasi vihodnoye posobiye kompensatsiya staj oylik ish haqi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "171-modda",
        "title": "Mehnat shartnomasi bekor qilinganda xodim bilan yakuniy hisob-kitob qilish",
        "content": (
            "Xodim bilan hisob-kitob mehnat shartnomasi bekor qilingan kuni amalga oshirilishi shart. Ish beruvchi xodimga tegishli barcha "
            "summalarni (oylik ish haqi, foydalanilmagan mehnat ta'tili uchun kompensatsiya va qonunda belgilangan nafaqalarni) to'lashi lozim. "
            "Agar xodim ishdan bo'shatilgan kuni ishlamagan bo'lsa, tegishli summalar hisob-kitob qilish to'g'risida talab qo'yilgandan keyin "
            "kechi bilan keyingi kundan kechiktirmasdan to'lanishi shart."
        ),
        "keywords": "hisob-kitob oxirgi oylik raschyot kompensatsiya foydalanilmagan ta'til kechiktirish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "268-modda",
        "title": "Xodimni avvalgi ishiga tiklash va majburiy progul uchun haq to'lash",
        "content": (
            "Mehnat shartnomasi g'ayriqonuniy ravishda bekor qilingan yoki xodim boshqa ishga g'ayriqonuniy o'tkazilgan taqdirda, u sud "
            "yoki boshqa vakolatli organ tomonidan avvalgi ishiga tiklanishi shart. Ishga tiklanganda ish beruvchiga xodimga majburiy progul "
            "vaqti uchun o'rtacha ish haqini to'lash majburiyati yuklatiladi (bir yildan ortiq bo'lmagan davr uchun). Shuningdek, xodimga "
            "yetkazilgan ma'naviy zarar uchun kompensatsiya undirilishi mumkin."
        ),
        "keywords": "ishga tiklash majburiy progul o'rtacha ish haqi ma'naviy zarar noqonuniy buyruq"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Mehnat kodeksi",
        "article_no": "560-modda",
        "title": "Yakka mehnat nizolarini ko'rish uchun sudga murojaat qilish muddatlari",
        "content": (
            "Sudga yakka mehnat nizosini ko'rib chiqish to'g'risidagi ariza bilan murojaat qilish quyidagi muddatlarda amalga oshiriladi:\n"
            "1) ishga tiklash to'g'risidagi nizolar bo'yicha — xodimga ish beruvchining mehnat shartnomasini bekor qilish haqidagi buyrug'i "
            "nusxasi topshirilgan kundan e'tiboran 3 oy ichida;\n"
            "2) xodim tomonidan ish beruvchiga yetkazilgan moddiy zararni qoplash to'g'risidagi nizolar bo'yicha — zarar yetkazilgani aniqlangan kundan 1 yil ichida;\n"
            "3) boshqa barcha mehnat nizolari (oylik undirish, intizomiy jazo va b.) bo'yicha — xodim o'z huquqi buzilganligini bilgan yoki bilishi lozim bo'lgan kundan 6 oy ichida.\n"
            "Uzrli sabablarga ko'ra o'tkazib yuborilgan muddatlar sud tomonidan tiklanishi mumkin."
        ),
        "keywords": "sudga murojaat muddati da'vo muddati ishga tiklash 3 oy oylik undirish 6 oy"
    },

    # ── 2. FUQAROLIK KODEKSI (FK) ───────────────────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "11-modda",
        "title": "Fuqarolik huquqlarini himoya qilish usullari",
        "content": (
            "Fuqarolik huquqlarini himoya qilish sud orqali quyidagi yo'llar bilan amalga oshiriladi:\n"
            "- huquqni tan olish;\n"
            "- huquq buzilishidan oldingi holatni tiklash va huquqni buzadigan harakatlarning oldini olish;\n"
            "- bitimni haqiqiy emas deb topish va uning oqibatlarini qo'llash;\n"
            "- davlat organining hujjatini haqiqiy emas deb topish;\n"
            "- majburiyatni aslicha (natura) bajarishga majbur qilish;\n"
            "- zararni to'lash;\n"
            "- neustoyka (jarima, penya) undirish;\n"
            "- ma'naviy zararni qoplash;\n"
            "- huquqiy munosabatni bekor qilish yoki o'zgartirish."
        ),
        "keywords": "huquqni himoya qilish sud orqali zararni to'lash neustoyka penya bitimni bekor qilish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "14-modda",
        "title": "Zararni to'liq qoplash",
        "content": (
            "Huquqi buzilgan shaxs o'ziga yetkazilgan zararning to'liq qoplanishini talab qilishi mumkin. Zarar deganda — huquqi buzilgan "
            "shaxsning buzilgan huquqini tiklash uchun qilgan yoki qilishi lozim bo'lgan xarajatlari, uning mol-mulki yo'qolishi yoki "
            "shikastlanishi (haqiqiy zarar), shuningdek ushbu shaxs o'z huquqlari buzilmagan taqdirda odatdagi fuqarolik muomalasi "
            "sharoitida olishi mumkin bo'lgan, lekin ololmay qolgan daromadlari (boy berilgan foyda) tushuniladi."
        ),
        "keywords": "zararni qoplash haqiqiy zarar boy berilgan foyda xarajat mol-mulk yo'qolishi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "102-modda",
        "title": "Ma'naviy zararni qoplash",
        "content": (
            "Fuqaroning sha'ni, qadr-qimmati yoki ishchanlik obro'siga putur yetkazuvchi, shuningdek shaxsning nomulkiy huquqlari yoki "
            "unga tegishli nomoddiy ne'matlarni buzuvchi harakatlar bilan yetkazilgan ma'naviy zarar (jismoniy yoki ma'naviy azob-uqubatlar) "
            "sud tomonidan pul shaklida qoplanadi. Ma'naviy zarar moddiy zarardan qat'i nazar qoplanishi lozim. Ma'naviy zararni qoplash "
            "miqdori jabrlanuvchiga yetkazilgan ruhiy va jismoniy azoblarning xarakteriga hamda aybdorning ayb darajasiga qarab sud tomonidan belgilanadi."
        ),
        "keywords": "ma'naviy zarar azob-uqubat tovon sha'n qadr-qimmat pul kompensatsiyasi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "149-modda",
        "title": "Umumiy da'vo muddati",
        "content": (
            "Umumiy da'vo muddati — uch yil. Da'vo muddati — shaxs o'zining buzilgan huquqini da'vo qo'zg'atish yo'li bilan himoya "
            "qilishi mumkin bo'lgan muddatdir. Da'vo muddati o'tganligi sud tomonidan faqat nizodagi tarafning sud qaror chiqarguniga "
            "qadar bergan arizasiga binoan qo'llanadi. Da'vo muddatining o'tishi sud tomonidan da'voni rad etish haqida qaror chiqarish uchun "
            "mustaqil asos bo'ladi."
        ),
        "keywords": "da'vo muddati 3 yil da'vo qo'zg'atish o'tib ketgan muddat rad etish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "236-modda",
        "title": "Majburiyatlarni lozim darajada bajarish",
        "content": (
            "Majburiyatlar majburiyat shartlariga va qonun hujjatlari talablariga muvofiq, bunday shartlar va talablar bo'lmaganida esa — "
            "ish muomalasi odatlariga yoki odatda qo'yiladigan boshqa talablarga muvofiq lozim darajada bajarilishi kerak. Majburiyatni "
            "bajarishdan bir tomonlama bosh tortishga va uning shartlarini bir tomonlama o'zgartirishga yo'l qo'yilmaydi."
        ),
        "keywords": "majburiyat shartnoma lozim darajada bajarish bir tomonlama voz kechish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "260-modda",
        "title": "Neustoyka (jarima, penya)",
        "content": (
            "Qonun hujjatlari yoki shartnoma bilan belgilangan, qarzdor majburiyatni bajarmagan yoki lozim darajada bajarmagan taqdirda "
            "kreditorga to'lashi shart bo'lgan pul summasi neustoyka hisoblanadi. Neustoyka jarima yoki penya shaklida bo'ladi. Majburiyatni "
            "bajarish kechiktirilganida qarzdor kechiktirilgan har bir kun uchun majburiyat summasiga nisbatan foiz hisobida penya to'laydi."
        ),
        "keywords": "neustoyka jarima penya shartnoma buzilishi kechiktirilgan kun foiz"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "327-modda",
        "title": "Boshqa shaxslarning pul mablag'laridan noqonuniy foydalanganlik uchun foizlar",
        "content": (
            "Boshqa shaxslarning pul mablag'larini noqonuniy ushlab qolish, ularni qaytarishdan bo'yin tovlash, boshqacha tarzda to'lashni "
            "kechiktirish yoxud boshqa shaxs hisobidan asossiz olish yoki jamg'arish natijasida ulardan foydalanganlik uchun ushbu mablag'lar "
            "summasiga foizlar to'lanishi lozim. Foizlar miqdori pul mablag'lari joylashgan joyda mavjud bo'lgan bank foizining hisob stavkasi "
            "(Markaziy bankning qayta moliyalash stavkasi) bo'yicha belgilanadi. Foizlar qarz to'langan kunga qadar hisoblanadi."
        ),
        "keywords": "327-modda pul mablag'lari foiz qayta moliyalash stavkasi qarzni qaytarmaslik asossiz boyish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "382-modda",
        "title": "Shartnomani o'zgartirish va bekor qilish asoslari",
        "content": (
            "Shartnoma taraflarning kelishuvi bo'yicha o'zgartirilishi va bekor qilinishi mumkin. Taraflardan birining talabi bilan shartnoma "
            "sud tomonidan faqat quyidagi hollarda bekor qilinishi mumkin:\n"
            "1) ikkinchi taraf shartnomani jiddiy ravishda buzganida;\n"
            "2) ushbu Kodeksda, boshqa qonunlarda yoki shartnomada nazarda tutilgan o'zga hollarda.\n"
            "Taraflardan birining shartnomani buzishi ikkinchi tarafga u shartnoma tuzishda umid qilishga haqli bo'lgan narsadan "
            "ahamiyatli darajada mahrum bo'ladigan darajada zarar yetkazishi shartnomaning jiddiy buzilishi hisoblanadi."
        ),
        "keywords": "shartnomani bekor qilish sud orqali jiddiy buzish shartnoma buzilishi zarar"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "326-modda",
        "title": "Neustoyka (jarima, penya) miqdorini sud tomonidan kamaytirish",
        "content": (
            "Agar to'lanishi lozim bo'lgan neustoyka kreditorga yetkazilgan zararga nomutanosibligi ko'rinib tursa, "
            "sud neustoykani kamaytirishga haqli. Qarzdorning javobgarligini kamaytirishda majburiyatlarning qarzdor "
            "tomonidan bajarilish darajasi, majburiyatda ishtirok etuvchi taraflarning mulkiy ahvoli, shuningdek kreditorning "
            "e'tiborga molik manfaatlari hisobga olinishi mumkin. Sud alohida hollarda qarzdor va kreditorning manfaatlarini "
            "hisobga olib, kreditorga to'lanishi lozim bo'lgan neustoykani kamaytirish huquqiga ega."
        ),
        "keywords": "326-modda neustoykani kamaytirish asossiz jarima yuqori penya nomutanosiblik sud kamaytirishi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "354-modda",
        "title": "Shartnoma erkinligi va qonunga muvofiqligi",
        "content": (
            "Fuqarolar va yuridik shaxslar shartnoma tuzishda erkindirlar. Shartnoma shartlari taraflarning xohishi bilan "
            "belgilanadi, tegishli shartning mazmuni qonun hujjatlarida ko'rsatilgan hollar bundan mustasno. Agar shartnoma "
            "sharti taraflar kelishuvi bilan o'zgartirilishi mumkin bo'lmagan qonun hujjatlarining imperativ normasi bilan "
            "belgilangan bo'lsa, shartnomaning bunday normaga zid keluvchi shartlari haqiqiy emas (o'z-o'zidan haqiqiy bo'lmagan) "
            "hisoblanadi."
        ),
        "keywords": "shartnoma erkinligi imperativ norma qonunga zid shartlar haqiqiy emas o'z-o'zidan bekor"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik kodeksi",
        "article_no": "383-modda",
        "title": "Shartnomani bajarishdan bir tomonlama bosh tortish",
        "content": (
            "Shartnomani bajarishdan bir tomonlama bosh tortishga (shartnomani bir tomonlama bekor qilishga) faqat qonunda "
            "yoki taraflarning kelishuvida nazarda tutilgan hollarda yo'l qo'yiladi. Bir taraflama bekor qilish haqida ikkinchi "
            "tarafga yozma xabarnoma yuborilgan paytdan boshlab shartnoma bekor qilingan hisoblanadi."
        ),
        "keywords": "bir tomonlama bekor qilish shartnomadan voz kechish xabarnoma bekor bo'lishi"
    },
    {
        "doc_type": "QONUN",
        "code_name": "Xo'jalik yurituvchi subyektlar faoliyatining shartnomaviy-huquqiy bazasi to'g'risida Qonun",
        "article_no": "25-32 moddalar",
        "title": "Iqtisodiy shartnomalarda penya va jarimalarning eng yuqori miqdori (50% chegarasi)",
        "content": (
            "Xo'jalik shartnomalari bo'yicha tovarlarni yetkazib berish, ishlarni bajarish yoki xizmatlarni ko'rsatish "
            "kechiktirilganda, shuningdek to'lov muddati kechiktirilganda to'lanadigan penya miqdori muddati o'tgan "
            "majburiyat summasining 50 foizidan oshmasligi kerak. Shartnomada bundan ortiq miqdorda penya belgilangan "
            "taqdirda ham, sud va amaliyotda 50 foizlik qonuniy cheklov qo'llaniladi. To'lov talabnomalari akseptsiz "
            "to'lanishi faqat qonunda nazarda tutilgan hollarda mumkin."
        ),
        "keywords": "penya chegarasi 50 foiz cheklov asossiz jarima shartnomaviy huquqiy baza qonun 25 modda 32 modda"
    },

    # ── 3. OILA KODEKSI (OK) ─────────────────────────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Oila kodeksi",
        "article_no": "37-modda",
        "title": "Er-xotinning umumiy mol-mulkini bo'lish",
        "content": (
            "Er-xotinning umumiy mol-mulkini bo'lish nikoh davrida ham, nikohdan ajralgandan keyin ham, shuningdek kreditorning talabiga binoan "
            "amalga oshirilishi mumkin. Er-xotinning umumiy mol-mulki ular o'rtasidagi kelishuvga binoan bo'linishi mumkin (notarial tasdiqlangan). "
            "Nizo bo'lgan taqdirda er-xotinning umumiy mol-mulkini bo'lish, shuningdek bu mol-mulkdagi er va xotinning ulushlarini aniqlash "
            "sud tartibida amalga oshiriladi. Nikohdan ajralgan er-xotinning umumiy mol-mulkni bo'lish to'g'risidagi talablariga nisbatan "
            "uch yillik da'vo muddati qo'llanadi."
        ),
        "keywords": "mol-mulkni bo'lish er-xotin ulush tenglik 50/50 nikohdan ajrashish 3 yil muddat"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Oila kodeksi",
        "article_no": "38-modda",
        "title": "Er va xotinning har birining mulki (Xususiy mulk)",
        "content": (
            "Er va xotinning nikohga qadar o'ziga tegishli bo'lgan mol-mulki, shuningdek ulardan birining nikoh davrida hadya, meros "
            "tariqasida yoki boshqa tekin bitimlar asosida olgan mol-mulki uning o'z mulki hisoblanadi va bo'linmaydi. Shaxsiy foydalanishdagi "
            "buyumlar (kiyim-kechak, poyabzal va boshqalar), qimmatbaho buyumlar va zargarlik buyumlari bundan mustasno, nikoh davrida "
            "er-xotinning umumiy mablag'i hisobiga olingan bo'lsa ham, ulardan foydalangan er yoki xotinning xususiy mulki hisoblanadi."
        ),
        "keywords": "shaxsiy mulk bo'linmaydigan mol-mulk hadya meros nikohgacha bo'lgan mulk"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Oila kodeksi",
        "article_no": "99-modda",
        "title": "Voyaga yetmagan bolalarga aliment miqdori",
        "content": (
            "Agar voyaga yetmagan bolalariga ta'minot berish haqida ota-ona o'rtasida kelishuv bo'lmasa, aliment sud tomonidan ota-onaning "
            "har oydagi ish haqi va boshqa daromadining:\n"
            "- bir bola uchun — to'rtdan bir (1/4) qismi miqdorida;\n"
            "- ikki bola uchun — uchdan bir (1/3) qismi miqdorida;\n"
            "- uch va undan ortiq bola uchun — yarmi (1/2) miqdorida undiriladi.\n"
            "Bu to'lovlarning miqdori har bir bola uchun qonunchilikda belgilangan eng kam mehnatga haq to'lash miqdorining 26,5 foizidan "
            "kam bo'lmasligi kerak."
        ),
        "keywords": "aliment miqdori 1 bola 25% 2 bola 33% 3 bola 50% ish haqi daromad bolalar ta'minoti"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Oila kodeksi",
        "article_no": "117-modda",
        "title": "Er-xotinning bir-biriga ta'minot berish majburiyati",
        "content": (
            "Er-xotin bir-biriga moddiy yordam berishi shart. Bunday yordam berishdan bosh tortilgan taqdirda, yordamga muhtoj mehnatga "
            "layoqatsiz er yoki xotin, homiladorlik davrida va umumiy bola tug'ilgan kundan boshlab uch yil davomida xotin, nogiron bolani "
            "parvarishlayotgan er (xotin) yordam berishga qodir bo'lgan eridan (xotinidan) sud tartibida aliment undirish huquqiga ega."
        ),
        "keywords": "xotiniga aliment homiladorlik davri 3 yoshgacha bola er-xotin ta'minoti"
    },

    # ── 4. JINOYAT KODEKSI (JK) ──────────────────────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Jinoyat kodeksi",
        "article_no": "168-modda",
        "title": "Firibgarlik",
        "content": (
            "Firibgarlik, ya'ni aldash yoki ishonchni suiiste'mol qilish yo'li bilan o'zganing mulkini yoki o'zganing mulkiga bo'lgan huquqni "
            "qo'lga kiritish — jarima, majburiy jamoat ishlari yoki uch yilgacha ozodlikdan mahrum qilish bilan jazolanadi.\n"
            "Firibgarlik ancha miqdorda, bir guruh shaxslar tomonidan oldindan til biriktirib yoki kompyuter texnikasi vositalaridan "
            "foydalanib sodir etilsa — 3 yildan 5 yilgacha ozodlikdan mahrum qilish;\n"
            "Katta miqdorda, xizmat mavqeidan foydalanib sodir etilsa — 5 yildan 8 yilgacha;\n"
            "Juda ko'p miqdorda yoki uyushgan guruh tomonidan sodir etilsa — 8 yildan 10 yilgacha ozodlikdan mahrum qilish bilan jazolanadi."
        ),
        "keywords": "firibgarlik aldash ishonchni suiiste'mol qilish pulni o'zlashtirish karta firibgarligi 168-modda"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Jinoyat kodeksi",
        "article_no": "66-1-modda",
        "title": "Yarashtirish instituti (Jinoiy javobgarlikdan ozod qilish)",
        "content": (
            "Ijtimoiy xavfi katta bo'lmagan yoki uncha og'ir bo'lmagan jinoyatni birinchi marta sodir etgan shaxs, agar u o'z aybiga to'liq "
            "iqror bo'lsa, jabrlanuvchi bilan yarashsa va yetkazilgan zararni to'liq bartaraf etsa, jinoiy javobgarlikdan ozod qilinishi mumkin. "
            "Yarashtirish to'g'risidagi arizani jabrlanuvchi yoki uning qonuniy vakili surishtiruv, dastlabki tergov va sud muhokamasining "
            "istalgan bosqichida, ammo sud maslahatxonaga kirgunga qadar berishi mumkin."
        ),
        "keywords": "yarashtirish javobgarlikdan ozod qilish zarar qoplash ariza yarashuv 66-1"
    },

    # ── 5. MA'MURIY JAVOBGARLIK TO'G'RISIDAGI KODEKS (MJtK) ───────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Ma'muriy javobgarlik to'g'risidagi kodeks",
        "article_no": "40-modda",
        "title": "Tuhmat",
        "content": (
            "Tuhmat, ya'ni bila turib boshqa shaxsni sharmanda qiladigan uydirmalar tarqatish — bazaviy hisoblash miqdorining yigirma "
            "baravaridan oltmish baravarigacha miqdorda jarima solishga sabab bo'ladi. Xuddi shunday harakat matbuotda yoki ommaviy axborot "
            "vositalarida, telekommunikatsiya tarmoqlarida yoki Internet jahon axborot tarmog'ida joylashtirish orqali sodir etilsa — "
            "BHMning 20 baravaridan 40 baravarigacha jarima solinadi."
        ),
        "keywords": "tuhmat uydirma sharmanda qilish yolg'on internet tarmoq jarima 40-modda"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Ma'muriy javobgarlik to'g'risidagi kodeks",
        "article_no": "41-modda",
        "title": "Haqorat qilish",
        "content": (
            "Haqorat qilish, ya'ni shaxsning sha'ni va qadr-qimmatini qasddan kamsitish — bazaviy hisoblash miqdorining yigirma baravaridan "
            "qirq baravarigacha miqdorda jarima solishga sabab bo'ladi."
        ),
        "keywords": "haqorat qilish sha'n qadr-qimmat kamsitish so'kish jarima 41-modda"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Ma'muriy javobgarlik to'g'risidagi kodeks",
        "article_no": "131-modda",
        "title": "Transport vositalarini mast holda boshqarish",
        "content": (
            "Haydovchilarning transport vositalarini alkogolli ichimlikdan, giyohvand modda ta'siridan yoki o'zgacha tarzda mast holda "
            "boshqarishi — transport vositasini boshqarish huquqidan bir yilu olti oydan uch yilgacha muddatga mahrum qilib, bazaviy "
            "hisoblash miqdorining yigirma besh baravari miqdorida jarima solishga sabab bo'ladi."
        ),
        "keywords": "mast holda haydash alkogol prava mahrum qilish 1.5 yil 3 yil jarima 131-modda"
    },

    # ── 6. FUQAROLIK PROTSESSUAL KODEKSI (FPK) ──────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik protsessual kodeksi",
        "article_no": "189-modda",
        "title": "Da'vo arizasining mazmuni",
        "content": (
            "Da'vo arizasida quyidagilar ko'rsatilishi shart:\n"
            "1) ariza berilayotgan sudning nomi;\n"
            "2) da'vogarning F.I.Sh., yashash joyi, telefon raqamlari, elektron manzili, STIR yoki JShShIR;\n"
            "3) javobgarning nomi, yashash joyi yoki joylashgan yeri, rekvizitlari;\n"
            "4) da'vogarning talabi va da'vo asoslangan holatlar hamda ularni tasdiqlovchi dalillar;\n"
            "5) agar da'vo baholanishi lozim bo'lsa, da'voning bahosi;\n"
            "6) javobgar bilan nizoni sudgacha hal qilish (pretenziya) tartibiga rioya etilganligi haqidagi ma'lumotlar;\n"
            "7) arizaga ilova qilinayotgan hujjatlar ro'yxati.\n"
            "Ariza da'vogar yoki uning vakolatli vakili tomonidan imzolanadi."
        ),
        "keywords": "da'vo arizasi mazmuni rekvizitlar sud nomi da'vogar javobgar da'vo bahosi ilovalar"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Fuqarolik protsessual kodeksi",
        "article_no": "399-modda",
        "title": "Apellyatsiya shikoyati berish muddati",
        "content": (
            "Apellyatsiya shikoyati (protesti) sudning hal qiluv qarori qabul qilingan kundan e'tiboran bir oy ichida berilishi mumkin. "
            "Apellyatsiya shikoyati qaror chiqargan sud orqali yuqori turuvchi sudga beriladi. Uzrli sabablarga ko'ra o'tkazib yuborilgan "
            "muddat shikoyat beruvchi shaxsning iltimosnomasiga asosan sud tomonidan tiklanishi mumkin."
        ),
        "keywords": "apellyatsiya shikoyati muddat 1 oy hal qiluv qarori shikoyat berish sudga"
    },

    # ── 7. OLIY SUD PLENUMI QARORLARI ────────────────────────────────────────
    {
        "doc_type": "PLENUM",
        "code_name": "Oliy Sud Plenumi",
        "article_no": "1998-yil 12-sonli qaror",
        "title": "Sudlar tomonidan mehnat shartnomasini bekor qilishni tartibga soluvchi qonunlarning qo'llanilishi",
        "content": (
            "Sudlarga tushuntirilsinki, ish beruvchining tashabbusi bilan mehnat shartnomasini bekor qilish qonuniyligini tekshirishda "
            "sud mehnat intizomini buzish sabablarini, xodimning oldingi xulq-atvorini, ayb darajasini va oqibatlarini har tomonlama "
            "baholashi shart. Kasaba uyushmasi roziligi talab qilingan hollarda bunday rozilik olinmagan bo'lsa yoki rozilik buyruq chiqarilgandan "
            "keyin olingan bo'lsa, buyruq so'zsiz noqonuniy deb topiladi va xodim ishga tiklanadi. Ish beruvchi xodimni boshqa ishga o'tkazish "
            "imkoniyatini taklif qilmagan bo'lsa (shtat qisqarganda), ishdan bo'shatish noqonuniy hisoblanadi."
        ),
        "keywords": "plenum mehnat nizosi ishga tiklash kasaba uyushmasi shtat qisqarishi noqonuniy buyruq"
    },
    {
        "doc_type": "PLENUM",
        "code_name": "Oliy Sud Plenumi",
        "article_no": "2011-yil 06-sonli qaror",
        "title": "Sudlar tomonidan nikohdan ajratishga oid ishlarni ko'rish amaliyoti to'g'risida",
        "content": (
            "Nikohdan ajratish to'g'risidagi ishlarni ko'rishda sudlar oilani saqlab qolish choralarini ko'rishlari, oilaning barbod bo'lish "
            "sabablarini aniqlashlari lozim. Voyaga yetmagan bolalari bor er-xotinni ajratishda, er-xotinga yarashish uchun olti oygacha "
            "bo'lgan muddat tayinlanishi mumkin. Agar sud oilaning kelgusida birga yashashi va uni saqlab qolish mutlaqo imkonsiz deb "
            "topsagina nikohni bekor qiladi. Sud bir vaqtning o'zida bolalar kim bilan qolishi, aliment miqdori va mulk taqsimotini hal qiladi."
        ),
        "keywords": "plenum ajrashish nikohdan ajratish yarashuv muddati 6 oy aliment bolalar taqdiri"
    },
    {
        "doc_type": "PLENUM",
        "code_name": "Oliy Sud Plenumi",
        "article_no": "2000-yil 7-sonli qaror",
        "title": "Ma'naviy zararni qoplash haqidagi qonunlarni qo'llash amaliyoti to'g'risida",
        "content": (
            "Ma'naviy zarar — fuqaroning shaxsiy nomulkiy huquqlari yoki boshqa nomoddiy ne'matlariga tajovuz qilish natijasida "
            "boshdan kechirgan ruhiy (azoblanish, uyat, xo'rlanish, qo'rquv) yoki jismoniy (og'riq) azob-uqubatlaridir. Ma'naviy zarar "
            "moddiy zarar yetkazilgan yoki yetkazilmaganidan qat'i nazar undiriladi. Sud kompensatsiya miqdorini belgilashda jabrlanuvchining "
            "azoblanish darajasini, aybdorning xatti-harakatlarini va oqililik hamda adolat talablarini inobatga oladi."
        ),
        "keywords": "plenum ma'naviy zarar ruhiy azob tovon kompensatsiya miqdori adolat oqilonalik"
    },
    {
        "doc_type": "PLENUM",
        "code_name": "Oliy Sud Plenumi",
        "article_no": "2017-yil 35-sonli qaror",
        "title": "Firibgarlik to'g'risidagi ishlar bo'yicha sud amaliyoti to'g'risida",
        "content": (
            "Fuqarolik-huquqiy munosabatlar (masalan, qarz shartnomasi yoki mahsulot yetkazib berish majburiyati) doirasidagi majburiyatlarni "
            "bajarmaslik har doim ham firibgarlik hisoblanmaydi. Agar shaxs pul yoki mulkni olayotgan paytda uni qaytarish niyati mutlaqo bo'lmaganligi, "
            "soxta hujjatlar taqdim etgani, yashiringani yoki mablag'larni maqsadsiz sarflab yuborgani isbotlansa — bu qilmish JK 168-moddasi "
            "(firibgarlik) bilan kvalifikatsiya qilinadi. Qolgan hollarda nizo fuqarolik yoki iqtisodiy sud tartibida hal qilinishi lozim."
        ),
        "keywords": "plenum firibgarlik 168-modda qarz qaytarmaslik fuqarolik nizosi ajratish aldov"
    },

    # ── 8. SOLIQ KODEKSI (YANGI TAHRIR) ──────────────────────────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "14-modda",
        "title": "Soliq sohasidagi huquqlarni suiiste'mol qilishga yo'l qo'yilmasligi va vijdonlilik prezumpsiyasi",
        "content": (
            "Soliq to'lovchi soliq to'g'risidagi qonunchilik talablariga rioya etgan holda o'z huquqlarini amalga oshirishi lozim. "
            "Soliq to'g'risidagi qonunchilik hujjatlaridagi bartaraf etib bo'lmaydigan barcha ziddiyatlar va noaniqliklar "
            "soliq to'lovchining foydasiga talqin etiladi. Soliq to'lovchining harakatlarida ayb va soliq to'lashdan qasddan "
            "bo'yin tovlash niyati soliq organi tomonidan isbotlanishi shart. Bitimning faqat soliqni kamaytirish maqsadida "
            "tuzilganligi isbotlanmasa, soliq to'lovchining soliq imtiyozlaridan foydalanish huquqi cheklanmaydi."
        ),
        "keywords": "soliq kodeksi 14-modda vijdonlilik prezumpsiyasi noaniqliklar foydaga talqin asossiz ayblov"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "86-modda",
        "title": "Soliq to'lovchilarning huquqlari va soliq organlarining noqonuniy talablari",
        "content": (
            "Soliq to'lovchilar quyidagi huquqlarga ega:\n"
            "1) soliq organlaridan soliqlarni to'lash tartibi bo'yicha bepul axborot va tushuntirishlar olish;\n"
            "2) ortiqcha to'langan yoki ortiqcha undirilgan soliq summalarini o'z vaqtida hisobga olinishiga yoki qaytarilishiga erishish;\n"
            "3) soliq organlari va ularning mansabdor shaxslarining qonunga xilof hujjatlari, talablari hamda harakatlariga bo'ysunmaslik;\n"
            "4) soliq tekshiruvlari dalolatnomalari va soliq organlarining qarorlari ustidan belgilangan tartibda shikoyat qilish;\n"
            "5) soliq siri saqlanishini talab qilish."
        ),
        "keywords": "soliq to'lovchi huquqlari 86-modda noqonuniy talabga bo'ysunmaslik shikoyat qilish soliq siri"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "138-modda",
        "title": "Kameral soliq tekshiruvi tartibi va soliq to'lovchining himoyasi",
        "content": (
            "Kameral soliq tekshiruvi soliq organi tomonidan soliq to'lovchi huzuriga bormasdan, soliq hisobotlari va mavjud axborotlar "
            "asosida o'tkaziladi. Tekshiruv davomida xatolar yoki tafovutlar aniqlansa, soliq organi soliq to'lovchiga aniqlangan tafovutlar "
            "asoslari ko'rsatilgan holda talabnoma yuboradi. Soliq to'lovchi talabnoma olingan kundan e'tiboran 10 kun ichida tushuntirish "
            "yoki tuzatilgan soliq hisobotini taqdim etishga haqli. Soliq organi tushuntirishlarni inobatga olmagan taqdirda, soliq "
            "to'lovchiga qo'shimcha soliq hisoblash to'g'risida asoslantirilgan qaror qabul qiladi."
        ),
        "keywords": "kameral soliq tekshiruvi 138-modda talabnoma 10 kun muddat tushuntirish berish asossiz soliq"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "140-modda",
        "title": "Sayyor soliq tekshiruvi shartlari va cheklovlari",
        "content": (
            "Sayyor soliq tekshiruvi soliq to'lovchilarning faoliyat ko'rsatish joyida o'tkaziladi. Tekshiruv faqat soliq organining "
            "buyrug'i, tekshirish dasturi va maxsus ro'yxatga olish guvohnomasi mavjud bo'lganda boshlanishi mumkin. Sayyor soliq "
            "tekshiruvi davomida soliq to'lovchining ishlab chiqarish, savdo yoki xizmat ko'rsatish faoliyatini to'xtatib qo'yishga, "
            "bino va asbob-uskunalarni asossiz muhrlashga yo'l qo'yilmaydi. Tekshiruv muddati 10 ish kunidan oshishi mumkin emas."
        ),
        "keywords": "sayyor soliq tekshiruvi 140-modda buyruq 10 kun faoliyatni to'xtatmaslik tekshirish dasturi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "147-modda",
        "title": "Soliq organlarining qarorlari ustidan sudga shikoyat qilish va ijroni to'xtatish",
        "content": (
            "Soliq to'lovchi soliq organining qarori, harakati yoki harakatsizligi ustidan yuqori turuvchi organga yoki to'g'ridan-to'g'ri "
            "sudga (ma'muriy sudga) shikoyat qilishga haqli. Soliq to'lovchi tomonidan sudga shikoyat (da'vo arizasi) berilishi "
            "soliq organining hisoblangan soliqlar, penyalar va moliyaviy jarimalarni undirish to'g'risidagi qarori ijrosini "
            "sudning qonuniy kuchga kirgan qarori qabul qilinguniga qadar to'xtatib turadi."
        ),
        "keywords": "soliq qarori ustidan shikoyat 147-modda ma'muriy sud ijroni to'xtatish jarima bekor qilish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Soliq kodeksi",
        "article_no": "103-105 moddalar",
        "title": "Ortiqcha to'langan yoki undirilgan soliqlarni qaytarish va foizlar undirish",
        "content": (
            "Ortiqcha to'langan yoki soliq organi tomonidan ortiqcha undirilgan soliq summasi soliq to'lovchining yozma arizasiga "
            "binoan 15 kun muddatda uning bank hisobvarag'iga qaytarilishi yoki boshqa soliq qarzlari bo'yicha hisobga olinishi lozim. "
            "Agar soliq organi ortiqcha summani belgilangan muddatda qaytarmasa, qaytarilmagan har bir kechiktirilgan kun uchun "
            "Markaziy bankning amaldagi qayta moliyalash stavkasi bo'yicha foizlar hisoblanadi va soliq to'lovchiga to'lanadi."
        ),
        "keywords": "ortiqcha soliqni qaytarish 103-modda 105-modda 15 kun muddat foizlar qayta moliyalash stavkasi"
    },

    # ── 9. YER KODEKSI VA KOMPENSATSIYA TO'G'RISIDAGI QONUN ──────────────────
    {
        "doc_type": "KODEKS",
        "code_name": "Yer kodeksi",
        "article_no": "36-modda",
        "title": "Yer uchastkasiga bo'lgan huquqning bekor bo'lishining qat'iy asoslari",
        "content": (
            "Yer uchastkasiga egalik qilish, foydalanish yoki ijara huquqi faqat qonunda ko'rsatilgan quyidagi hollarda bekor bo'ladi:\n"
            "- yer uchastkasidan ixtiyoriy voz kechilganda;\n"
            "- yer berilgan muddat tugaganda;\n"
            "- yuridik shaxs tugatilganda;\n"
            "- yerdan belgilangan maqsadda foydalanilmaganda (uzrli sabablarsiz 3 yil davomida);\n"
            "- yer uchastkasi jamoat ehtiyojlari uchun qonunda belgilangan tartibda olib qo'yilganda.\n"
            "Boshqa hollarda davlat organlarining yer uchastkasiga bo'lgan huquqni bekor qilish to'g'risidagi qarorlari noqonuniy hisoblanadi."
        ),
        "keywords": "yer kodeksi 36-modda yer huquqini bekor qilish noqonuniy olib qo'yish yer tortib olish"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Yer kodeksi",
        "article_no": "41-modda",
        "title": "Yer egalari va yerdan foydalanuvchilar huquqlarining davlat kafolatlari",
        "content": (
            "Yer uchastkalarini davlat va jamoat ehtiyojlari uchun olib qo'yishga faqat yer egasi yoki yerdan foydalanuvchining "
            "roziligi bilan hamda yetkazilgan zararlar, jumladan boy berilgan foyda va ko'chmas mulk qiymati oldindan to'liq qoplangandan "
            "keyingina yo'l qo'yiladi. Yer egasining huquqlarini buzuvchi davlat yoki mahalliy hokimiyat organlarining hujjatlari "
            "sud tartibida haqiqiy emas deb topiladi."
        ),
        "keywords": "yer kodeksi 41-modda davlat kafolatlari boy berilgan foyda hokim qarorini bekor qilish"
    },
    {
        "doc_type": "QONUN",
        "code_name": "Kompensatsiya to'g'risidagi Qonun (O'RQ-781)",
        "article_no": "4, 11, 14-moddalar",
        "title": "Yer uchastkasini olib qo'yish va mulkni buzish ('snos') shartlari hamda bozor bahosidagi kompensatsiya",
        "content": (
            "1. Yer uchastkasini jamoat ehtiyojlari uchun olib qo'yish faqat Qoraqalpog'iston Jo'qorg'i Kengesi, xalq deputatlari "
            "viloyatlar va Toshkent shahar Kengashlari qarori bilan amalga oshiriladi (tuman/shahar hokimlariga bu vakolat berilmagan!).\n"
            "2. Kompensatsiya turlari: bozor qiymatidagi pul mablag'lari, teng qiymatli boshqa ko'chmas mulk berish, ko'chish xarajatlari "
            "va vaqtincha ijara xarajatlari, shuningdek boy berilgan foyda to'liq qoplanadi.\n"
            "3. Olib qo'yilayotgan yer uchastkasidagi bino va inshootlarni kompensatsiya to'liq to'lanmasdan turib buzish QAT'IYAN TAQIQLANADI. "
            "Mulkiy nizo sud tomonidan ko'rib chiqilayotgan paytda buzish ishlarini olib borish jinoiy javobgarlikka sabab bo'ladi."
        ),
        "keywords": "snos buzish kompensatsiya o'rq 781 qonun bozor bahosi kengash qarori hokim noqonuniy buzishi"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Yer kodeksi",
        "article_no": "86-modda",
        "title": "Yer egalari va tadbirkorlarga yetkazilgan zararlarning to'liq hajmda qoplanishi",
        "content": (
            "Yer uchastkasi olib qo'yilganda yoki yer egalarining huquqlari cheklanganda yetkazilgan zararlar to'liq hajmda, shu jumladan "
            "boy berilgan foyda ham qoplanishi shart. Zararlar miqdorini baholash mustaqil baholovchi tashkilot tomonidan bozor qiymatida "
            "amalga oshiriladi. Agar yer egasi baholash natijasidan norozi bo'lsa, kompensatsiya miqdori sud tomonidan tayinlangan "
            "sud ekspertizasi xulosasi asosida belgilanadi."
        ),
        "keywords": "yer kodeksi 86-modda zararni qoplash boy berilgan foyda baholash bozor qiymati ekspertiza"
    },

    # ── 10. IQTISODIY PROTSESSUAL KODEKSI (IPK — BIZNES VA KORPORATIV NIZOLAR) ─
    {
        "doc_type": "KODEKS",
        "code_name": "Iqtisodiy protsessual kodeksi",
        "article_no": "25-26 moddalar",
        "title": "Iqtisodiy sudga taalluqli biznes va korporativ nizolar doirasi",
        "content": (
            "Iqtisodiy sudlar yuridik shaxslar, yakka tartibdagi tadbirkorlar va davlat organlari o'rtasidagi iqtisodiy nizolarni hal qiladi:\n"
            "1) xo'jalik shartnomalarini tuzish, o'zgartirish, bekor qilish va ulardan kelib chiqadigan qarzdorliklar;\n"
            "2) mulk huquqini tan olish va asossiz boyish bo'yicha nizolar;\n"
            "3) MChJ va aksiyadorlik jamiyatlari ishtirokchilari (muassislari) o'rtasidagi korporativ nizolar (ulushlarni taqsimlash, dividendlar, ta'sischilar qarorlarini bekor qilish);\n"
            "4) bankrotlik (to'lovga qobiliyatsizlik) ishlari."
        ),
        "keywords": "iqtisodiy sud ipk 25-modda korporativ nizo mchj ta'sischi ulush dividend biznes qarzdorlik"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Iqtisodiy protsessual kodeksi",
        "article_no": "132-modda",
        "title": "Da'voni ta'minlash choralari (javobgarning hisob raqamini xatlash)",
        "content": (
            "Iqtisodiy sud da'vogarning arizasiga ko'ra, agar da'voni ta'minlash choralarini ko'rmaslik sud qarorining ijrosini "
            "qiyinlashtirsa yoki imkonsiz qilib qo'ysa, da'voni ta'minlash choralarini ko'radi. Ta'minlash choralari:\n"
            "1) javobgarga tegishli mol-mulkni yoki pul mablag'larini (da'vo summasi miqdorida) xatlash (arest qo'yish);\n"
            "2) javobgarga muayyan harakatlarni amalga oshirishni taqiqlash;\n"
            "3) boshqa shaxslarga nizo predmeti bo'lgan mol-mulkni javobgarga topshirishni taqiqlash.\n"
            "Ariza da'vo arizasi kelib tushgan kuni yoki ertasi kundan kechiktirmay sudya tomonidan ko'rib chiqiladi."
        ),
        "keywords": "da'voni ta'minlash ipk 132-modda hisob raqamni muzlatish arest mol-mulkni xatlash ijroni ta'minlash"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Iqtisodiy protsessual kodeksi",
        "article_no": "149-modda",
        "title": "Iqtisodiy sudga da'vo arizasi berish talablari va pretenziya tartibi",
        "content": (
            "Iqtisodiy sudga da'vo arizasi yozma shaklda yoki elektron tarzda (sud portali orqali) taqdim etiladi. Da'vo arizasida "
            "taraflarning to'liq rekvizitlari (nomi, STIR/INN, bank hisob raqamlari, pochta va elektron manzillari), da'vo talablari, "
            "moddiy va protsessual qonun normalari, da'vo bahosi va davlat boji hisob-kitobi ko'rsatilishi shart. Agar qonunda yoki "
            "shartnomada nizoni sudgacha hal qilish (pretenziya) tartibi nazarda tutilgan bo'lsa, javobgarga talabnoma (pretenziya) "
            "yuborilganligi va unga javob olinganligi yoki javob berish muddati o'tganligini tasdiqlovchi hujjat ilova qilinishi shart."
        ),
        "keywords": "iqtisodiy sud da'vo arizasi ipk 149-modda rekvizitlar pretenziya davlat boji sud portali"
    },
    {
        "doc_type": "KODEKS",
        "code_name": "Iqtisodiy protsessual kodeksi",
        "article_no": "192-modda",
        "title": "Iqtisodiy sud qarorlari ustidan apellyatsiya shikoyati berish muddati",
        "content": (
            "Iqtisodiy sudning qonuniy kuchga kirmagan hal qiluv qarori ustidan apellyatsiya shikoyati qaror qabul qilingan kundan "
            "e'tiboran bir oy ichida berilishi mumkin. Shikoyat qaror qabul qilgan iqtisodiy sud orqali apellyatsiya instansiyasi sudiga "
            "beriladi. O'tkazib yuborilgan muddat uzrli sabablar mavjud bo'lganda qaror qabul qilingan kundan olti oydan kechiktirmay "
            "berilgan iltimosnomaga binoan sud tomonidan tiklanishi mumkin."
        ),
        "keywords": "ipk apellyatsiya shikoyati muddat 1 oy iqtisodiy sud hal qiluv qarori qayta ko'rish"
    },

    # ── 11. TADBIRKORLIK ERKINLIGI KAFOLATLARI TO'G'RISIDA QONUN ─────────────
    {
        "doc_type": "QONUN",
        "code_name": "Tadbirkorlik faoliyati erkinligining kafolatlari to'g'risida Qonun",
        "article_no": "18, 42-moddalar",
        "title": "Tadbirkorlik faoliyatiga davlat organlarining aralashuviga yo'l qo'yilmasligi va tadbirkor foydasiga prezumpsiya",
        "content": (
            "Davlat organlari, ularning mansabdor shaxslari tadbirkorlik subyektlarining qonun hujjatlariga muvofiq amalga "
            "oshirilayotgan faoliyatiga aralashishga haqli emas. Qonunchilik hujjatlarida tadbirkorlik faoliyatini amalga oshirish "
            "bilan bog'liq holda yuzaga keladigan barcha bartaraf etib bo'lmaydigan ziddiyatlar, noaniqliklar va bo'shliqlar "
            "tadbirkorlik subyektining foydasiga talqin etiladi. Tadbirkorlik subyektiga davlat organi tomonidan yetkazilgan zararlar "
            "aybdor organning mablag'lari hisobidan to'liq hajmda qoplanishi shart."
        ),
        "keywords": "tadbirkorlik kafolatlari 18-modda 42-modda aralashmaslik noaniqlik tadbirkor foydasiga zararni qoplash"
    }
]


def populate_statutes():
    """Barcha rasmiy moddalar va plenum qarorlarini SQLite bazasiga yozadi."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("DELETE FROM legal_statutes")
    cur.execute("DELETE FROM legal_statutes_fts")

    for item in STATUTES_DATA:
        cur.execute("""
            INSERT INTO legal_statutes(doc_type, code_name, article_no, title, content, keywords)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item["doc_type"], item["code_name"], item["article_no"],
            item["title"], item["content"], item["keywords"]
        ))

        cur.execute("""
            INSERT INTO legal_statutes_fts(code_name, article_no, title, content)
            VALUES (?, ?, ?, ?)
        """, (
            item["code_name"], item["article_no"], item["title"], item["content"]
        ))

    conn.commit()
    conn.close()
    print(f"[STATUTES] Muvaffaqiyatli yuklandi: {len(STATUTES_DATA)} ta rasmiy qonun moddalari va plenum qarorlari.")
    return len(STATUTES_DATA)


if __name__ == "__main__":
    populate_statutes()
