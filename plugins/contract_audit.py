"""
plugins/contract_audit.py — Shartnomalarning Yuridik Auditi va Xavf Tahlili (Legal Due Diligence).

O'zbekiston Respublikasi Fuqarolik kodeksi, Mehnat kodeksi va "Xo'jalik yurituvchi subyektlar
faoliyatining shartnomaviy-huquqiy bazasi to'g'risida"gi Qonun asosida har qanday shartnoma
(ijara, mehnat, oldi-sotdi, pudrat, xizmat ko'rsatish, kredit, dasturiy ta'minot) loyihasini
chuqur tahlil qiladi. Bir tomonlama asossiz jarimalar, noqonuniy bekor qilish shartlari,
fors-major kamchiliklari va sudlov tuzoqlarini aniqlaydi hamda rasmiy
"YURIDIK EKSPERTIZA XULOSASI" (LEGAL OPINION) Microsoft Word (.docx) faylini tayyorlaydi.
"""

from __future__ import annotations
import datetime
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from core import gemini
from core import advokat_kb

import sys
REPORTS_DIR = (Path(sys.executable).parent / "reports") if getattr(sys, "frozen", False) else (Path(__file__).resolve().parent.parent / "reports")

PLUGIN = {
    "name": "contract_audit",
    "description": (
        "Shartnomalarni chuqur yuridik audit qilish va xavflarni aniqlash (Legal Due Diligence). "
        "Foydalanuvchi taqdim etgan shartnoma matni yoki fayli (.docx, .txt, .md) bo'yicha "
        "bir tomonlama asossiz jarimalar, noqonuniy moddalar (FK 326, 327, 382, 151), sudlov va "
        "bekor qilish tuzoqlarini Qizil (yuqori xavfli) va Sariq (ehtiyotkorlik) darajalarda aniqlaydi. "
        "Xavfli bandlarning tuzatilgan xavfsiz tahririni taklif etadi hamda rasmiy "
        "'YURIDIK EKSPERTIZA XULOSASI (LEGAL OPINION)' Microsoft Word (.docx) va matn (.md) hisobotini "
        "tayyorlab, kompyuterda Word dasturida avtomatik ochadi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "matn_yoki_fayl": {
                "type": "STRING",
                "description": (
                    "Tekshirilishi kerak bo'lgan shartnoma matni, bandlari yoki kompyuterdagi "
                    "hujjat fayli yo'li (.docx, .txt, .md)."
                )
            },
            "shartnoma_turi": {
                "type": "STRING",
                "description": (
                    "Shartnoma turi: 'ijara', 'mehnat', 'oldi_sotdi', 'pudrat', "
                    "'xizmat_korsatish', 'qarz', 'kredit', 'it_dasturiy', yoki 'umumiy'"
                )
            },
            "himoya_qilinuvchi_taraf": {
                "type": "STRING",
                "description": (
                    "Kimning manfaatini himoya qilish kerak: 'ijarachi', 'ijaraga_beruvchi', "
                    "'buyurtmachi', 'ijrochi', 'xodim', 'ish_beruvchi', 'xaridor', 'sotuvchi' va h.k."
                )
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Word (.docx) hisobotini avtomatik ochish (sukut bo'yicha true)."
            }
        },
        "required": ["matn_yoki_fayl"]
    }
}


def _extract_text_from_file_or_raw(input_data: str) -> str:
    """Matn yoki fayl yo'lidan shartnoma matnini ajratib oladi."""
    raw_str = input_data.strip()
    # Ehtimoliy fayl yo'li
    clean_path = raw_str.strip('"').strip("'")
    p = Path(clean_path)
    if p.exists() and p.is_file():
        suffix = p.suffix.lower()
        if suffix == ".docx":
            try:
                doc = docx.Document(str(p))
                full_text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        full_text.append(para.text)
                for table in doc.tables:
                    for row in table.rows:
                        row_text = [c.text.strip() for c in row.cells if c.text.strip()]
                        if row_text:
                            full_text.append(" | ".join(row_text))
                return "\n".join(full_text)
            except Exception:
                pass
        elif suffix in (".txt", ".md", ".json"):
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                try:
                    return p.read_text(encoding="cp1251")
                except Exception:
                    pass

    return raw_str


