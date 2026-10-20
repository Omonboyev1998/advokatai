"""
Advokat AI — Lex.uz Rasmiy Qonunchilik Qidiruvi.

O'zbekiston Respublikasi qonunlari, kodekslari, Prezident farmon va qarorlari,
Vazirlar Mahkamasi qarorlarini rasmiy Lex.uz manbasidan qidirish va tahlil qilish.
"""

from __future__ import annotations
import urllib.parse
import requests
from bs4 import BeautifulSoup
from core import gemini

PLUGIN = {
    "name": "lexuz_search",
    "description": (
        "O'zbekiston Respublikasi qonun hujjatlarini (qonunlar, kodekslar, qarorlar, farmonlar) "
        "Lex.uz rasmiy milliy qonunchilik bazasidan qidirish va tasdiqlangan huquqiy normalarni topish. "
        "Aniq qonun matni, moddasi yoki yangi qabul qilingan qarorlar kerak bo'lganda foydalaning."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "mavzu": {
                "type": "STRING",
                "description": "Qidirilayotgan qonun nomi, modda yoki huquqiy mavzu (masalan: 'Mehnat kodeksi 161-modda', 'ijara shartnomasi qonuni')"
            }
        },
        "required": ["mavzu"]
    }
}


def _search_duckduckgo_lexuz(query: str) -> list[dict]:
    """DuckDuckGo orqali site:lex.uz natijalarini qidirish."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote('site:lex.uz ' + query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    results = []
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", class_="result__snippet")[:3]:
                text = a.get_text(strip=True)
                if text:
                    results.append({"snippet": text})
    except Exception:
        pass
    return results


def run(parameters: dict, player=None, session_memory=None) -> str:
    mavzu = parameters.get("mavzu", "").strip()
    if not mavzu:
        return "Qaysi qonun yoki modda bo'yicha qidiruv o'tkazish kerakligini ayting."

    try:
        if player:
            try:
                player.write_log(f"LEX.UZ QIDIRUV: '{mavzu}' bo'yicha rasmiy manbalar tekshirilmoqda...")
            except Exception:
                pass

        # 1. Lex.uz natijalarini qidirish
        web_results = _search_duckduckgo_lexuz(mavzu)
        context = "\n".join([r["snippet"] for r in web_results])

        # 2. Gemini orqali qonun normalarini tizimlashtirish
        prompt = (
            f"Sen — O'zbekiston Respublikasi qonunchiligi bo'yicha advokat yordamchisisan. "
            f"Foydalanuvchi Lex.uz dan quyidagi qonuniy masalani qidirmoqda: '{mavzu}'.\n"
            f"Topilgan rasmiy manbalar: {context}\n\n"
            f"Ushbu qonun hujjati, tegishli moddalar va uning amaliy ahamiyati haqida aniq, "
            f"rasmiy va tushunarli qilib to'liq xulosa ber. O'zbekiston qonunchiligiga asoslan."
        )

        xulosa = gemini.text(prompt, tier=gemini.SMART, timeout_ms=20000)

        if player:
            try:
                player.show_content(
                    title="📜 LEX.UZ — RASMIY QONUNCHILIK",
                    text=f"Mavzu: {mavzu}\n\n{xulosa}"
                )
            except Exception:
                pass

        # Ovozli javob uchun tozalash
        clean_speech = xulosa.replace("#", "").replace("*", "").replace("•", "-")
        return f"Lex.uz bazasi bo'yicha '{mavzu}' yuzasidan rasmiy qonun normalari aniqlandi. {clean_speech}"

    except Exception as e:
        return f"Lex.uz qonunchilik bazasidan qidirishda xatolik yuz berdi: {e}"
