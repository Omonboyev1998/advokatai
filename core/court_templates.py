"""
core/court_templates.py — O'zbekiston Respublikasi Sud Portallari (my.sud.uz va template.sud.uz)
Standartlariga Muvozanatlangan Rasmiy Da'vo Arizalari va Hujjat Shablonlari Registri.

Ushbu modul:
1. my.sud.uz (Fuqarolik, iqtisodiy va ma'muriy sudlar bo'yicha da'vo arizalari)
2. template.sud.uz (Oliy sudning Universal Template tizimidagi 115 ta rasmiy shablon)
3. FPK 189-191, IPK 148-150 va MSYUK moddalaridagi qat'iy protsessual talablarni
birlashtirgan to'liq katalog va shablon generatori hisoblanadi.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

# Fuqarolik ishlari bo'yicha sudlar (FIB / my.sud.uz/claim-simples/civil) asosiy toifalari
CIVIL_CLAIM_CATEGORIES = {
    "qarz_undirish": {
        "title": "Qarz shartnomasi (tilxat) bo'yicha qarz va foizlarni undirish haqida da'vo arizasi",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["FK 732, 734, 735, 736-moddalari", "FK 327-moddasi"],
        "procedural_law": ["FPK 189, 190, 191-moddalari"],
        "duty_rules": "Da'vo bahosidan 4 foiz (kamida 1 BHM, FPK 105-modda / Davlat boji to'g'risidagi qonun)",
        "mandatory_evidence": [
            "Qarz shartnomasi yoki tilxatning asli yoki nusxasi",
            "Qarzni qaytarish talabi (ogohlantirish xati, pochta kvitansiyasi)",
            "Bank ko'chirmasi yoki to'lov topshiriqnomasi (pul o'tkazilgan bo'lsa)",
            "Davlat boji va pochta xarajati to'langanligi kvitansiyasi"
        ],
        "default_prayer": [
            "Javobgardan da'vogar foydasiga asosiy qarz summasi {qarz_summasi} so'm undirilsin.",
            "Javobgardan qarzni qaytarish kechiktirilganligi uchun {penya_summasi} so'm foiz (penya) undirilsin.",
            "Da'vogar tomonidan to'langan {davlat_boji} so'm davlat boji va {pochta} so'm pochta xarajatlari javobgar hisobidan undirilsin."
        ]
    },
    "nikohdan_ajratish": {
        "title": "Nikohdan ajratish haqida da'vo arizasi",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["Oila kodeksi 37, 38, 40, 41, 42-moddalari"],
        "procedural_law": ["FPK 189, 190-moddalari"],
        "duty_rules": "BHMning 2 baravari (birinchi nikoh uchun) yoki BHMning 4 baravari (takroriy nikoh uchun)",
        "mandatory_evidence": [
            "Nikoh tuzilganligi to'g'risidagi guvohnomaning asl nusxasi",
            "Bolalarning tug'ilganlik to'g'risidagi guvohnomalari nusxasi",
            "Oila yarashish komissiyasi / Mahalla xulosasi",
            "Davlat boji to'langanligi to'g'risida kvitansiya"
        ],
        "default_prayer": [
            "Da'vogar va javobgar o'rtasida {nikoh_sanasi} yilda tuzilgan nikoh (dalolatnoma raqami {dalolatnoma_raqami}) bekor qilinsin.",
            "Voyaga yetmagan farzandlar tarbiyasi onasi/otasi qaramog'iga qoldirilsin."
        ]
    },
    "aliment_undirish": {
        "title": "Voyaga yetmagan bolalar ta'minoti uchun aliment undirish haqida da'vo arizasi / sud buyrug'i",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["Oila kodeksi 96, 99, 102, 103, 104-moddalari"],
        "procedural_law": ["FPK 171-moddasi (sud buyrug'i) yoki FPK 189-moddasi (da'vo tartibi)"],
        "duty_rules": "Da'vogar davlat boji to'lashdan ozod qilingan (keyinchalik javobgardan undiriladi)",
        "mandatory_evidence": [
            "Nikoh tuzilganligi yoki bekor qilinganligi to'g'risidagi guvohnoma",
            "Bolaning tug'ilganlik to'g'risidagi guvohnomasi nusxasi",
            "Da'vogarning bola bilan birga yashayotganligi haqida ma'lumotnoma (mahalla)",
            "Javobgarning ish joyi va daromadlari haqida ma'lumot (mavjud bo'lsa)"
        ],
        "default_prayer": [
            "Javobgardan da'vogar foydasiga voyaga yetmagan bola(lar) ta'minoti uchun har oyda daromadining belgilangan qismida aliment undirilsin."
        ]
    },
    "uy_joydan_kochirib_chiqarish": {
        "title": "Uy-joydan foydalanish huquqini yo'qotgan deb topish va ko'chirib chiqarish haqida da'vo arizasi",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["Uy-joy kodeksi 32, 52, 53-moddalari", "FK 164, 182-moddalari"],
        "procedural_law": ["FPK 189, 190, 191-moddalari"],
        "duty_rules": "BHMning 2 baravari (mulkiy bo'lmagan xarakterdagi da'volar)",
        "mandatory_evidence": [
            "Mulk huquqini tasdiqlovchi hujjat (kadastr, oldi-sotdi yoki hadya shartnomasi)",
            "Doimiy yashash joyi ma'lumotnomasi / 'Proverka' dalolatnomasi",
            "Javobgarning uzrli sabablarsiz 6 oydan ortiq yashamayotganligi haqida mahalla dalolatnomasi",
            "Davlat boji to'lovi kvitansiyasi"
        ],
        "default_prayer": [
            "Javobgar da'vogarga tegishli {uy_manzili} manzilidagi uy-joydan foydalanish huquqini yo'qotgan deb topilsin.",
            "Javobgar ushbu uy-joydan majburiy tartibda ko'chirilsin va ro'yxatdan chiqarilsin."
        ]
    },
    "mehnat_nizosi_ishga_tiklash": {
        "title": "Ishga tiklash va majburiy progul uchun ish haqi undirish haqida da'vo arizasi",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["Yangi Mehnat kodeksi 161, 171, 173, 541, 542, 543-moddalari"],
        "procedural_law": ["FPK 189, 190-moddalari"],
        "duty_rules": "Xodim da'vo arizasi berishda davlat boji to'lashdan ozod qilingan (MK 545-modda)",
        "mandatory_evidence": [
            "Mehnat shartnomasi yoki mehnat daftarchasidan ko'chirma (yoki my.mehnat.uz ko'chirmasi)",
            "Ish beruvchining ishdan bo'shatish to'g'risidagi buyrug'i",
            "Oxirgi oylik maoshlari to'g'risidagi ma'lumotnoma",
            "Kasaba uyushmasi roziligi olinmaganligi yoki protsessual buzilish dalillari"
        ],
        "default_prayer": [
            "Ish beruvchining {buyruq_sanasi} dagi {buyruq_raqami}-sonli buyrug'i noqonuniy deb topilsin va bekor qilinsin.",
            "Da'vogar o'zining avvalgi lavozimiga ishga tiklansin.",
            "Javobgardan majburiy progul kunlari uchun o'rtacha oylik ish haqi va {manaviy_zarar} so'm ma'naviy zarar undirilsin."
        ]
    },
    "moddiy_manaviy_zarar": {
        "title": "Yetkazilgan moddiy va ma'naviy zararni qoplash haqida da'vo arizasi (DTP, jinoyat oqibatida yoki huquqbuzarlik)",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["FK 985, 999, 1021, 1022-moddalari"],
        "procedural_law": ["FPK 189, 190, 191-moddalari"],
        "duty_rules": "Moddiy zarar bo'yicha da'vo bahosidan 4 foiz; Ma'naviy zarar bo'yicha BHM 1 baravari",
        "mandatory_evidence": [
            "Huquqbuzarlikni yoki YTHni tasdiqlovchi organ qarori / Sud hukmi",
            "Yetkazilgan moddiy zarar bo'yicha mustaqil baholovchi xulosasi",
            "Davolanish xarajatlari kvitansiyalari, dori-darmon cheklari (tan jarohati bo'lsa)",
            "Davlat boji to'lovi kvitansiyasi"
        ],
        "default_prayer": [
            "Javobgardan da'vogar foydasiga {moddiy_zarar} so'm moddiy zarar undirilsin.",
            "Javobgardan da'vogar foydasiga {manaviy_zarar} so'm ma'naviy zarar undirilsin.",
            "Davlat boji va ekspertiza xarajatlari javobgar hisobiga yuklatilsin."
        ]
    },
    "meros_taqsimoti": {
        "title": "Meros mulkini taqsimlash va merosdagi ulushni ajratish haqida da'vo arizasi",
        "court_type": "Fuqarolik ishlari bo'yicha tumanlararo sudi",
        "substantive_law": ["FK 1112, 1118, 1134, 1135, 1146, 1150-moddalari"],
        "procedural_law": ["FPK 189, 190, 191-moddalari"],
        "duty_rules": "Da'vo qilinayotgan mulk ulushi bahosidan 4 foiz",
        "mandatory_evidence": [
            "Meros qoldiruvchining o'lim to'g'risidagi guvohnomasi",
            "Qarindoshlik munosabatlarini tasdiqlovchi FHDYo guvohnomalari",
            "Notariusning meros ishi ochilganligi yoki rad etish haqidagi qarori",
            "Meros mol-mulkining huquqiy hujjatlari (kadastr, texnik pasport)"
        ],
        "default_prayer": [
            "Meros qoldiruvchidan qolgan mol-mulk tarkibi aniqlanib, da'vogarning qonuniy {ulush_miqdori} ulushi ajratib berilsin."
        ]
    }
}

# Iqtisodiy sudlar (IPK / template.sud.uz Universal Templates) asosiy toifalari
ECONOMIC_CLAIM_CATEGORIES = {
    "yetkazib_berish_qarzdorlik": {
        "title": "Mahsulot yetkazib berish (old-sotdi) shartnomasi bo'yicha qarzdorlik va penya undirish haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 377, 382, 437, 442, 444-moddalari", "'Xo'jalik yurituvchi subyektlar faoliyatining shartnomaviy-huquqiy bazasi to'g'risida'gi Qonun"],
        "procedural_law": ["IPK 148, 149, 150-moddalari"],
        "duty_rules": "Da'vo bahosidan 2 foiz (kamida 1 BHM, IPK 113-modda / Davlat boji to'g'risidagi qonun)",
        "mandatory_evidence": [
            "Tegishli shartnoma nusxasi",
            "Hisobvaraq-fakturalar (ESF / didox/soliq tizimidan)",
            "Solishtirma dalolatnoma (Akt sverki)",
            "Sudgacha talabnoma (pretenziya) va uning topshirilganligini tasdiqlovchi pochta kvitansiyasi",
            "Davlat boji va pochta xarajati to'langanligi to'g'risida to'lov topshiriqnomasi"
        ],
        "default_prayer": [
            "Javobgar hisobidan da'vogar foydasiga yetkazib berilgan tovarlar uchun {asosiy_qarz} so'm asosiy qarz undirilsin.",
            "Javobgardan majburiyatni kechiktirganlik uchun {penya_summasi} so'm penya undirilsin.",
            "To'langan {davlat_boji} so'm davlat boji va pochta xarajatlari javobgar zimmasiga yuklatilsin."
        ]
    },
    "pudrat_shartnomasi_qarzdorlik": {
        "title": "Qurilish / Pudrat shartnomasi bo'yicha bajarilgan ishlar haqini va penya undirish haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 631, 638, 666, 673, 674-moddalari"],
        "procedural_law": ["IPK 148, 149, 150-moddalari"],
        "duty_rules": "Da'vo bahosidan 2 foiz (kamida 1 BHM)",
        "mandatory_evidence": [
            "Pudrat shartnomasi va uning smetalari",
            "Bajarilgan ishlarni qabul qilish dalolatnomalari (Forma-2 / Forma-3, ESF)",
            "Pretenziya xati va uning pochta kvitansiyasi",
            "Davlat boji to'lovi to'lov topshiriqnomasi"
        ],
        "default_prayer": [
            "Javobgardan pudrat ishlari haqi uchun {asosiy_qarz} so'm asosiy qarzdorlik undirilsin.",
            "Kechiktirilgan har bir kun uchun hisoblangan {penya_summasi} so'm penya undirilsin."
        ]
    },
    "ijara_qarzdorlik_va_bekor_qilish": {
        "title": "Ijara shartnomasi bo'yicha qarzdorlikni undirish, shartnomani bekor qilish va binoni bo'shatish haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 535, 544, 551, 553, 555-moddalari"],
        "procedural_law": ["IPK 148, 149, 150-moddalari"],
        "duty_rules": "Undirilayotgan ijara haqi bahosidan 2 foiz + shartnomani bekor qilish uchun BHM 10 baravari",
        "mandatory_evidence": [
            "Bino/inshoot ijara shartnomasi",
            "Qabul qilish-topshirish dalolatnomasi",
            "Ijara haqini to'lash talabnomasi va ogohlantirish xati",
            "Hisob-kitob varaqasi va bank to'lov hujjatlari"
        ],
        "default_prayer": [
            "Javobgardan da'vogar foydasiga {ijara_qarzi} so'm ijara qarzdorligi undirilsin.",
            "Taraflar o'rtasidagi {shartnoma_sanasi} dagi {shartnoma_raqami}-sonli ijara shartnomasi bekor qilinsin.",
            "Javobgar ijaraga olingan binoni majburiy ravishda bo'shatib berishga majbur qilinsin."
        ]
    },
    "xizmat_korsatish_qarzdorlik": {
        "title": "Haq evaziga xizmat ko'rsatish shartnomasi bo'yicha qarzdorlikni undirish haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 703, 705, 706-moddalari"],
        "procedural_law": ["IPK 148, 149, 150-moddalari"],
        "duty_rules": "Da'vo bahosidan 2 foiz (kamida 1 BHM)",
        "mandatory_evidence": [
            "Xizmat ko'rsatish shartnomasi",
            "Xizmat ko'rsatilganligini tasdiqlovchi dalolatnoma (Akt vypolnennyx rabot/uslug)",
            "Elektron hisobvaraq-faktura (ESF)",
            "Pretenziya nusxasi va pochta kvitansiyasi"
        ],
        "default_prayer": [
            "Javobgardan ko'rsatilgan xizmatlar uchun {asosiy_qarz} so'm asosiy qarz va {penya_summasi} so'm penya undirilsin."
        ]
    },
    "kredit_va_garov_undiruvi": {
        "title": "Kredit shartnomasi bo'yicha qarzni undirish va undiruvni garovga qaratish haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 264, 280, 281, 744, 745-moddalari", "'Garov to'g'risida'gi Qonun"],
        "procedural_law": ["IPK 148, 149-moddalari"],
        "duty_rules": "Da'vo bahosidan 2 foiz",
        "mandatory_evidence": [
            "Kredit shartnomasi",
            "Garov (ipoteka) shartnomasi va taqiq solinganlik ma'lumotnomasi",
            "Kredit hisobvaraqlari ko'chirmasi va qarzdorlik hisob-kitobi",
            "Kreditni muddatidan oldin qaytarish to'g'risidagi talabnoma"
        ],
        "default_prayer": [
            "Qarzdordan kredit qarzdorligi {kredit_summasi} so'm undirilsin.",
            "Undiruv garovdagi mol-mulkka ({garov_nomi}) qaratilib, ochiq auksion orqali sotish belgilansin."
        ]
    },
    "shartnomani_haqiqiy_emas_deb_topish": {
        "title": "Bitimni (shartnomani) haqiqiy emas deb topish va haqiqiy emaslik oqibatlarini qo'llash haqida da'vo arizasi",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["FK 113, 114, 115, 116, 122, 124, 125-moddalari"],
        "procedural_law": ["IPK 148, 149, 150-moddalari"],
        "duty_rules": "BHMning 10 baravari (nomulkiy talab) + mulkiy oqibat bo'lsa 2 foiz",
        "mandatory_evidence": [
            "Nizolashilayotgan shartnoma nusxasi",
            "Vakolat doirasidan chetga chiqilganligi yoki soxtaligini tasdiqlovchi hujjatlar (ustav, qarorlar)",
            "Yetkazilgan zarar va ikki tomonlama restitutsiya asoslari",
            "Davlat boji to'lovi"
        ],
        "default_prayer": [
            "Taraflar o'rtasida {shartnoma_sanasi} da tuzilgan {shartnoma_raqami}-sonli shartnoma haqiqiy emas deb topilsin.",
            "Taraflarning dastlabki holatga qaytishi (restitutsiya) ta'minlansin."
        ]
    },
    "bankrotlik_arizasi": {
        "title": "Qarzdor yuridik shaxsni to'lovga qobiliyatsiz (bankrot) deb topish haqida ariza",
        "court_type": "Tumanlararo Iqtisodiy sudi",
        "substantive_law": ["'To'lovga qobiliyatsizlik to'g'risida'gi Qonun moddalari"],
        "procedural_law": ["IPK 148-moddasi, To'lovga qobiliyatsizlik to'g'risidagi qonun"],
        "duty_rules": "BHMning 3 baravari (yoki Qonunda belgilangan maxsus stavka)",
        "mandatory_evidence": [
            "Qarzdorlikni tasdiqlovchi qonuniy kuchga kirgan sud hujjatlari",
            "MIBning ijro hujjati bo'yicha undiruv imkonsizligi haqidagi dalolatnomasi",
            "Qarzdorga bildirishnoma yuborilganligi ma'lumotnomasi"
        ],
        "default_prayer": [
            "Qarzdor {qarzdor_nomi} to'lovga qobiliyatsiz (bankrot) deb topilsin va tugatish/sog'lomlashtirish jarayoni boshlansin.",
            "Sud boshqaruvchisi tayinlansin."
        ]
    }
}

# Universal shablon standarti (Oliy sud template.sud.uz talablari)
UNIVERSAL_TEMPLATE_STRUCTURE = {
    "court_header": {
        "court_name": "[Fuqarolik ishlari bo'yicha / Tumanlararo Iqtisodiy] sudiga",
        "plaintiff": "Da'vogar: [F.I.Sh. / Tashkilot nomi], STIR/JShShIR: [...], Manzil: [...], Tel: [...], E-pochta: [...]",
        "defendant": "Javobgar: [F.I.Sh. / Tashkilot nomi], STIR/JShShIR: [...], Manzil: [...], Tel: [...], E-pochta: [...]",
        "third_party": "Uchinchi shaxs (agar bo'lsa): [Nomi, manzili, tel]",
        "claim_value": "Da'vo bahosi: {claim_amount} so'm",
        "state_duty": "Davlat boji: {state_duty} so'm, Pochta xarajati: {postal_fee} so'm"
    },
    "title_block": "DA'VO ARIZASI\n({claim_subject})",
    "narrative_sections": [
        "1. Huquqiy munosabatning vujudga kelishi (shartnoma, bitim, qarindoshlik yoki huquqiy fakt)",
        "2. Majburiyatning buzilishi holatlari (to'lov amalga oshirilmaganligi, noqonuniy xatti-harakatlar, sanalar va summalar)",
        "3. Sudgacha nizoni hal etish tartibiga rioya etilganligi (talabnoma / ogohlantirish xati sanasi va unga javob olinmaganligi)",
        "4. Qonuniy asoslar (O'zbekiston Respublikasi Kodekslari va qonun moddalari, Oliy Sud Plenumi qarorlari)"
    ],
    "prayer_keyword": "SO'RAYMAN:",
    "mandatory_attachments": [
        "Da'vo arizasi nusxasi (sudga qog'ozda berilganda javobgarlar soniga ko'ra; my.sud.uz da shart emas)",
        "Davlat boji va pochta xarajatlari to'langanligini tasdiqlovchi kvitansiya / to'lov topshiriqnomasi",
        "Da'vogarning shaxsini tasdiqlovchi hujjat yoki davlat ro'yxatidan o'tganlik guvohnomasi nusxasi",
        "Da'vo talablarini asoslovchi barcha yozma va elektron dalillar",
        "Vakilning ishonchnomasi va advokat orderi (agar ariza advokat orqali berilsa)"
    ]
}


def find_matching_template(query: str) -> Optional[Dict[str, Any]]:
    """
    Qidiruv so'ziga ko'ra mos rasmiy sud shablonini topadi.
    """
    q = query.lower()
    for cat_id, data in CIVIL_CLAIM_CATEGORIES.items():
        if any(w in q for w in cat_id.split("_")) or any(w in q for w in data["title"].lower().split() if len(w) > 4):
            res = dict(data)
            res["jurisdiction"] = "civil"
            res["template_key"] = cat_id
            return res

    for cat_id, data in ECONOMIC_CLAIM_CATEGORIES.items():
        if any(w in q for w in cat_id.split("_")) or any(w in q for w in data["title"].lower().split() if len(w) > 4):
            res = dict(data)
            res["jurisdiction"] = "economic"
            res["template_key"] = cat_id
            return res

    return None


def get_all_templates_summary() -> List[Dict[str, str]]:
    """
    Barcha my.sud.uz va template.sud.uz rasmiy andozalari ro'yxatini qaytaradi.
    """
    items = []
    for k, v in CIVIL_CLAIM_CATEGORIES.items():
        items.append({
            "key": k,
            "type": "Fuqarolik (my.sud.uz)",
            "court": v["court_type"],
            "title": v["title"],
            "law": ", ".join(v["substantive_law"])
        })
    for k, v in ECONOMIC_CLAIM_CATEGORIES.items():
        items.append({
            "key": k,
            "type": "Iqtisodiy (template.sud.uz)",
            "court": v["court_type"],
            "title": v["title"],
            "law": ", ".join(v["substantive_law"])
        })
    return items
