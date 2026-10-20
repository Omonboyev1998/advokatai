"""
plugins/legal_ocr.py — Yuridik Skaner, Rasm va PDF Hujjatlarni Tanib Olish hamda Tahlil Qilish (Legal OCR & Document Digitizer).

Sud qarorlari, ajrimlar, tergov hujjatlari, dalolatnomalar, orderlar, tilxatlar va
shartnomalarning skaner yoki fotosuratlarini (JPG, PNG, PDF, TIFF) matnga aylantiradi,
yuridik rekvizitlarini ajratadi, protsessual muddatlarini tekshiradi va advokatlik
bahosini berib, rasmiy Word (.docx) formatida saqlaydi hamda ochadi.
"""

from __future__ import annotations
import datetime
import mimetypes
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from google.genai import types
from core import gemini
from core import advokat_kb

import sys
REPORTS_DIR = (Path(sys.executable).parent / "reports") if getattr(sys, "frozen", False) else (Path(__file__).resolve().parent.parent / "reports")

PLUGIN = {
    "name": "legal_ocr",
    "description": (
        "Yuridik skaner, fotosurat va PDF hujjatlarni (sud qarorlari, ajrimlar, protokollar, "
        "tilxatlar, shartnomalar, dalolatnomalar) tanib olish va chuqur huquqiy tahlil qilish (OCR & Legal Analysis). "
        "Fayl yo'li (.pdf, .jpg, .png, .webp, .docx) berilganda matnni xatosiz raqamlashtiradi, "
        "sud/organ rekvizitlarini, taraflarni va da'vo xulosasini ajratib oladi, qonuniyligini va "
        "shikoyat (apellyatsiya/kassatsiya) berish muddatlarini tekshiradi hamda rasmiy "
        "'HUJJATNING YURIDIK TAHLIL VA TRANSKRIPTSIYASI' Microsoft Word (.docx) hisobotini "
        "tayyorlab avtomatik ochadi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "fayl_yoli": {
                "type": "STRING",
                "description": (
                    "Tekshirilishi yoki o'qilishi kerak bo'lgan hujjat fayli yo'li "
                    "(masalan: PDF, JPG, PNG rasmi yoki DOCX hujjati)."
                )
            },
            "savol_yoki_vazifa": {
                "type": "STRING",
                "description": (
                    "Advokatga qo'yilayotgan maxsus vazifa: 'matnni raqamlashtir', "
                    "'sud qarorini tahlil qil va shikoyat muddatini ayt', 'ushbu tilxat qonuniymi' va h.k. "
                    "(agar ko'rsatilmasa to'liq tahlil va transkripsiya beriladi)."
                )
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Word (.docx) hisobotini avtomatik ochish (sukut bo'yicha true)."
            }
        },
        "required": ["fayl_yoli"]
    }
}


def _extract_local_pdf_text(pdf_path: Path) -> str:
    """PDF fayldan mahalliy kutubxonalar orqali matn ajratish."""
    text_parts = []
    # 1. pdfplumber sinovi
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages[:15]:  # Dastlabki 15 sahifa
                ptxt = page.extract_text()
                if ptxt and ptxt.strip():
                    text_parts.append(ptxt.strip())
        if text_parts:
            return "\n\n--- SAHIFA ---\n\n".join(text_parts)
    except Exception:
        pass

    # 2. pypdf sinovi
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        for page in reader.pages[:15]:
            ptxt = page.extract_text()
            if ptxt and ptxt.strip():
                text_parts.append(ptxt.strip())
        if text_parts:
            return "\n\n--- SAHIFA ---\n\n".join(text_parts)
    except Exception:
        pass

    return ""


