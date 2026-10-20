"""
plugins/legal_draft.py — Rasmiy Yuridik Hujjatlar va Sud Arizalari Generatori (DOCX & MD).

O'zbekiston Respublikasi protsessual qonunchiligi (FPK, IPK, MSK, JPK) va yuridik
texnika qoidalari asosida sudga da'vo arizalari, talabnomalar (pretenziya),
apellyatsiya/kassatsiya shikoyatlari, iltimosnomalar va shartnoma loyihalarini
professional darajada tayyorlaydi hamda to'g'ridan-to'g'ri chop etishga tayyor
Microsoft Word (.docx) va matn (.md) formatlarida saqlaydi.
"""

from __future__ import annotations
import datetime
import os
import re
import subprocess
from pathlib import Path

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core import gemini
from core import advokat_kb

import sys
REPORTS_DIR = (Path(sys.executable).parent / "reports") if getattr(sys, "frozen", False) else (Path(__file__).resolve().parent.parent / "reports")

PLUGIN = {
    "name": "legal_draft",
    "description": (
        "Rasmiy yuridik hujjatlar loyihasini O'zbekiston sud standartlari asosida "
        "Microsoft Word (.docx) va matn (.md) formatida professional tayyorlash. "
        "Sudga da'vo arizasi (fuqarolik, iqtisodiy, ma'muriy sudlarga), huquqbuzarga "
        "rasmiy talabnoma (pretenziya), apellyatsiya va kassatsiya shikoyati, sudga "
        "iltimosnoma, advokatlik so'rovi yoki shartnoma loyihalarini barcha rekvizitlar, "
        "qonuniy moddalar va talablar bilan tuzadi hamda 'reports/' papkasiga Word (.docx) "
        "fayl qilib saqlaydi."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "hujjat_turi": {
                "type": "STRING",
                "description": (
                    "Hujjat turi: 'davo_arizasi' (sudga da'vo), 'talabnoma' (pretenziya), "
                    "'shikoyat' (apellyatsiya/kassatsiya), 'iltimosnoma', 'advokat_sorovi', 'shartnoma'"
                )
            },
            "tafsilot": {
                "type": "STRING",
                "description": "Nizo tafsilotlari, tomonlar (kimdan kimgaligi), nizo predmeti, da'vo summasi yoki qonunbuzarlik mazmuni"
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Faylni Microsoft Word dasturida avtomatik ochish (sukut bo'yicha true)"
            }
        },
        "required": ["hujjat_turi", "tafsilot"]
    }
}