def _set_cell_background(cell, fill_hex: str):
    """Word jadval katakchasiga fon rangi berish."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)


def build_legal_opinion_docx(
    shartnoma_turi: str,
    himoya_taraf: str,
    opinion_matni: str,
    docx_path: Path
) -> Path:
    """
    Advokatlik andozalariga mos, professional «YURIDIK EKSPERTIZA XULOSASI» (.docx)
    hujjatini yaratadi.
    """
    doc = docx.Document()

    # Hoshiyalar (Advokatlik standarti: chap 3.0 sm, o'ng 1.5 sm, yuqori 2.0 sm, past 2.0 sm)
    for s in doc.sections:
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(3.0)
        s.right_margin = Cm(1.5)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(15, 23, 42)

    # 1. Tashkiliy ustxat (Header)
    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_org.paragraph_format.space_after = Pt(2)
    run_org = p_org.add_run("ADVOKAT AI — YURIDIK EKSPERTIZA VA AUDIT MARKAZI\nO'zbekiston Respublikasi Qonunchiligi Tahlili")
    run_org.bold = True
    run_org.font.size = Pt(11)
    run_org.font.color.rgb = RGBColor(71, 85, 105)

    # Chiziq
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(10)
    p_line.add_run("─" * 45).font.color.rgb = RGBColor(203, 213, 225)

    # 2. Sarlavha
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("SHARTNOMANING YURIDIK EKSPERTIZA XULOSASI\n(LEGAL OPINION)")
    run_title.bold = True
    run_title.font.size = Pt(15)
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # 3. Metama'lumotlar bloki
    bugun = datetime.date.today().strftime("%d.%m.%Y")
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_meta.paragraph_format.space_before = Pt(8)
    p_meta.paragraph_format.space_after = Pt(12)
    p_meta.paragraph_format.line_spacing = 1.15
    p_meta.add_run(f"• Ekspertiza sanasi: ").bold = True
    p_meta.add_run(f"{bugun}\n")
    p_meta.add_run(f"• Shartnoma toifasi: ").bold = True
    p_meta.add_run(f"{shartnoma_turi.upper()}\n")
    p_meta.add_run(f"• Himoya qilinayotgan taraf manfaati: ").bold = True
    p_meta.add_run(f"{himoya_taraf.upper()}\n")
    p_meta.add_run(f"• Qo'llanilgan huquqiy asos: ").bold = True
    p_meta.add_run("O'zbekiston Respublikasi Fuqarolik kodeksi, Mehnat kodeksi, Shartnomaviy-huquqiy baza to'g'risidagi Qonun")

    # 4. Asosiy mazmunni formatlash
    lines = opinion_matni.strip().split("\n")
    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        clean = re.sub(r"^#+\s*", "", raw).strip()
        clean = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean).strip()

        # Bo'lim sarlavhalari (Qizil xavflar, Sariq xavflar, Tavsiyalar)
        if any(clean.upper().startswith(kw) for kw in (
            "QIZIL XAVF", "SARIQ XAVF", "YASHIL", "TUZATILGAN TAHRIR", "YAKUNIY XULOSA",
            "1. QIZIL", "2. SARIQ", "3. YASHIL", "4. TUZATILGAN", "5. YAKUNIY", "XULOSA"
        )) or (clean.isupper() and len(clean) < 40 and clean.endswith(":")):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean)
            run.bold = True
            run.font.size = Pt(13)
            if "QIZIL" in clean.upper():
                run.font.color.rgb = RGBColor(185, 28, 28)  # Qizil rang
            elif "SARIQ" in clean.upper():
                run.font.color.rgb = RGBColor(180, 83, 9)   # Sariq/Oltin rang
            elif "YASHIL" in clean.upper():
                run.font.color.rgb = RGBColor(21, 128, 61)  # Yashil rang
            else:
                run.font.color.rgb = RGBColor(30, 41, 59)
            continue

        # Raqamlangan yoki markerli bandlar
        if re.match(r"^(\d+[\.\)]|[-•*])\s+", clean):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean)
            if any(w in clean.upper() for w in ("XATAR:", "XAVF:", "DIQQAT:", "MODDA:", "TAVSIYA:")):
                # Ajratilgan qismlar
                pass
            continue

        # Oddiy matn
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(clean)

    # 5. Yakuniy Advokatlik Imzosi va Muhr o'rni
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(20)
    p_sig.paragraph_format.first_line_indent = Cm(0)
    run_sig = p_sig.add_run(
        "Bosh advokat-konsultant:  ___________________ (ADVOKAT AI)\n"
        f"Xulosa berilgan sana:     {bugun}\n"
        "M.O'. (Yuridik xizmat muhri)"
    )
    run_sig.bold = True
    run_sig.font.size = Pt(11)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    return docx_path


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    Shartnomani chuqur yuridik audit qiladi, xulosani Word (.docx) va matn (.md)
    qilib tayyorlaydi.
    """
    raw_input = parameters.get("matn_yoki_fayl", "").strip()
    shartnoma_turi = parameters.get("shartnoma_turi", "umumiy").strip().lower()
    himoya_taraf = parameters.get("himoya_qilinuvchi_taraf", "mijoz").strip().lower()
    ochish = parameters.get("ochish", True)

    if not raw_input:
        return "Iltimos, tekshirilishi kerak bo'lgan shartnoma matnini yoki fayl yo'lini kiriting."

    try:
        if player:
            try:
                player.write_log("LEGAL DUE DILIGENCE: Shartnoma matni ajratib olinmoqda...")
            except Exception:
                pass

        # 1. Matnni olish
        shartnoma_matni = _extract_text_from_file_or_raw(raw_input)
        if len(shartnoma_matni) < 40:
            return "Kiritilgan shartnoma matni juda qisqa yoki bo'sh. Iltimos, to'liq shartnoma bandlarini taqdim eting."

        if player:
            try:
                player.write_log(f"LEGAL DUE DILIGENCE: O'zbekiston Fuqarolik kodeksi bo'yicha risk tahlili boshlandi...")
            except Exception:
                pass

        # 2. Qonunchilik bazasidan mezonlar olish
        kb_articles = advokat_kb.search_statutes(f"shartnoma jarima penya bekor qilish {shartnoma_turi}", limit=4)
        statutes_context = ""
        if kb_articles:
            statutes_context = "\nO'ZBEKISTON QONUNCHILIGI MODDALARI (AUDIT MEZONLARI):\n"
            for a in kb_articles:
                statutes_context += f"• {a['code_name']} {a['article_no']} ({a['title']}):\n  {a['content'][:300]}...\n\n"

        # 3. Gemini orqali professional Legal Due Diligence tahlilini amalga oshirish
        bugun = datetime.date.today().strftime("%d.%m.%Y")
        prompt = (
            f"Sen — O'zbekiston Respublikasining Shartnomaviy huquq va Korporativ amaliyot "
            f"bo'yicha bosh advokati va yuridik auditorisan.\n\n"
            f"VAZIFA: Quyida keltirilgan shartnoma loyihasini O'zbekiston Respublikasi qonunlari "
            f"(Fuqarolik kodeksi, Mehnat kodeksi, 'Xo'jalik yurituvchi subyektlar faoliyatining "
            f"shartnomaviy-huquqiy bazasi to'g'risida'gi Qonun) asosida qat'iy va chuqur "
            f"YURIDIK EKSPERTIZADAN (LEGAL DUE DILIGENCE) o'tkaz.\n\n"
            f"HIMOYA QILINAYOTGAN TARAFI: {himoya_taraf.upper()}\n"
            f"SHARTNOMA TOIFASI: {shartnoma_turi.upper()}\n"
            f"SANA: {bugun}\n\n"
            f"{statutes_context}\n"
            f"TEKSHIRILADIGAN SHARTNOMA MATNI:\n"
            f"```\n{shartnoma_matni[:12000]}\n```\n\n"
            f"EKSPERTIZA XULOSASI TUZILISHI (QAT'IY QOIDALAR):\n"
            f"1. KIRISH VA UMUMIY BAHO:\n"
            f"   - Shartnomaning huquqiy xarakteri va taraflar o'rtasidagi muvozanat holati (tengmi yoki bir taraf kamsitilganmi).\n\n"
            f"2. 🔴 QIZIL XAVFLAR (JIDDIY VA XATARLI BANDLAR):\n"
            f"   - Imzolamaslik yoki zudlik bilan olib tashlash shart bo'lgan bandlar (asossiz yuqori penya/jarima, 50% lik qonuniy cheklov buzilgani, bir tomonlama jarimasiz bekor qilish huquqi, sudga murojaat qilishni cheklash, asossiz moddiy javobgarlik);\n"
            f"   - Har bir xavf uchun: Shartnoma bandi matni, Qaysi qonun moddasiga zidligi (masalan: FK 326, 327, 382, 151-moddalar), Nega xavfliligi.\n\n"
            f"3. 🟡 SARIQ XAVFLAR (EHTIYOTKORLIK TALAB ETILADIGAN BANDLAR):\n"
            f"   - Fors-major bandining chala yozilgani (SSP guvohnomasi talabi yo'qligi), qabul qilish-topshirish dalolatnomasi muddatlari noaniqligi, to'lov muddati o'tishidagi nomutanosiblik.\n\n"
            f"4. 🟢 YASHIL QISMLAR (XAVFSIZ VA STANDART SHARTLAR):\n"
            f"   - Qonunga to'liq muvofiq, imzolash xavfsiz bo'lgan me'yorlar.\n\n"
            f"5. ✍️ TUZATILGAN XAVFSIZ TAHRIR (QARSHI TAKLIF / PROTOKOL RAZNOGLASIY):\n"
            f"   - Aniqlangan xavfli bandlar o'rniga {himoya_taraf.upper()} manfaatini 100% himoya qiluvchi tayyor shartnoma bandlari matni (to'g'ridan-to'g'ri ko'chirib olish uchun).\n\n"
            f"6. YAKUNIY ADVOKATLIK TAVSIYASI:\n"
            f"   - Xulosa: Shartnomani amaldagi ko'rinishda imzolash mumkinmi, yo'qmi yoki qaysi bandlar tuzatilgandan so'ng imzolash kerakligi bo'yicha qat'iy xulosa.\n\n"
            f"Matnni o'zbek adabiy va professional yuridik tilida, lo'nda, faktlarga asoslangan va ta'sirchan yoz."
        )

        opinion_matni = gemini.text(prompt, tier=gemini.SMART, timeout_ms=60000)

        # 4. Fayllarni saqlash
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_type = "".join(c for c in shartnoma_turi if c.isalnum() or c in ("_", "-")) or "shartnoma"
        docx_filename = f"legal_opinion_{safe_type}_{stamp}.docx"
        md_filename = f"legal_opinion_{safe_type}_{stamp}.md"

        docx_path = REPORTS_DIR / docx_filename
        md_path = REPORTS_DIR / md_filename

        md_path.write_text(opinion_matni, encoding="utf-8")
        build_legal_opinion_docx(shartnoma_turi, himoya_taraf, opinion_matni, docx_path)

        # 5. Word dasturida avtomatik ochish
        if ochish and os.name == "nt":
            try:
                os.startfile(str(docx_path))
                if player:
                    try:
                        player.write_log(f"DOCX: '{docx_filename}' Word dasturida ochildi.")
                    except Exception:
                        pass
            except Exception:
                try:
                    subprocess.Popen(["cmd", "/c", "start", "", str(docx_path)], shell=True)
                except Exception:
                    pass

        # 6. Ekranga chiqarish
        if player:
            try:
                player.show_content(
                    title=f"⚖️ YURIDIK EKSPERTIZA XULOSASI (.DOCX)",
                    text=opinion_matni
                )
            except Exception:
                pass

        return (
            f"Shartnoma bo'yicha O'zbekiston Respublikasi qonunchiligi asosida chuqur yuridik audit "
            f"(Legal Due Diligence) o'tkazildi. Aniqlangan qizil va sariq xavflar, qonun moddalari "
            f"hamda tavsiya etiladigan xavfsiz tahrirlar rasmiy 'YURIDIK EKSPERTIZA XULOSASI (LEGAL OPINION)' "
            f"shaklida Microsoft Word (.docx) formatida 'reports/{docx_filename}' fayliga saqlandi "
            f"va Word dasturida ochildi."
        )

    except Exception as e:
        return f"Shartnomani yuridik audit qilishda xatolik yuz berdi: {e}"


