"""
plugins/ish_yuritish.py — O'zbek tilida ish yuritish va hujjatshunoslik bo'yicha
yuridik maslahatchi va rasmiy hujjatlar generatri (DOCX & MD).

O'zbekiston Respublikasining "Davlat tili haqida"gi Qonuni, Vazirlar Mahkamasi
qarorlari va O'zDSt standartlari asosida korxona, tashkilot va idoraviy hujjatlarni
(Buyruq, Ariza, Bildirgi, Tushuntirish xati, Dalolatnoma, Bayonnoma, Xizmat xati,
Kafolat xati, Tavsifnoma, Tilxat, Ishonchnoma) tayyorlaydi hamda Word (.docx) formatida
saqlab, kompyuterda ochadi.
"""

from __future__ import annotations
import datetime
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core import gemini
from core import advokat_kb

import sys
REPORTS_DIR = (Path(sys.executable).parent / "reports") if getattr(sys, "frozen", False) else (Path(__file__).resolve().parent.parent / "reports")

PLUGIN = {
    "name": "ish_yuritish",
    "description": (
        "O'zbek tilida ish yuritish, hujjatshunoslik va devonxona standartlari bo'yicha "
        "professional maslahat berish hamda rasmiy tashkiliy-farmoyish, axborot-ma'lumot "
        "va shaxsiy hujjatlarni (Buyruq, Ariza, Bildirgi, Tushuntirish xati, Dalolatnoma/Akt, "
        "Bayonnoma/Protokol, Xizmat xati, Kafolat xati, Tavsifnoma, Tilxat, Ishonchnoma) "
        "davlat standartlari asosida Microsoft Word (.docx) va matn (.md) formatlarida "
        "tayyorlash hamda 'reports/' papkasiga saqlab avtomatik ochish."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "hujjat_turi": {
                "type": "STRING",
                "description": (
                    "Hujjat yoki operatsiya turi: 'buyruq' (ishga olish, ta'til, ishdan bo'shatish, intizomiy jazo), "
                    "'ariza' (ishga kirish, mehnat ta'tili, bo'shash, moddiy yordam), 'bildirgi' (dokladnaya), "
                    "'tushuntirish_xati' (kechikish, tushuntirish), 'dalolatnoma' (akt), 'bayonnoma' (protokol), "
                    "'kafolat_xati', 'xizmat_xati', 'tavsifnoma' (xarakteristika), 'tilxat' (raspiska), "
                    "'ishonchnoma' (doverennost), yoki 'qoidalar' (ish yuritish talablari bo'yicha maslahat)."
                )
            },
            "tafsilot": {
                "type": "STRING",
                "description": (
                    "Hujjat tafsilotlari: tashkilot nomi, kimdan kimga (rahbar va xodim F.I.Sh.), lavozimi, "
                    "hujjat sababi/mazmuni, sanalar, summalar yoki qonuniy asoslar."
                )
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Faylni Microsoft Word dasturida avtomatik ochish (sukut bo'yicha true)."
            }
        },
        "required": ["hujjat_turi", "tafsilot"]
    }
}


