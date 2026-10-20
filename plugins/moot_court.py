"""
plugins/moot_court.py — Sud Majlisi Simulyatori va Sudga Tayyorgarlik Trenajyori (Moot Court).

Mijoz yoki yosh advokatni sud zalidagi real savol-javobga tayyorlaydi.
O'zini Sudya, Qarshi taraf advokati yoki Prokuror roliga qo'yib,
sud zalidagi qaltis va jiddiy savollarni beradi, xatolarni ko'rsatadi,
ideal javoblarni o'rgatadi hamda yakunda to'liq rasmiy Word (.docx)
sud nutqi va taktik qo'llanmasini tayyorlaydi.
"""

from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from core import moot_court

PLUGIN = {
    "name": "moot_court",
    "description": (
        "Sud majlisiga tayyorgarlik simulyatori va trenajyori (Moot Court Simulator). "
        "Foydalanuvchini sud zalidagi real savol-javoblarga tayyorlaydi. Sudya, Qarshi taraf "
        "advokati yoki Prokuror sifatida kutilmagan va jiddiy sud savollarini beradi, foydalanuvchi "
        "javobidagi huquqiy xatolar va hissiy kamchiliklarni ko'rsatib coaching beradi. "
        "Mashg'ulot yakunida sud oldida so'zlanadigan tayyor nutq, kutilayotgan savollar va qonuniy "
        "javoblar jamlangan rasmiy Word (.docx) qo'llanmasini shakllantirib, Word dasturida avtomatik ochadi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "amal": {
                "type": "STRING",
                "description": (
                    "Bajariladigan harakat: 'boshlash' (yangi sud simulyatsiyasini boshlash), "
                    "'javob_berish' (sudya/advokat savoliga navbatdagi javobni kiritish), "
                    "'yakunlash' (mashg'ulotni to'xtatish va rasmiy Word sud nutqi qo'llanmasini tayyorlash)."
                )
            },
            "mavzu": {
                "type": "STRING",
                "description": "Nizo yoki sud ishi mavzusi (masalan: 'aliment undirish', 'noqonuniy ishdan bo'shatish', 'qarz nizosi')"
            },
            "rol": {
                "type": "STRING",
                "description": "AI qaysi rolda savol bersin: 'sudya', 'raqib_advokat', 'prokuror' (sukut bo'yicha: 'sudya')"
            },
            "mijoz_roli": {
                "type": "STRING",
                "description": "Foydalanuvchining suddagi maqomi: 'da'vogar', 'javobgar', 'ayblanuvchi', 'guvoh'"
            },
            "foydalanuvchi_javobi": {
                "type": "STRING",
                "description": "Sudya yoki advokatning avvalgi savoliga foydalanuvchining bergan javobi"
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Word (.docx) qo'llanmasini avtomatik ochish (sukut bo'yicha true)"
            }
        },
        "required": ["amal"]
    }
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    Sud simulyatori bo'yicha qadam-baqadam boshqaruv.
    """
    amal = parameters.get("amal", "boshlash").strip().lower()
    mavzu = parameters.get("mavzu", "").strip()
    rol = parameters.get("rol", "sudya").strip()
    mijoz_roli = parameters.get("mijoz_roli", "da'vogar").strip()
    javob = parameters.get("foydalanuvchi_javobi", "").strip()
    ochish = parameters.get("ochish", True)

    try:
        # 1. BOSHLASH
        if amal in ("boshlash", "start", "mashgulot_boshlash"):
            if not mavzu and javob:
                mavzu = javob

            if player:
                try:
                    player.write_log(f"MOOT COURT: Sud simulyatori boshlanmoqda (Rol: {rol.upper()})...")
                except Exception:
                    pass

            result = moot_court.start_simulation(
                topic=mavzu or "Yuridik nizo",
                role=rol,
                user_role=mijoz_roli
            )

            if player:
                try:
                    player.show_content(f"⚖️ SUD ZALI SIMULYATORI ({rol.upper()})", result)
                except Exception:
                    pass

            return result

        # 2. NAVBATDAGI JAVOBNI TAHLIL QILISH
        elif amal in ("javob_berish", "turn", "davom"):
            if not javob:
                return "Iltimos, sudya yoki advokat savoliga javobingizni ayting."

            if player:
                try:
                    player.write_log("MOOT COURT: Javobingiz tahlil qilinmoqda...")
                except Exception:
                    pass

            result = moot_court.process_turn(javob)

            if player:
                try:
                    player.show_content("⚖️ SUD SO'ROVI VA ADVOKAT TAHLILI", result)
                except Exception:
                    pass

            return result

        # 3. YAKUNLASH VA WORD HUJJAT TAYYORLASH
        elif amal in ("yakunlash", "stop", "tugatish", "xulosa"):
            if player:
                try:
                    player.write_log("MOOT COURT: Mashg'ulot yakunlanmoqda va Word qo'llanmasi tuzilmoqda...")
                except Exception:
                    pass

            result = moot_court.finish_simulation(ochish=ochish)

            if player:
                try:
                    player.show_content("🏁 SUDGA TAYYORGARLIK PROTOKOLI", result)
                except Exception:
                    pass

            return result

        else:
            return f"Noma'lum amal: '{amal}'. Mavjud amallar: boshlash, javob_berish, yakunlash."

    except Exception as e:
        return f"Sud simulyatorida xatolik yuz berdi: {e}"


def execute(amal: str, mavzu: str = "", rol: str = "sudya", mijoz_roli: str = "da'vogar", foydalanuvchi_javobi: str = "", ochish: bool = True) -> str:
    """Yordamchi chaqirish interfeysi."""
    return run({
        "amal": amal,
        "mavzu": mavzu,
        "rol": rol,
        "mijoz_roli": mijoz_roli,
        "foydalanuvchi_javobi": foydalanuvchi_javobi,
        "ochish": ochish
    })