def execute(matn_yoki_fayl: str, shartnoma_turi: str = "umumiy", himoya_qilinuvchi_taraf: str = "mijoz", ochish: bool = True) -> str:
    """Yordamchi/to'g'ridan-to'g'ri chaqirish interfeysi."""
    return run({
        "matn_yoki_fayl": matn_yoki_fayl,
        "shartnoma_turi": shartnoma_turi,
        "himoya_qilinuvchi_taraf": himoya_qilinuvchi_taraf,
        "ochish": ochish
    })


if __name__ == "__main__":
    sample_clause = (
        "5.1. Agar ijrochi xizmatlarni kechiktirsa, buyurtmachiga kechiktirilgan har bir kun uchun "
        "shartnoma umumiy summasining 5% miqdorida penya to'laydi. "
        "5.2. Buyurtmachi shartnomani istalgan vaqtda hech qanday sababsiz va to'lovsiz bir tomonlama bekor qilish huquqiga ega. "
        "5.3. Taraflar o'rtasidagi har qanday nizo bo'yicha sudga murojaat qilish taqiqlanadi."
    )
    res = execute(sample_clause, shartnoma_turi="xizmat_korsatish", himoya_qilinuvchi_taraf="ijrochi", ochish=False)
    print("Natija:")
    print(res)
