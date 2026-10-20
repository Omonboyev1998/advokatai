"""
core/moot_court.py — Sud Majlisi Simulyatori va Sudga Tayyorgarlik Trenajyori (Moot Court).

Mijoz yoki advokatni sud majlisiga tayyorlaydi: Sudya, Qarshi taraf advokati
yoki Prokuror rolida real sud savollarini beradi, javoblardagi xatolarni
ko'rsatib coaching beradi hamda yakunda rasmiy Word (.docx) sud nutqi va
savol-javoblar protokolini shakllantiradi.
"""

from __future__ import annotations
import datetime
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core import gemini
from core import advokat_kb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "memory" / "moot_court_session.json"
REPORTS_DIR = PROJECT_ROOT / "reports"


def get_current_session() -> Dict[str, Any]:
    """Joriy simulyatsiya sessiyasini yuklaydi."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "active": False,
        "role": "sudya",
        "topic": "",
        "user_role": "da'vogar",
        "history": [],
        "mistakes": [],
        "round_count": 0
    }


def save_session(session: Dict[str, Any]) -> None:
    """Sessiyani faylga saqlaydi."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_session() -> None:
    """Sessiyani tozalaydi."""
    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
        except Exception:
            pass


def build_hearing_prep_docx(session: Dict[str, Any], final_guide_text: str, docx_path: Path) -> Path:
    """
    Sud majlisida so'zlash taktikasi va savol-javoblar bo'yicha
    rasmiy Word (.docx) qo'llanmasini shakllantiradi.
    """
    doc = docx.Document()

    for s in doc.sections:
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(3.0)
        s.right_margin = Cm(1.5)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(15, 23, 42)

    # 1. Bosh Header
    p_hdr = doc.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.space_after = Pt(2)
    r = p_hdr.add_run("ADVOKAT AI — SUD AMALIYOTIGA TAYYORGARLIK VA SIMULYATSIYA MARKAZI")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(71, 85, 105)

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(8)
    p_line.add_run("─" * 45).font.color.rgb = RGBColor(203, 213, 225)

    # 2. Sarlavha
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(10)
    r_t = p_title.add_run("SUD MAJLISIDA SO'ZGA CHIQISH TAKTIKASI VA\nSAVOL-JAVOBLAR PROTOKOLI (MOOT COURT)")
    r_t.bold = True
    r_t.font.size = Pt(14)

    # Metama'lumot
    bugun = datetime.date.today().strftime("%d.%m.%Y")
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(12)
    p_meta.add_run(f"• Nizo mavzusi: ").bold = True
    p_meta.add_run(f"{session.get('topic', 'Yuridik nizo')}\n")
    p_meta.add_run(f"• Mijozning suddagi maqomi: ").bold = True
    p_meta.add_run(f"{session.get('user_role', 'Da’vogar').upper()}\n")
    p_meta.add_run(f"• O'tkazilgan simulyatsiya raundlari: ").bold = True
    p_meta.add_run(f"{session.get('round_count', 0)} ta savol-javob\n")
    p_meta.add_run(f"• Sana: ").bold = True
    p_meta.add_run(f"{bugun}")

    # Asosiy yo'riqnoma matni
    lines = final_guide_text.strip().split("\n")
    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        clean = re.sub(r"^#+\s*", "", raw).strip()
        clean = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean).strip()

        if any(clean.upper().startswith(kw) for kw in (
            "I.", "II.", "III.", "IV.", "1.", "2.", "3.",
            "SUD NUTQI", "KUTILAYOTGAN SAVOLLAR", "TAQIQLANGAN XATOLAR",
            "QONUNIY ASOSLAR", "XULOSA"
        )) and len(clean) < 60:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean)
            run.bold = True
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(30, 41, 59)
            continue

        if re.match(r"^(\d+[\.\)]|[-•*])\s+", clean):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.add_run(clean)
            continue

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(clean)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(24)
    p_sig.paragraph_format.first_line_indent = Cm(0)
    p_sig.add_run(
        "Bosh advokat / Trener:  ___________________ (ADVOKAT AI)\n"
        f"Sana:                  {bugun}\n"
        "M.O'."
    ).bold = True

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    return docx_path


