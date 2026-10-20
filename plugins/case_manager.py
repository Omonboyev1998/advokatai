"""
plugins/case_manager.py — Advokatlik Ishlar Dosyesi va Mijozlar Kabineti (Legal CRM & Case Dossier).

Advokatning sud ishlari, mijozlar bazasi, sud majlisi sanalari,
da'vo summalari, tayyorlangan arizalar va advokatlik eslatmalarini
boshqaradi hamda to'liq rasmiy Word (.docx) dosye hisobotini shakllantiradi.
"""

from __future__ import annotations
import datetime
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from core import case_manager

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

PLUGIN = {
    "name": "case_manager",
    "description": (
        "Advokatlik ishlar dosyesi va mijozlar kabinetini boshqarish (Legal Case Management & Dossier). "
        "Yangi sud ishi ochish, faol sud ishlari ro'yxatini ko'rish, yaqinlashib kelayotgan sud majlislari "
        "sanalari va vaqtlarini kuzatish, mijoz bo'yicha to'liq sud dosyesini (da'vo bahosi, sudya, "
        "sud nomi, tayyorlangan hujjatlar tarixi) ko'rish hamda to'liq rasmiy 'SUD ISHI DOSYESI' "
        "Microsoft Word (.docx) hisobotini tayyorlab avtomatik ochish."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "amal": {
                "type": "STRING",
                "description": (
                    "Bajariladigan amal: 'ish_ochish' (yangi ish kiritish), "
                    "'ishlar_royxati' (barcha faol sud ishlarini ko'rish), "
                    "'dosye_korish' (mijoz yoki ish bo'yicha to'liq ma'lumot), "
                    "'sud_sanasini_belgilash' (sud majlisi vaqtini kiritish/yangilash), "
                    "'qayd_qoshish' (advokatlik eslatmasi kiritish), "
                    "'ishni_yopish' (ishni yakunlash), "
                    "'dossier_docx' (to'liq Word dosye faylini shakllantirish)."
                )
            },
            "mijoz_fio": {
                "type": "STRING",
                "description": "Mijozning F.I.Sh. (masalan: 'Akmal Karimov')"
            },
            "ish_nomi": {
                "type": "STRING",
                "description": "Sud ishi mavzusi (masalan: 'Aliment undirish', 'Mehnat nizosi', 'Qarz undirish')"
            },
            "sud_nomi": {
                "type": "STRING",
                "description": "Ko'rilayotgan sud nomi (masalan: 'FIB Shayxontohur tumanlararo sudi')"
            },
            "ish_raqami": {
                "type": "STRING",
                "description": "Sud ishi raqami (masalan: '2-1001-2601/45')"
            },
            "majlis_vaqti": {
                "type": "STRING",
                "description": "Sud majlisi sanasi va vaqti (masalan: '2026-10-25 11:00')"
            },
            "tafsilot": {
                "type": "STRING",
                "description": "Qo'shimcha tafsilotlar: da'vo summasi, sudya ismi, qayd matni yoki nizo mohiyati"
            },
            "ochish": {
                "type": "BOOLEAN",
                "description": "Dosye Word faylini avtomatik ochish (sukut bo'yicha true)"
            }
        },
        "required": ["amal"]
    }
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    """
    Advokatlik ishlar dosyesi va mijozlar kabinetini boshqaruvchi asosiy interfeys.
    """
    amal = parameters.get("amal", "ishlar_royxati").strip().lower()
    mijoz_fio = parameters.get("mijoz_fio", "").strip()
    ish_nomi = parameters.get("ish_nomi", "").strip()
    sud_nomi = parameters.get("sud_nomi", "").strip()
    ish_raqami = parameters.get("ish_raqami", "").strip()
    majlis_vaqti = parameters.get("majlis_vaqti", "").strip()
    tafsilot = parameters.get("tafsilot", "").strip()
    ochish = parameters.get("ochish", True)

    try:
        # 1. YANGI ISH OCHISH
        if amal in ("ish_ochish", "yangi_ish"):
            if not mijoz_fio and not ish_nomi:
                return "Iltimos, sud ishi ochish uchun kamida mijoz F.I.Sh. yoki ish nomini ko'rsating."

            res = case_manager.create_case(
                client_name=mijoz_fio or "Noma'lum mijoz",
                case_title=ish_nomi or "Umumiy yuridik nizo",
                court_name=sud_nomi,
                case_number=ish_raqami,
                hearing_date=majlis_vaqti,
                summary=tafsilot
            )

            if player:
                try:
                    player.write_log(f"CASE CRM: Yangi ish ochildi: {res['case_number']} ({res['client_name']})")
                except Exception:
                    pass

            return (
                f"✅ **YANGI SUD ISHI MUVAFFAQIYATLI OCHILDI:**\n\n"
                f"• **Ish raqami:** `{res['case_number']}`\n"
                f"• **Mijoz:** {res['client_name']}\n"
                f"• **Nizo mavzusi:** {res['case_title']}\n"
                f"• **Sud:** {res['court_name'] or 'Hali belgilanmagan'}\n"
                f"• **Sud majlisi vaqti:** {res['hearing_date'] or 'Belgilanmagan'}\n"
                f"• **Holati:** Jarayonda\n\n"
                f"Ish bo'yicha hujjatlar va qaydlar avtomatik tarzda ushbu dosye bilan bog'lanadi."
            )

        # 2. FAOL ISHLAR RO'YXATI
        elif amal in ("ishlar_royxati", "royxat", "faol_ishlar"):
            cases = case_manager.list_active_cases()
            if not cases:
                return (
                    "📂 **ADVOKATLIK BAZASIDA FAOL SUD ISHLARI MAVJUD EMAS.**\n\n"
                    "Yangi ish ochish uchun: *'Mijoz Akmal Karimovga aliment bo'yicha ish och'* deb buyruq berishingiz mumkin."
                )

            lines = [f"📂 **ADVOKATNING FAOL SUD ISHLARI RO'YXATI ({len(cases)} ta ish):**\n"]
            for i, c in enumerate(cases, 1):
                sud_str = f" | Sud: {c['court_name']}" if c.get('court_name') else ""
                majlis_str = f" ⏰ **Majlis: {c['hearing_date']}**" if c.get('hearing_date') else " (Majlis belgilanmagan)"
                lines.append(
                    f"{i}. **[{c.get('case_number', '-')}]** {c.get('client_name', 'Mijoz')} — *{c.get('case_title', '')}*{sud_str}{majlis_str}"
                )

            lines.append("\n*Biror ish bo'yicha to'liq dosye ko'rish uchun mijoz ismini yoki ish raqamini ayting.*")
            natija = "\n".join(lines)

            if player:
                try:
                    player.show_content("📂 FAOL SUD ISHLARI", natija)
                except Exception:
                    pass

            return natija

        # 3. TO'LIQ DOSYE KO'RISH YOKI WORD EXPORT
        elif amal in ("dosye_korish", "dosye", "dossier_docx", "eksport"):
            q = ish_raqami or mijoz_fio or tafsilot
            if not q:
                return "Iltimos, qaysi ish yoki mijoz bo'yicha dosye kerakligini ko'rsating (masalan: 'Ali Valiyev')."

            case = case_manager.find_case(q)
            if not case:
                return f"'{q}' bo'yicha hech qanday sud ishi yoki mijoz topilmadi."

            # Word (.docx) dosye yaratish
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_num = "".join(c for c in case.get("case_number", "ish") if c.isalnum() or c in ("_", "-"))
            docx_name = f"dossier_{clean_num}_{stamp}.docx"
            docx_path = REPORTS_DIR / docx_name

            case_manager.build_case_dossier_docx(case, docx_path)

            if ochish and os.name == "nt":
                try:
                    os.startfile(str(docx_path))
                    if player:
                        try:
                            player.write_log(f"DOCX: '{docx_name}' Word dasturida ochildi.")
                        except Exception:
                            pass
                except Exception:
                    try:
                        subprocess.Popen(["cmd", "/c", "start", "", str(docx_path)], shell=True)
                    except Exception:
                        pass

            # Matnli hisobot
            docs_cnt = len(case.get("documents", []))
            notes_cnt = len(case.get("notes", []))
            reply = (
                f"🗂 **SUD ISHI DOSYESI: № {case.get('case_number', '-')}**\n\n"
                f"• **Mijoz:** {case.get('client_name', '-')} (Tel: {case.get('client_phone') or '-'})\n"
                f"• **Nizo mavzusi:** {case.get('case_title', '-')}\n"
                f"• **Ko'rib chiquvchi sud:** {case.get('court_name') or 'Belgilanmagan'}\n"
                f"• **Sudya:** {case.get('judge_name') or 'Tayinlanmagan'}\n"
                f"• **Qarshi taraf:** {case.get('opponent_name') or '-'}\n"
                f"• **Da'vo bahosi:** {case.get('claim_amount') or '0'} so'm\n"
                f"• **Keyingi sud majlisi:** {case.get('hearing_date') or 'Belgilanmagan'}\n"
                f"• **Joriy holati:** {case.get('status', 'jarayonda').upper()}\n"
                f"• **Biriktirilgan hujjatlar:** {docs_cnt} ta\n"
                f"• **Advokat qaydlari:** {notes_cnt} ta\n\n"
                f"📑 To'liq rasmiy dosye Word hujjati shakllantirildi: `reports/{docx_name}` va ochildi."
            )

            if player:
                try:
                    player.show_content(f"🗂 DOSYE: {case.get('case_number')}", reply)
                except Exception:
                    pass

            return reply

        # 4. SUD SANASINI YANGILASH
        elif amal in ("sud_sanasini_belgilash", "majlis_vaqti", "sana_ozgartirish"):
            q = ish_raqami or mijoz_fio or tafsilot
            if not q or not majlis_vaqti:
                return "Iltimos, ish raqami/mijoz ismi va yangi sud majlisi sanasi/vaqtini ko'rsating."

            ok = case_manager.update_hearing_date(q, majlis_vaqti)
            if ok:
                return f"✅ '{q}' ishi bo'yicha navbatdagi sud majlisi vaqti muvaffaqiyatli belgilandi: **{majlis_vaqti}**"
            else:
                return f"'{q}' bo'yicha ish topilmadi."

        # 5. QAYD QO'SHISH
        elif amal in ("qayd_qoshish", "eslatma"):
            q = ish_raqami or mijoz_fio
            if not q or not tafsilot:
                return "Iltimos, ishni ko'rsating va kiritilishi kerak bo'lgan advokatlik qaydini yozing."

            ok = case_manager.add_case_note(q, tafsilot)
            if ok:
                return f"📝 '{q}' sud ishi dosyesiga yangi advokatlik qaydi qo'shildi:\n*\"{tafsilot}\"*"
            else:
                return f"'{q}' bo'yicha ish topilmadi."

        # 6. ISHNI YOPISH
        elif amal in ("ishni_yopish", "yakunlash"):
            q = ish_raqami or mijoz_fio
            if not q:
                return "Iltimos, yopilishi kerak bo'lgan ish raqami yoki mijoz ismini ko'rsating."

            status = tafsilot or "yopildi"
            ok = case_manager.close_case(q, status)
            if ok:
                return f"🏁 '{q}' sud ishi muvaffaqiyatli yakunlandi (Holati: {status.upper()})."
            else:
                return f"'{q}' bo'yicha ish topilmadi."

        else:
            return f"Noma'lum amal: '{amal}'. Mavjud amallar: ish_ochish, ishlar_royxati, dosye_korish, sud_sanasini_belgilash, qayd_qoshish, ishni_yopish."

    except Exception as e:
        return f"Advokatlik ishlar dosyesini boshqarishda xatolik yuz berdi: {e}"


def execute(amal: str, mijoz_fio: str = "", ish_nomi: str = "", sud_nomi: str = "", ish_raqami: str = "", majlis_vaqti: str = "", tafsilot: str = "", ochish: bool = True) -> str:
    """Yordamchi/to'g'ridan-to'g'ri chaqirish funksiyasi."""
    return run({
        "amal": amal,
        "mijoz_fio": mijoz_fio,
        "ish_nomi": ish_nomi,
        "sud_nomi": sud_nomi,
        "ish_raqami": ish_raqami,
        "majlis_vaqti": majlis_vaqti,
        "tafsilot": tafsilot,
        "ochish": ochish
    })
