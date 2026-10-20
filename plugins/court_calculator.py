"""
Advokat AI — Sud Davlat Boji va Protsessual Muddatlar Kalkulyatori.

O'zbekiston Respublikasi 'Davlat boji to'g'risida'gi Qonuni, Fuqarolik protsessual
va Iqtisodiy protsessual kodekslariga binoan sud harajatlari va muddatlarni hisoblaydi.
"""

from __future__ import annotations
import re

# Joriy Bazaviy hisoblash miqdori (BHM) — so'mda
CURRENT_BHM = 375_000

PLUGIN = {
    "name": "court_calculator",
    "description": (
        "Sudga da'vo arizasi kiritishda to'lanadigan davlat boji miqdorini aniq hisoblab beradi "
        "(mulkiy da'volar, nikohdan ajratish, nomulkiy nizolar, iqtisodiy va ma'muriy sudlar). "
        "Shuningdek qonuniy da'vo muddatlari va apellyatsiya shikoyati berish muddatlarini tushuntiradi. "
        "Foydalanuvchi sudga ariza berish xarajati yoki muddatlar haqida so'raganda ishlatiladi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "ariza_turi": {
                "type": "STRING",
                "description": "Da'vo turi: 'mulkiy' (qarz, zarar undirish), 'ajrashish', 'nomulkiy', 'mehnat', 'iqtisodiy', 'muddat'"
            },
            "summa": {
                "type": "NUMBER",
                "description": "Mulkiy da'volarda undirilishi talab qilinayotgan umumiy summa (so'mda)"
            }
        },
        "required": ["ariza_turi"]
    }
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    ariza_turi = str(parameters.get("ariza_turi") or parameters.get("davo_turi") or parameters.get("amal") or parameters.get("turi") or "").lower()
    summa = float(parameters.get("summa") or parameters.get("davo_bahosi") or parameters.get("amount") or 0)

    bhm_formatted = f"{CURRENT_BHM:,}".replace(",", " ")

    natija = []
    ogzaki = []

    if "ajrash" in ariza_turi or "nikoh" in ariza_turi:
        boj = CURRENT_BHM * 2
        boj_str = f"{boj:,}".replace(",", " ")
        natija.append(f"⚖️ NIKOHDAN AJRATISH BO'YICHA DAVLAT BOJI:")
        natija.append(f"• Stavka: 2 BHM (Bazaviy hisoblash miqdorining 2 baravari)")
        natija.append(f"• Joriy BHM: {bhm_formatted} so'm")
        natija.append(f"• To'lanadigan summa: {boj_str} so'm")
        natija.append(f"• Eslatma: Takroriy nikohdan ajratishda davlat boji 4 BHM ({CURRENT_BHM*4:,} so'm) bo'ladi.")
        ogzaki.append(f"Nikohdan ajratish da'vosi uchun davlat boji 2 BHM, ya'ni {boj_str} so'mni tashkil etadi.")

    elif "mehnat" in ariza_turi or "ish haqi" in ariza_turi:
        natija.append(f"⚖️ MEHNAT NIZOLARI VA ISH HAQI BO'YICHA:")
        natija.append(f"• Xodimlar mehnat munosabatlaridan kelib chiqadigan barcha talablar (ishga tiklash, ish haqi undirish) bo'yicha davlat bojidan TO'LIQ OZOD QILINGAN.")
        natija.append(f"• Da'vo muddati: Ishdan nohaq bo'shatilganda — buyruq nusxasi berilgan kundan boshlab 1 OY ichida sudga murojaat qilish shart!")
        ogzaki.append("Mehnat nizolari va ish haqini undirish bo'yicha da'vogar davlat bojidan qonunan to'liq ozod qilingan. Ammo ishga tiklash da'vosini 1 oy ichida kiritish shart.")

    elif "iqtisodiy" in ariza_turi or "biznes" in ariza_turi:
        foiz = 0.02
        hisoblangan = max(summa * foiz, float(CURRENT_BHM)) if summa > 0 else float(CURRENT_BHM)
        boj_str = f"{int(hisoblangan):,}".replace(",", " ")
        natija.append(f"⚖️ IQTISODIY SUDLAR UCHUN DAVLAT BOJI:")
        natija.append(f"• Mulkiy da'volarda: Da'vo bahosining 2 foizi (lekin kamida 1 BHM)")
        if summa > 0:
            summa_str = f"{int(summa):,}".replace(",", " ")
            natija.append(f"• Da'vo summasi: {summa_str} so'm")
            natija.append(f"• To'lanadigan davlat boji: {boj_str} so'm")
        else:
            natija.append(f"• Minimal davlat boji: 1 BHM ({bhm_formatted} so'm)")
        ogzaki.append(f"Iqtisodiy sudlar uchun davlat boji da'vo summasining 2 foizini tashkil etadi. Hisoblangan to'lov: {boj_str} so'm.")

    elif "muddat" in ariza_turi or "protsessual" in ariza_turi:
        natija.append(f"📅 ASOSIY QONUNIY PROTSESSUAL MUDDATLAR:")
        natija.append(f"• Umumiy da'vo muddati (FK 150-modda): 3 YIL;")
        natija.append(f"• Ishga tiklash bo'yicha da'vo muddati (MK): 1 OY;")
        natija.append(f"• Apellyatsiya shikoyati berish muddati: Sud hal qiluv qarori chiqqan kundan boshlab 1 OY ichida;")
        natija.append(f"• Sud buyrug'iga e'tiroz bildirish muddati: Qaror nusxasi olingan kundan 10 KUN ichida;")
        natija.append(f"• Ma'muriy bayonnomaga shikoyat: 10 KUN ichida.")
        ogzaki.append("Umumiy qonuniy da'vo muddati 3 yil, ammo mehnatda ishga tiklash muddati 1 oy, sud qaroridan apellyatsiya berish muddati esa 1 oyni tashkil qiladi.")

    else:
        # Umumiy fuqarolik mulkiy da'vosi (4%, kamida 1 BHM)
        foiz = 0.04
        if summa > 0:
            hisoblangan = max(summa * foiz, float(CURRENT_BHM))
            summa_str = f"{int(summa):,}".replace(",", " ")
            boj_str = f"{int(hisoblangan):,}".replace(",", " ")
            natija.append(f"⚖️ FUQAROLIK SUDI (MULKIY DA'VOLAR) DAVLAT BOJI:")
            natija.append(f"• Stavka: Da'vo bahosining 4 foizi (kamida 1 BHM)")
            natija.append(f"• Da'vo summasi: {summa_str} so'm")
            natija.append(f"• To'lanadigan davlat boji: {boj_str} so'm")
            ogzaki.append(f"Fuqarolik sudida {summa_str} so'mlik da'vo uchun 4 foiz, ya'ni {boj_str} so'm davlat boji to'lanadi.")
        else:
            natija.append(f"⚖️ FUQAROLIK SUDI DAVLAT BOJI:")
            natija.append(f"• Mulkiy da'volar: Da'vo summasining 4 foizi (kamida 1 BHM — {bhm_formatted} so'm)")
            natija.append(f"• Nomulkiy da'volar (masalan: shartnomani bekor qilish, huquqni tan olish): 2 BHM ({CURRENT_BHM*2:,} so'm)")
            ogzaki.append(f"Fuqarolik sudida mulkiy da'volar bo'yicha 4 foiz, nomulkiy nizolar uchun esa 2 BHM davlat boji belgilanadi.")

    full_text = "\n".join(natija)

    if player:
        try:
            player.show_content(
                title="💰 SUD DAVLAT BOJI VA MUDDATLAR",
                text=full_text
            )
        except Exception:
            pass

    return " ".join(ogzaki) + " Tafsilotlar va moddalar ekranda ham ko'rsatildi."