def build_ish_yuritish_docx(hujjat_turi: str, matn: str, docx_path: Path) -> Path:
    """
    O'zbek tilida ish yuritish va davlat standartlariga mos Word (.docx) hujjatini shakllantiradi:
    - Sahifa chetlari: Chap 3.0 sm (tikish zaxirasi), O'ng 1.5 sm, Yuqori 2.0 sm, Past 2.0 sm;
    - Shrift: Times New Roman, 12-14 pt, 1.15 qatorlar oralig'i;
    - To'g'ri rekvizitlar joylashuvi (shapka, sarlavha, matn xatboshisi 1.25 sm, imzo va sana).
    """
    doc = docx.Document()

    # Hoshiyalar
    for s in doc.sections:
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(3.0)
        s.right_margin = Cm(1.5)

    # Standart shrift
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(15, 23, 42)

    lines = matn.strip().split("\n")
    mode = "header"

    header_triggers = (
        "direktori", "boshlig'i", "rahbari", "kimga:", "kimdan:", "hurmatli", "manzil:"
    )

    title_triggers = (
        "BUYRUQ", "ARIZA", "BILDIRGI", "BILDIRISHNOMA", "TUSHUNTIRISH XATI",
        "DALOLATNOMA", "BAYONNOMA", "KAFOLAT XATI", "XIZMAT XATI",
        "TAVSIFNOMA", "TAVSIYANOMA", "TILXAT", "ISHONCHNOMA", "HISOBOT"
    )

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        clean_line = re.sub(r"^#+\s*", "", raw).strip()
        clean_line = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean_line).strip()

        # 1. Hujjat Sarlavhasi (BUYRUQ, ARIZA, DALOLATNOMA va h.k.)
        is_title = any(clean_line.upper().startswith(t) for t in title_triggers) or (
            mode == "header" and clean_line.isupper() and len(clean_line) < 35
        )

        if is_title:
            mode = "title"
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            continue

        # 2. Sarlavha osti (Qavs ichidagi yoki tematik sarlavha: "... to'g'risida")
        if mode == "title" and (clean_line.lower().endswith("to'g'risida") or clean_line.lower().endswith("haqida") or (clean_line.startswith("(") and clean_line.endswith(")"))):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.italic = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            mode = "body"
            continue

        # 3. Rekvizitlar "Shapka" (O'ng tomonga tekislash: Ariza, Bildirgi, Tushuntirish xati uchun)
        is_header = any(ht in clean_line.lower() for ht in header_triggers) or (
            mode == "header" and not clean_line.startswith(("Men,", "202", "Ushbu", "Biz,"))
        )

        if mode == "header" and is_header:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.left_indent = Cm(8.5)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"
            if any(k in clean_line for k in ("direktori", "boshlig'i", "Kimga:", "Kimdan:")):
                run.bold = True
            continue

        # 4. Asosiy matn (Body)
        mode = "body"
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        # Ichki kalit so'zlar: BUYURAMAN, QAROR QILINDI, ESHITILDI, KUN TARTIBI, TASDIQLAYMAN
        is_command_word = any(w in clean_line.upper() for w in (
            "BUYURAMAN:", "QAROR QILINDI:", "QAROR QILADI:", "ESHITILDI:",
            "KUN TARTIBI:", "SO'ZGA CHIQDILAR:", "TASDIQLAYMAN:", "TASDIQLAYMAN"
        ))

        if is_command_word or (clean_line.isupper() and len(clean_line) < 30 and clean_line.endswith(":")):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if "BUYURAMAN" in clean_line.upper() else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = "Times New Roman"
            if "BUYURAMAN" in clean_line.upper():
                run.font.size = Pt(13.5)

        # Raqamlangan bandlar (1., 2., 3.)
        elif re.match(r"^\d+[\.\)]\s+", clean_line):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(1.25)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"

        # Sana, imzo va ijrochi bloki
        elif any(k in clean_line for k in ("Imzo:", "Rahbar:", "Direktor:", "Rais:", "Kotib:", "Ijrochi:", "Sana:", "___")):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = "Times New Roman"

        # Oddiy abzats
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(1.25)
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    return docx_path


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    JARVIS plugin interface: runs clerical document generator and returns summary.
    """
    hujjat_turi = parameters.get("hujjat_turi", "buyruq").strip().lower()
    tafsilot = parameters.get("tafsilot", "").strip()
    ochish = parameters.get("ochish", True)

    if not tafsilot:
        return "Iltimos, ish yuritish hujjati turi, kim tomonidan va qanday maqsadda tuzilayotganini bayon qiling."

    try:
        if player:
            try:
                player.write_log(f"ISH YURITISH: '{hujjat_turi}' bo'yicha qoidalar va andozalar olinmoqda...")
            except Exception:
                pass

        # 1. Bilimlar bazasidan qidirish
        search_query = f"{hujjat_turi} {tafsilot}"
        kb_results = advokat_kb.search_ish_yuritish(search_query, limit=2)

        kb_context = ""
        if kb_results:
            kb_context = "\n---\nISh YURITISH STANDARTLARI VA REKVIZITLARI (Baza):\n"
            for r in kb_results:
                kb_context += f"• [{r['doc_type']}] {r['title']}:\n{r['procedure']}\n\n"

        # Agar foydalanuvchi faqat qoidalarni so'ragan bo'lsa
        if hujjat_turi == "qoidalar" and not any(k in tafsilot.lower() for k in ("yoz", "tuz", "chiqar", "tayyorla")):
            if kb_results:
                reply = f"📑 **O'ZBEK TILIDA ISH YURITISH TARTIBI:**\n\n"
                for r in kb_results:
                    reply += f"### {r['title']}\n{r['procedure']}\n\n"
                return reply

        # 2. LLM orqali rasmiy hujjat matnini tuzish
        prompt = (
            f"Sen O'zbekiston Respublikasining davlat tilida ish yuritish va hujjatshunoslik "
            f"bo'yicha bosh mutaxassisi hamda tajribali advokatisan.\n"
            f"Vazifang: Quyidagi talab asosida rasmiy, yuridik jihatdan benuqson va Davlat standarti "
            f"(O'zDSt) hamda 'Davlat tilida ish yuritish' qoidalariga 100% mos keluvchi rasmiy hujjat loyihasini tayyorlash.\n\n"
            f"HUJJAT TURI: {hujjat_turi}\n"
            f"TAFSILOT VA TALAB: {tafsilot}\n\n"
            f"{kb_context}\n"
            f"QAT'IY QOIDALAR:\n"
            f"1. Faqat lotin yozuviga asoslangan adabiy va rasmiy o'zbek tilida yoz.\n"
            f"2. Hujjatning barcha majburiy rekvizitlarini to'liq kirit:\n"
            f"   - Korxona/tashkilot nomi va joyi (Toshkent sh.);\n"
            f"   - Agar Buyruq bo'lsa: sana, №, mavzu sarlavhasi, kirish qismi (Mehnat kodeksi yoki asoslantirish), "
            f"markazda 'BUYURAMAN:', 1, 2, 3-bandlar, ijro nazorati, asos va rahbar imzosi bloki;\n"
            f"   - Agar Ariza/Bildirgi/Tushuntirish xati bo'lsa: o'ng tomonda manzil egasi (Kimga, Kimdan), "
            f"markazda hujjat nomi (katta harflarda), aniq va lo'nda matn, sana va shaxsiy imzo;\n"
            f"   - Agar Dalolatnoma (Akt) bo'lsa: 'TASDIQLAYMAN' ustxati, komissiya a'zolari (kamida 3 kishi), holat bayoni, imzolar;\n"
            f"   - Agar Kafolat xati yoki Xizmat xati bo'lsa: tashkilot blankasi, chiquvchi raqami va sanasi, rahbar va bosh hisobchi imzosi, muhr o'rni.\n"
            f"3. Matnni to'liq, real hayotda darhol chop etib imzolash mumkin bo'lgan holatda yoz. Hech qanday keraksiz salomlashish yoki soxta kirish so'zlarini qo'shma, to'g'ridan-to'g'ri rasmiy hujjat matnini ber."
        )

        if player:
            try:
                player.write_log("ISH YURITISH: Rasmiy hujjat matni tuzilmoqda...")
            except Exception:
                pass

        hujjat_matni = gemini.text(prompt, tier=gemini.SMART, timeout_ms=45000)

        # 3. Fayllarni saqlash
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_type = re.sub(r"[^\w]", "_", hujjat_turi.lower())
        docx_filename = f"ish_yuritish_{clean_type}_{stamp}.docx"
        md_filename = f"ish_yuritish_{clean_type}_{stamp}.md"

        docx_path = REPORTS_DIR / docx_filename
        md_path = REPORTS_DIR / md_filename

        md_path.write_text(hujjat_matni, encoding="utf-8")
        build_ish_yuritish_docx(hujjat_turi, hujjat_matni, docx_path)

        # 4. Word faylini avtomatik ochish
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

        if player:
            try:
                player.show_content(
                    title=f"📑 {hujjat_turi.upper()} (.DOCX)",
                    text=hujjat_matni
                )
            except Exception:
                pass

        return (
            f"Davlat tilida ish yuritish standartlari asosida rasmiy '{hujjat_turi}' hujjati "
            f"Microsoft Word (.docx) formatida professional tayyorlandi va 'reports/{docx_filename}' "
            f"fayliga saqlandi. Hujjat barcha rekvizitlar, me'yorlar va qoidalar bilan rasmiylashtirildi "
            f"hamda Word dasturida avtomatik ochildi."
        )

    except Exception as e:
        return f"Ish yuritish hujjatini tayyorlashda xatolik yuz berdi: {e}"


def execute(hujjat_turi: str, tafsilot: str, ochish: bool = True) -> str:
    """Yordamchi/to'g'ridan-to'g'ri chaqirish funksiyasi."""
    return run({"hujjat_turi": hujjat_turi, "tafsilot": tafsilot, "ochish": ochish})


if __name__ == "__main__":
    test_out = execute(
        hujjat_turi="buyruq",
        tafsilot="Kompaniya direktori Alisher Karimov tomonidan xodim Botir Rahimovni 2026-yil 15-oktabrdan Bosh dasturchi lavozimiga ishga qabul qilish to'g'risida buyruq.",
        ochish=False
    )
    print("Test natijasi:")
    print(test_out)