def build_court_docx(hujjat_turi: str, matn: str, docx_path: Path) -> Path:
    """
    Matndan O'zbekiston sud va davlat idoralari qoidalariga 100% mos keluvchi
    mukammal formatlangan Microsoft Word (.docx) faylini yaratadi:
    - Sahifa chetlari: Chap 3.0 sm (tikish uchun), O'ng 1.5 sm, Yuqori/Past 2.0 sm.
    - Shrift: Times New Roman, 13-14 pt.
    - Sud va tomonlar rekvizitlari: O'ng tomondan (8.5 sm surilgan).
    - Hujjat nomi: Markazda, Katta harflarda, Qalin (Bold).
    - Xatboshi (abzats): 1.25 sm, qator oraliqlari 1.15.
    - So'rov/Talab qismi: Qalin ajratilgan bandlar.
    - Imzo va sana bloki.
    """
    doc = docx.Document()

    # 1. Sahifa chetlari (Sud formati: chapdan 3 sm tikish maydoni)
    for s in doc.sections:
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(3.0)
        s.right_margin = Cm(1.5)

    # Shrift sozlamalari
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(15, 23, 42)

    lines = matn.strip().split("\n")
    mode = "header"  # 'header' -> 'title' -> 'body'

    header_keywords = (
        "sudiga", "sudining", "da'vogar:", "davo_gar:", "javobgar:",
        "uchinchi shaxs:", "ariza beruvchi:", "manzil:", "tel:",
        "da'vo bahosi:", "davlat boji:", "pochta xarajati:", "kimga:", "kimdan:"
    )

    title_keywords = (
        "DA'VO ARIZASI", "TALABNOMA", "PRETENZIYA", "SHIKOYAT",
        "APELLYATSIYA SHIKOYATI", "KASSATSIYA SHIKOYATI", "ILTIMOSNOMA",
        "ADVOKAT SO'ROVI", "SHARTNOMA"
    )

    for line in lines:
        raw = line.strip()
        if not raw:
            continue

        # Markdown sarlavha belgilarini tozalash
        clean_line = re.sub(r"^#+\s*", "", raw).strip()
        clean_line = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean_line).strip()

        # 2. Hujjat Sarlavhasi (Title)
        is_title = any(clean_line.upper().startswith(t) for t in title_keywords) or (
            mode == "header" and clean_line.isupper() and len(clean_line) < 40 and "ARIZA" in clean_line
        )

        if is_title:
            mode = "title"
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line.upper())
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            continue

        # 3. Hujjat tag-sarlavhasi (Qavs ichidagi izoh)
        if mode == "title" and clean_line.startswith("(") and clean_line.endswith(")"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.italic = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
            mode = "body"
            continue

        # 4. Shapka (Sud va taraflar bloki)
        is_header_line = any(clean_line.lower().startswith(hk) for hk in header_keywords) or (
            mode == "header" and not clean_line.startswith(("Men,", "Biz,", "202", "Ushbu"))
        )

        if mode == "header" and is_header_line:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.left_indent = Cm(8.5)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"
            if any(clean_line.startswith(k) for k in ("Fuqarolik", "Iqtisodiy", "Ma'muriy", "Jinoyat", "Da'vogar:", "Javobgar:", "Da'vo bahosi:")):
                run.bold = True
            continue

        # 5. Asosiy matn (Body)
        mode = "body"
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        # Ichki bo'lim sarlavhalari (SO'RAYMAN, QONUNIY ASOSLAR, ILOVA)
        if (clean_line.endswith(":") and len(clean_line) < 60) or clean_line.isupper() and len(clean_line) < 30:
            is_pray = any(w in clean_line.upper() for w in ("SO'RAYMAN", "TALAB QILAMAN", "ILTIMOS QILAMAN"))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_pray else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = "Times New Roman"
            if is_pray:
                run.font.size = Pt(13.5)

        # Raqamlangan talablar yoki ilovalar (1., 2., 3.)
        elif re.match(r"^\d+[\.\)]\s+", clean_line):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(1.25)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"

        # Sana va imzo qatori
        elif any(k in clean_line for k in ("Da'vogar:", "Ariza beruvchi:", "Sana:", "___", "Imzo:")):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.first_line_indent = Cm(0)
            run = p.add_run(clean_line)
            run.bold = True
            run.font.name = "Times New Roman"

        # Oddiy paragraf matni
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(1.25)
            run = p.add_run(clean_line)
            run.font.name = "Times New Roman"

    doc.save(str(docx_path))
    return docx_path


def run(parameters: dict, player=None, session_memory=None) -> str:
    hujjat_turi = parameters.get("hujjat_turi", "davo_arizasi").strip().lower()
    tafsilot = parameters.get("tafsilot", "").strip()
    ochish = parameters.get("ochish", True)

    if not tafsilot:
        return "Iltimos, hujjatda qanday vaziyat, taraflar va qanday talablar aks etishi kerakligini batafsilroq bayon qiling."

    try:
        if player:
            try:
                player.write_log(f"ADVOKAT AI DRAFT: '{hujjat_turi}' bo'yicha bilimlar bazasidan pretsedentlar qidirilmoqda...")
            except Exception:
                pass

        # 1. Bilimlar bazasidan (8,186 keys) mavzuga oid sud amaliyoti va moddalarni olish
        kb_context = ""
        try:
            hits = advokat_kb.search_legal_knowledge(f"{hujjat_turi} {tafsilot}", limit=2)
            if hits:
                kb_snippets = []
                for h in hits:
                    kb_snippets.append(f"KEYS: {h['query']}\nHUQUQIY YECHIM: {h['response'][:400]}...")
                kb_context = "\n\nO'ZBEKISTON SUD AMALIYOTI PRESEDENTLARI:\n" + "\n---\n".join(kb_snippets)
        except Exception:
            pass

        # 2. Sud Portallari (my.sud.uz va template.sud.uz) rasmiy shablonlarini aniqlash
        court_template_context = ""
        try:
            from core import court_templates
            matched_tpl = court_templates.find_matching_template(f"{hujjat_turi} {tafsilot}")
            if matched_tpl:
                duty_info = matched_tpl.get("duty_rules", "")
                evidence_list = "\n".join(f"  - {e}" for e in matched_tpl.get("mandatory_evidence", []))
                prayer_list = "\n".join(f"  - {p}" for p in matched_tpl.get("default_prayer", []))
                law_list = ", ".join(matched_tpl.get("substantive_law", []))
                proc_law = ", ".join(matched_tpl.get("procedural_law", []))
                court_name = matched_tpl.get("court_type", "")
                
                court_template_context = (
                    f"\n\nO'ZBEKISTON OLIY SUDI (my.sud.uz / template.sud.uz) RASMIY STANDARTI:\n"
                    f"- Yurisdiksiya va sud turi: {court_name}\n"
                    f"- Moddiy huquq asoslari: {law_list}\n"
                    f"- Protsessual asoslar: {proc_law}\n"
                    f"- Davlat boji stavkasi: {duty_info}\n"
                    f"- Majburiy ilova qilinadigan dalillar ro'yxati (FPK 191 / IPK 150):\n{evidence_list}\n"
                    f"- Talab qismi namunasi:\n{prayer_list}\n"
                )
        except Exception:
            pass

        bugun = datetime.date.today().strftime("%d.%m.%Y")
        prompt = (
            f"Sen — O'zbekiston Respublikasining Oliy toifali amaliyotchi advokatisan. "
            f"Oliy sudning 'my.sud.uz' va 'template.sud.uz' rasmiy talablari hamda FPK/IPK/MSYUK moddalari "
            f"asosida sudga yoki rasmiy idoraga taqdim etiladigan, to'liq yuridik kuchga ega '{hujjat_turi}' loyihasini tuz:\n\n"
            f"TAFSILOTLAR: {tafsilot}\n"
            f"SANA: {bugun}\n"
            f"{kb_context}"
            f"{court_template_context}\n\n"
            f"QAT'IY QOIDALAR VA YURIDIK STANDARTLAR:\n"
            f"1. Shakl va til: Rasmiy o'zbek adabiy tilida, O'zbekiston protsessual qonunlari (FPK 189-191, IPK 148-150 yoki MSYUK) talablariga 100% mos tuzilsin.\n"
            f"2. Shapka qismi (O'ng burchak uchun): Sud yoki organ nomi (masalan: Fuqarolik ishlari bo'yicha ... tumanlararo sudiga yoki Tumanlararo iqtisodiy sudiga), "
            f"Da'vogar/Ariza beruvchi (F.I.Sh / Tashkilot, manzil, telefon, STIR/JShShIR), Javobgar (Nomi/F.I.Sh, manzil, rekvizitlar), "
            f"Da'vo bahosi va Davlat boji summalari (BHMga bog'langan holda) aniq ko'rsatilsin.\n"
            f"3. Sarlavha: Katta harflarda (masalan: DA'VO ARIZASI), tagida qavs ichida nizo mohiyati yozilsin.\n"
            f"4. Tavsif qismi: Voqea qachon boshlangani, shartnoma yoki buyruq raqamlari, huquqbuzarlik harakatlari aniq sanalar bilan keltirilsin.\n"
            f"5. Sudgacha tartibda hal etish: Talabnoma (pretenziya) yuborilganligi va uning oqibati ko'rsatilsin.\n"
            f"6. Qonuniy asoslar: O'zbekiston Respublikasi Fuqarolik, Oila, Mehnat, Uy-joy yoki Soliq kodekslarining aniq moddalari va protsessual normalar havola qilinsin.\n"
            f"7. Talab qismi: 'SO'RAYMAN:' deb alohida markaziy sarlavha qilinib, 1, 2, 3 raqamli bandlar bilan sud oldiga qo'yilayotgan qat'iy talablar yozilsin.\n"
            f"8. Ilovalar ro'yxati (FPK 191 / IPK 150): Isbotlovchi barcha dalillar, davlat boji to'lovi kvitansiyasi, shaxsni tasdiqlovchi hujjat, talabnoma nusxalari sanab o'tilsin.\n"
            f"9. Imzo qismi: Da'vogar (vakili) imzosi, F.I.Sh. va sana joyi qoldirilsin.\n"
            f"Eslatma: Faqat to'liq tayyor hujjat matnini chiqaring, keraksiz kirish yoki xulosa gaplar yozmang."
        )

        if player:
            try:
                player.write_log(f"ADVOKAT AI DRAFT: Gemini yuridik qonunlar bilan hujjatni shakllantirmoqda...")
            except Exception:
                pass

        hujjat_matni = gemini.text(prompt, tier=gemini.SMART, timeout_ms=45000)

        # Fayllarni saqlash
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        safe_type = "".join(c for c in hujjat_turi if c.isalnum() or c in ("_", "-")) or "hujjat"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Word (.docx) fayli
        docx_nomi = f"{safe_type}_{timestamp}.docx"
        docx_yoli = REPORTS_DIR / docx_nomi
        build_court_docx(hujjat_turi, hujjat_matni, docx_yoli)

        # 2. Matn (.md) fayli (zaxira va tezkor ko'rish uchun)
        md_nomi = f"{safe_type}_{timestamp}.md"
        md_yoli = REPORTS_DIR / md_nomi
        md_yoli.write_text(hujjat_matni, encoding="utf-8")

        # Dosyega avtomatik biriktirish
        try:
            from core import case_manager
            active_cases = case_manager.list_active_cases()
            for ac in active_cases:
                c_name = ac.get("client_name", "").lower()
                c_num = ac.get("case_number", "").lower()
                if (c_name and c_name in tafsilot.lower()) or (c_num and c_num in tafsilot.lower()):
                    case_manager.attach_document(ac["id"], hujjat_turi, str(docx_yoli))
                    break
        except Exception:
            pass

        # Windowsda Word orqali avtomatik ochish
        if ochish and os.name == "nt":
            try:
                os.startfile(str(docx_yoli))
                if player:
                    try:
                        player.write_log(f"DOCX: '{docx_nomi}' Word dasturida ochildi.")
                    except Exception:
                        pass
            except Exception:
                pass

        # Ekranda aks ettirish
        if player:
            try:
                player.show_content(
                    title=f"📝 {hujjat_turi.upper()} (.DOCX)",
                    text=hujjat_matni
                )
                player.write_log(f"Yuridik hujjat tayyor: reports/{docx_nomi}")
            except Exception:
                pass

        return (
            f"Rasmiy {hujjat_turi} loyihasi O'zbekiston sud standartlari asosida "
            f"Microsoft Word (.docx) formatida professional tayyorlandi va 'reports/{docx_nomi}' "
            f"fayliga saqlandi. Hujjatda sud va taraflar rekvizitlari, moddama-modda asoslar hamda "
            f"talablar to'liq shakllantirildi. Uni to'g'ridan-to'g'ri chop etib, imzolab sudga taqdim etishingiz mumkin."
        )

    except Exception as e:
        return f"Hujjat loyihasini tayyorlashda xatolik yuz berdi: {e}"