def start_simulation(topic: str, role: str = "sudya", user_role: str = "da'vogar") -> str:
    """Yangi sud mashg'ulotini boshlash."""
    clean_role = role.lower()
    if "advokat" in clean_role or "raqib" in clean_role:
        ai_role = "raqib_advokat"
        role_title = "QARSHI TARAFI ADVOKATI"
    elif "prokuror" in clean_role:
        ai_role = "prokuror"
        role_title = "DAVLAT AYBLOVCHISI (PROKUROR)"
    else:
        ai_role = "sudya"
        role_title = "RAISLIK QILUVCHI SUDYA"

    session = {
        "active": True,
        "role": ai_role,
        "role_title": role_title,
        "topic": topic.strip() or "Fuqarolik nizosi",
        "user_role": user_role.strip() or "da'vogar",
        "history": [],
        "mistakes": [],
        "round_count": 0
    }

    # Dastlabki sud replikasi
    prompt = (
        f"Sen O'zbekiston Respublikasi sud zalidasan. Sening roling: {role_title}.\n"
        f"Mavzu: {session['topic']}.\n"
        f"Foydalanuvchining suddagi maqomi: {session['user_role'].upper()}.\n\n"
        f"VAZIFA:\n"
        f"1. Sud majlisini qat'iy protsessual tartibda rasman och (masalan: 'Sud majlisi ochiq deb e'lon qilinadi...').\n"
        f"2. {session['user_role'].upper()}ga dastlabki rasmiy, ammo jiddiy va sinovli sud savolini ber.\n"
        f"3. Savoldan so'ng alohida qilib:\n"
        f"   💡 [ADVOKAT TAVSIYASI]: Foydalanuvchiga ushbu savolga qanday ruhda va qaysi qonuniy me'yorlarga "
        f"tayangan holda javob berishi kerakligini qisqacha o'rgat (1-2 jumla)."
    )

    intro = gemini.text(prompt, tier=gemini.SMART, timeout_ms=30000)
    session["history"].append({"speaker": ai_role, "text": intro})
    save_session(session)

    return (
        f"⚖️ **SUD SIMULYATORI BOSHLANDI (MOOT COURT)**\n"
        f"• **Simulyator roli:** {role_title}\n"
        f"• **Sizning rolingiz:** {session['user_role'].upper()}\n"
        f"• **Mavzu:** {session['topic']}\n\n"
        f"----------------------------------------\n\n"
        f"{intro}\n\n"
        f"*(Javobingizni ayting yoki yozing. Mashg'ulotni yakunlash uchun: 'yakunlash' deb ayting)*"
    )


def process_turn(user_answer: str) -> str:
    """Foydalanuvchi javobini tahlil qilish va navbatdagi sud savolini berish."""
    session = get_current_session()
    if not session.get("active"):
        return start_simulation(topic=user_answer, role="sudya")

    session["round_count"] += 1
    session["history"].append({"speaker": "user", "text": user_answer})

    prompt = (
        f"Sen O'zbekiston Respublikasi sud zalidasan. Sening roling: {session.get('role_title', 'SUDYA')}.\n"
        f"Nizo mavzusi: {session.get('topic')}.\n"
        f"Foydalanuvchi sudda: {session.get('user_role', 'da’vogar').upper()}.\n\n"
        f"Foydalanuvchining hozirgina bergan javobi:\n"
        f"\"{user_answer}\"\n\n"
        f"VAZIFANG (IKKI QISMDA JAVOB BER):\n"
        f"1. SUDYA/RAQIBNING REAKSIYASI VA KEYINGI SAVOLI:\n"
        f"   - {session.get('role_title')} sifatida javobdagi zaiflikka e'tibor qaratib, navbatdagi qaltis va jiddiy savolni ber.\n\n"
        f"2. 💡 [ADVOKATLIK COACHING & TAHLIL]:\n"
        f"   - Mijozning javobidagi xatolar: hissiyotga berildimi, asossiz gapirdimi, moddani eslatmadimi?\n"
        f"   - To'g'ri va kuchli huquqiy javob andozasi: 'Sudda bunday deyish kerak edi: ...'\n"
    )

    reply = gemini.text(prompt, tier=gemini.SMART, timeout_ms=35000)
    session["history"].append({"speaker": session.get("role", "sudya"), "text": reply})
    save_session(session)

    return reply


