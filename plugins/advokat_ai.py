"""
Advokat AI — O'zbekiston Respublikasi qonunchiligi bo'yicha professional yuridik yordamchi.

Exports bazasidagi 8,186 ta amaliyotchi advokat taktikasi, 11 ta huquqiy soha
va 6,000+ ta qonun moddalari (FK, JK, MK, OK, MJtK, FPK, JPK) asosida ishlaydi.
Barcha huquqiy choralarni, moddalarni va qadam-baqadam tavsiyalarni
to'liq va batafsil ovozli tarzda tushuntirib beradi.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from core.advokat_kb import search_legal_knowledge
from core import gemini

PLUGIN = {
    "name": "advokat_ai",
    "description": (
        "O'zbekiston Respublikasi qonunchiligi bo'yicha yuridik maslahat berish, "
        "shartnomalar, nizolar, sud ishlari, aliment, meros, moddalar, jarimalar, "
        "huquqbuzarliklar va advokatlik taktikasi bo'yicha aniq qadam-baqadam yechim beradi. "
        "Foydalanuvchiga to'liq huquqiy ma'lumotni ovozli tarzda batafsil tushuntirib beradi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "savol": {
                "type": "STRING",
                "description": "Foydalanuvchining yuridik muammosi, savoli yoki qonun moddasi"
            },
            "soha": {
                "type": "STRING",
                "description": "Huquq sohasi (mehnat, fuqarolik, oila, jinoyat, soliq, iqtisodiy va h.k.)"
            }
        },
        "required": ["savol"]
    }
}


def _clean_for_speech(raw_text: str) -> str:
    """
    Markdown va maxsus belgilarni tozalab, ovozli sintez (TTS) uchun
    ravon va tushunarli matn shakliga keltiradi.
    """
    text = raw_text

    # Sarlavhalarni tozalash (###, ####)
    text = re.sub(r'#+\s*', '', text)

    # Markdown formatlash belgilarini tozalash (**qalin**, *kursiv*)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Ro'yxat belgilari (•, -, *)
    text = re.sub(r'^[•\-\*]\s*', '— ', text, flags=re.MULTILINE)

    # Barcha Unicode emojilarni va maxsus simvollarni tozalash (TTS nutq buzilmasligi uchun)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[\u2000-\u2bff]', '', text)
    # Ortiqcha bo'sh qatorlarni ixchamlashtirish
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n\n".join(lines)


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    Yuridik so'rovni qabul qilib, bazadan eng aniq amaliyotchi advokat xulosasini topadi
    va foydalanuvchiga OVOZLI tarzda to'liq ma'lumot beradi.
    """
    savol = parameters.get("savol", "").strip()
    if not savol:
        return "Iltimos, qanday huquqiy masala bo'yicha maslahat kerakligini ayting."

    try:
        # 1. Gibrid bilimlar bazasidan (Qonun moddalari + 8,186 ta amaliy keys) qidirish
        from core.advokat_kb import search_hybrid_legal
        hybrid_res = search_hybrid_legal(savol, statute_limit=1, precedent_limit=1)

        statutes = hybrid_res.get("statutes", [])
        precedents = hybrid_res.get("precedents", [])

        if statutes or precedents:
            response_parts = []

            # 1. Rasmiy qonun moddasi yoki plenum qarori (agar topilsa)
            if statutes:
                st = statutes[0]
                response_parts.append(
                    f"### ⚖️ Rasmiy Qonun Normasi: {st['code_name']}ning {st['article_no']} ({st['title']})\n\n"
                    f"{st['content']}"
                )

            # 2. Amaliyotchi advokatning sud taktikasi va qadam-baqadam yechimi
            if precedents:
                pr = precedents[0]
                response_parts.append(pr["response"])

            advokat_maslahati = "\n\n---\n\n".join(response_parts)

            # Ekrandagi Content Panelga chiqarish
            if player:
                try:
                    player.show_content(
                        title="⚖️ ADVOKAT AI — QONUN VA HUQUQIY YECHIM",
                        text=advokat_maslahati
                    )
                except Exception:
                    pass

                try:
                    player.write_log(f"ADVOKAT AI: '{savol}' bo'yicha qonun moddasi va amaliy taktika topildi.")
                except Exception:
                    pass

            spoken_text = _clean_for_speech(advokat_maslahati)
            return spoken_text

        else:
            # Agar bazada to'g'ridan-to'g'ri topilmasa, Gemini orqali batafsil advokat maslahati
            fallback_prompt = (
                f"Sen — O'zbekiston Respublikasi qonunchiligi bo'yicha mustaqil va tajribali amaliyotchi advokatsan. "
                f"Fuqaroning savoliga amaldagi qonun normalari (FK, JK, MK, OK, MJtK, JPK, FPK) asosida "
                f"aniq, amaliy, qadam-baqadam va to'liq professional huquqiy maslahat ber. "
                f"Qisqartirmasdan, qonun moddalarini va murojaat qilish organini to'liq ko'rsat.\n\n"
                f"Savol: {savol}"
            )
            advokat_javobi = gemini.text(fallback_prompt, tier=gemini.SMART, timeout_ms=25000)

            if player:
                try:
                    player.show_content(
                        title="⚖️ ADVOKAT AI — HUQUQIY MASLAHAT",
                        text=advokat_javobi
                    )
                except Exception:
                    pass

            spoken_text = _clean_for_speech(advokat_javobi)
            return spoken_text

    except Exception as e:
        return f"Hurmatli fuqaro, huquqiy bazadan ma'lumot olishda xatolik yuz berdi: {e}"