def build_ocr_analysis_docx(
    fayl_nomi: str,
    hujjat_matni: str,
    docx_path: Path
) -> Path:
    """
    Raqamlashtirilgan hujjat va advokatlik ekspertizasi bo'yicha Word (.docx)
    faylini yaratadi.
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

    # 1. Bosh sarlavha
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_after = Pt(2)
    r_hdr = p_header.add_run("ADVOKAT AI — HUJJATLARNI RAQAMLASHTIRISH VA EKSPERTIZA MARKAZI")
    r_hdr.bold = True
    r_hdr.font.size = Pt(11)
    r_hdr.font.color.rgb = RGBColor(71, 85, 105)

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(8)
    p_line.add_run("─" * 45).font.color.rgb = RGBColor(203, 213, 225)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("HUJJATNING YURIDIK TAHLILI VA RAQAMLI MATNI")
    r_title.bold = True
    r_title.font.size = Pt(14)

    # Metama'lumot
    bugun = datetime.date.today().strftime("%d.%m.%Y")
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(12)
    p_meta.add_run(f"• Tahlil qilingan fayl: ").bold = True
    p_meta.add_run(f"{fayl_nomi}\n")
    p_meta.add_run(f"• Ekspertiza sanasi: ").bold = True
    p_meta.add_run(f"{bugun}")

    lines = hujjat_matni.strip().split("\n")
    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        clean = re.sub(r"^#+\s*", "", raw).strip()
        clean = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean).strip()

        # Bo'lim sarlavhalari
        if any(clean.upper().startswith(kw) for kw in (
            "I.", "II.", "III.", "IV.", "1.", "2.", "3.",
            "YURIDIK REKVIZITLAR", "ADVOKATLIK EKSPERTIZASI", "PROTSESTUAL MUDDATLAR",
            "HUJJATNING TO'LIQ MATNI", "XULOSA VA TAVSIYA"
        )) and len(clean) < 60:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean)
            run.bold = True
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(30, 41, 59)
            continue

        # Bandlar
        if re.match(r"^(\d+[\.\)]|[-•*])\s+", clean):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.add_run(clean)
            continue

        # Paragraf
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(clean)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(20)
    p_sig.paragraph_format.first_line_indent = Cm(0)
    p_sig.add_run(
        "Ekspert-advokat:  ___________________ (ADVOKAT AI)\n"
        f"Sana:             {bugun}\n"
        "M.O'."
    ).bold = True

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    return docx_path


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    Hujjatni o'qiydi (OCR/PDF/Image/DOCX), yuridik tahlil qiladi va Word fayliga saqlaydi.
    """
    fayl_raw = parameters.get("fayl_yoli", "").strip().strip('"').strip("'")
    savol = parameters.get("savol_yoki_vazifa", "Hujjatni to'liq raqamlashtir va huquqiy baho ber").strip()
    ochish = parameters.get("ochish", True)

    if not fayl_raw:
        return "Iltimos, o'rganilishi kerak bo'lgan hujjat fayli yo'lini ko'rsating."

    p = Path(fayl_raw)
    if not p.exists() or not p.is_file():
        return f"Xatolik: '{fayl_raw}' fayli kompyuterda topilmadi. Iltimos, to'g'ri fayl yo'lini kiriting."

    try:
        suffix = p.suffix.lower()
        if player:
            try:
                player.write_log(f"LEGAL OCR: '{p.name}' fayli tahlilga yuklanmoqda...")
            except Exception:
                pass

        # 1. Fayl turiga qarab kontentni tayyorlash
        contents_payload = []
        instructions = (
            f"Sen — O'zbekiston Respublikasining Yuridik Hujjatshunoslik va Sud Ekspertizasi "
            f"bo'yicha bosh advokatisan.\n\n"
            f"Foydalanuvchi quyidagi hujjat faylini taqdim etdi: '{p.name}'\n"
            f"VAZIFA VA SAVOL: {savol}\n\n"
            f"QUYIDAGI TARTIBDA TO'LIQ VA MUKAMMAL YURIDIK TAHLIL BER:\n\n"
            f"I. HUJJATNING ASOSIY YURIDIK REKVIZITLARI:\n"
            f"   - Hujjat turi (Sud hal qiluv qarori, ajrim, sud buyrug'i, tergov qarori, dalolatnoma, tilxat, shartnoma);\n"
            f"   - Chiqargan organ/sud nomi (masalan: Fuqarolik ishlari bo'yicha ... tumanlararo sudi);\n"
            f"   - Hujjat sanasi va ro'yxatga olish raqami;\n"
            f"   - Ishda ishtirok etuvchi taraflar (Da'vogar, Javobgar, Sudya, Prokuror, Kotib);\n"
            f"   - Nizo yoki masalaning qisqacha mohiyati.\n\n"
            f"II. SUD YOKI ORGANNING YAKUNIY QARORI (XULOSASI):\n"
            f"   - Hujjatda qanday qaror qabul qilingan (da'vo qanoatlantirilganmi, rad etilganmi, qancha summa undirilishi belgilangan);\n"
            f"   - Davlat boji va ijro masalasi.\n\n"
            f"III. PROTSESTUAL MUDDATLAR VA SHIKOYAT TARTIBI:\n"
            f"   - Ushbu hujjat qachon qonuniy kuchga kiradi?\n"
            f"   - Apellyatsiya yoki kassatsiya shikoyati berish muddati (FPK, IPK, MSK yoki JPK bo'yicha aniq modda va kunlar soni);\n"
            f"   - Shikoyat qaysi yuqori instansiya sudiga beriladi.\n\n"
            f"IV. ADVOKATLIK MASLAHATI VA KEYINGI HARAKATLAR:\n"
            f"   - Ushbu hujjat qonuniymi yoki bekor qilish uchun asoslar bormi?\n"
            f"   - Mijoz zudlik bilan qanday harakatlarni amalga oshirishi lozim (dalillar to'plash, shikoyat tayyorlash, ijroni to'xtatish);\n\n"
            f"V. HUJJATNING TO'LIQ RAQAMLASHTIRILGAN MATNI (TRANSKRIPSIYA):\n"
            f"   - Hujjatdagi barcha matnni imlo xatolarisiz to'liq va aniq keltir.\n"
        )

        # Matnli PDF yoki Word hujjati bo'lsa
        if suffix in (".txt", ".md"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            contents_payload = [instructions, f"HUJJAT MATNI:\n```\n{txt[:15000]}\n```"]

        elif suffix == ".docx":
            doc = docx.Document(str(p))
            paras = [para.text for para in doc.paragraphs if para.text.strip()]
            txt = "\n".join(paras)
            contents_payload = [instructions, f"HUJJAT MATNI:\n```\n{txt[:15000]}\n```"]

        elif suffix == ".pdf":
            local_txt = _extract_local_pdf_text(p)
            if local_txt and len(local_txt) > 200:
                # Mahalliy matn yetarli bo'lsa
                contents_payload = [instructions, f"PDF HUJJAT MATNI:\n```\n{local_txt[:15000]}\n```"]
            else:
                # Skaner qilingan PDF — multimodal part orqali uzatish
                pdf_bytes = p.read_bytes()
                pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
                contents_payload = [instructions, pdf_part]

        elif suffix in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            # Rasm fayli — multimodal OCR
            mime = mimetypes.guess_type(str(p))[0] or "image/jpeg"
            img_bytes = p.read_bytes()
            img_part = types.Part.from_bytes(data=img_bytes, mime_type=mime)
            contents_payload = [instructions, img_part]

        else:
            return f"Qo'llab-quvvatlanmaydigan fayl formati: '{suffix}'. Iltimos, PDF, Word yoki rasm (.jpg, .png) faylini taqdim eting."

        if player:
            try:
                player.write_log("LEGAL OCR: Gemini Vision hujjatni raqamlashtirmoqda...")
            except Exception:
                pass

        # 2. Gemini orqali tahlil qilish
        tahlil_matni = gemini.text(contents_payload, tier=gemini.SMART, timeout_ms=60000)

        # 3. Fayllarni saqlash
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_name = re.sub(r"[^\w]", "_", p.stem.lower())
        docx_filename = f"legal_ocr_{clean_name}_{stamp}.docx"
        md_filename = f"legal_ocr_{clean_name}_{stamp}.md"

        docx_path = REPORTS_DIR / docx_filename
        md_path = REPORTS_DIR / md_filename

        md_path.write_text(tahlil_matni, encoding="utf-8")
        build_ocr_analysis_docx(p.name, tahlil_matni, docx_path)

        # 4. Word dasturida ochish
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

        # 5. Ekranga chiqarish
        if player:
            try:
                player.show_content(
                    title=f"📑 {p.name.upper()} — HUJJAT TAHLILI",
                    text=tahlil_matni
                )
            except Exception:
                pass

        return (
            f"'{p.name}' hujjati muvaffaqiyatli tanib olindi (OCR) va O'zbekiston qonunchiligi asosida "
            f"to'liq yuridik ekspertizadan o'tkazildi. Hujjat rekvizitlari, qaror qismi, shikoyat berish "
            f"muddatlari hamda to'liq raqamlashtirilgan matni 'reports/{docx_filename}' Word fayliga "
            f"saqlandi va avtomatik ochildi."
        )

    except Exception as e:
        return f"Hujjatni tanib olish va tahlil qilishda xatolik yuz berdi: {e}"


def execute(fayl_yoli: str, savol_yoki_vazifa: str = "", ochish: bool = True) -> str:
    """Yordamchi/to'g'ridan-to'g'ri chaqirish interfeysi."""
    return run({
        "fayl_yoli": fayl_yoli,
        "savol_yoki_vazifa": savol_yoki_vazifa,
        "ochish": ochish
    })