def finish_simulation(ochish: bool = True) -> str:
    """Mashg'ulotni yakunlash va rasmiy Word (.docx) sud nutqi/protokolini tayyorlash."""
    session = get_current_session()
    if not session.get("active") or session.get("round_count", 0) == 0:
        reset_session()
        return "Faol sud mashg'uloti mavjud emas. Yangi mashg'ulotni boshlash uchun nizo mavzusini ayting."

    history_text = "\n".join([f"{h['speaker'].upper()}: {h['text']}" for h in session.get("history", [])])

    prompt = (
        f"Sen — O'zbekistonning Oliy toifali sud advokatisan.\n"
        f"Quyida sud simulyatsiyasi (Moot Court) davomida bo'lib o'tgan savol-javoblar keltirilgan:\n"
        f"Mavzu: {session.get('topic')}\n"
        f"Foydalanuvchi roli: {session.get('user_role')}\n\n"
        f"MULOQOT TARIXI:\n{history_text[:8000]}\n\n"
        f"VAZIFA: Ushbu mashg'ulot asosida mijoz uchun sud majlisida 100% yutib chiqishga yordam beruvchi "
        f"to'liq rasmiy 'SUD MAJLISIDA SO'ZGA CHIQISH TAKTIKASI VA QO'LLANMA' hujjatini tayyorla:\n\n"
        f"TUZILISHI:\n"
        f"I. SUDYA OLDIDA SO'ZLANADIGAN KIRISH NUTQI (Tayyor nutq matni — kirish, nizo sababi, qonun moddalari, talab);\n"
        f"II. SUDDA KUTILAYOTGAN ENG XAVFLI 5 TA SAVOL VA ULARGA BERILADIGAN IDEAL HUQUQIY JAVOBLAR;\n"
        f"III. MASHG'ULOT DAVOMIDA YO'L QO'YILGAN XATOLAR VA ULARNI BARTARAF ETISH;\n"
        f"IV. SUD ZALIDAGI ADVOKATLIK XULQ-ATVORI QOIDALARI (Taqiqlangan harakatlar va psixologik ustunlik);\n"
        f"V. QO'LLANILADIGAN MODDALAR VA MODDIY TALABLAR.\n"
    )

    guide_text = gemini.text(prompt, tier=gemini.SMART, timeout_ms=50000)

    # Word (.docx) hisobotini saqlash
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_name = f"sud_nutqi_taktika_{stamp}.docx"
    md_name = f"sud_nutqi_taktika_{stamp}.md"

    docx_path = REPORTS_DIR / docx_name
    md_path = REPORTS_DIR / md_name

    md_path.write_text(guide_text, encoding="utf-8")
    build_hearing_prep_docx(session, guide_text, docx_path)

    reset_session()

    if ochish and os.name == "nt":
        try:
            os.startfile(str(docx_path))
        except Exception:
            try:
                subprocess.Popen(["cmd", "/c", "start", "", str(docx_path)], shell=True)
            except Exception:
                pass

    return (
        f"🏁 **SUD MAJLISI MASHG'ULOTI MUVAFFAQIYATLI YAKUNLANDI!**\n\n"
        f"• **Mavzu:** {session.get('topic')}\n"
        f"• **O'tkazilgan raundlar:** {session.get('round_count', 0)} ta savol-javob\n"
        f"• **Saqlangan Word hujjati:** `reports/{docx_name}` (avtomatik ochildi)\n\n"
        f"--- TAYYOR SUD NUTQI VA TAKTIK QO'LLANMA ---\n\n"
        f"{guide_text}"
    )
