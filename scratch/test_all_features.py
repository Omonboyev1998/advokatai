"""
scratch/test_all_features.py — Barcha modullar, plaginlar va funksiyalarni to'liq tekshirish skripti.
"""
import sys
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

results = []

def test(name, func):
    try:
        msg = func()
        results.append((name, "PASS", msg or "OK"))
        print(f"[PASS] {name}: {msg or 'OK'}")
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        results.append((name, "FAIL", err))
        print(f"[FAIL] {name}: {err}")
        traceback.print_exc()

print("=" * 60)
print("1. MA'LUMOTLAR BAZALARI VA KORPUSLARNI TEKSHIRISH")
print("=" * 60)

def test_kb_db():
    import sqlite3
    db_path = PROJECT_ROOT / "memory" / "advokat_knowledge.db"
    assert db_path.exists(), "advokat_knowledge.db mavjud emas"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM legal_knowledge")
    cases = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM legal_statutes")
    statutes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ish_yuritish_kb")
    clerical = c.fetchone()[0]
    conn.close()
    return f"Keyslar: {cases}, Moddalar: {statutes}, Ish yuritish: {clerical}"

test("Advokat Knowledge Database", test_kb_db)

def test_cases_db():
    from core import case_manager
    cases = case_manager.list_active_cases()
    return f"Faol sud ishlari: {len(cases)} ta"

test("Case Manager Database", test_cases_db)

print("\n" + "=" * 60)
print("2. ASOSIY QIDIRUV VA GIBRID FUNKSIYALAR")
print("=" * 60)

def test_hybrid_search():
    from core import advokat_kb
    res = advokat_kb.search_hybrid_legal("mehnat shartnomasini bekor qilish")
    stat_len = len(res.get("statutes", []))
    prec_len = len(res.get("precedents", []))
    assert stat_len > 0, "Moddalar topilmadi"
    assert prec_len > 0, "Pretsedentlar topilmadi"
    return f"Topilgan moddalar: {stat_len}, pretsedentlar: {prec_len}"

test("Hybrid Legal Search", test_hybrid_search)

def test_ish_yuritish_search():
    from core import advokat_kb
    res = advokat_kb.search_ish_yuritish("ishga qabul qilish buyrugi")
    assert len(res) > 0, "Ish yuritish qoidasi topilmadi"
    return f"Topilgan qoidalar: {len(res)} ta"

test("Clerical Workflow Search", test_ish_yuritish_search)

print("\n" + "=" * 60)
print("3. BARCHA PLAGINLARNI YUKLASH (DISCOVERY)")
print("=" * 60)

def test_plugin_discovery():
    from core.plugin_loader import discover_plugins
    reg = discover_plugins(PROJECT_ROOT / "plugins", ())
    total = len(reg._plugins)
    assert total >= 23, f"Plaginlar soni kutilganidan kam: {total}"
    expected_plugins = [
        "advokat_ai", "court_calculator", "legal_draft", "ish_yuritish",
        "contract_audit", "legal_ocr", "case_manager", "moot_court", "lexuz_search"
    ]
    for p in expected_plugins:
        assert p in reg._plugins, f"Plagin yuklanmadi: {p}"
    return f"Yuklangan plaginlar: {total} ta (Barcha advokatlik plaginlari faol)"

test("Plugin Discovery & Validation", test_plugin_discovery)

print("\n" + "=" * 60)
print("4. PLAGINLARNING FUNKSIONAL SINOVI (EXECUTE / DRY-RUN)")
print("=" * 60)

def test_court_calc():
    from plugins import court_calculator
    out = court_calculator.run({"amal": "davlat_boji", "davo_turi": "mulkiy", "davo_bahosi": 50000000})
    assert "Davlat boji" in out or "so'm" in out
    return "Kalkulyator hisob-kitob qildi"

test("Plugin: court_calculator", test_court_calc)

def test_case_manager_plugin():
    from plugins import case_manager
    out = case_manager.execute("ishlar_royxati", ochish=False)
    assert "SUD ISHLARI" in out
    return "Ishlar ro'yxati chiqdi"

test("Plugin: case_manager", test_case_manager_plugin)

def test_moot_court_plugin():
    from plugins import moot_court
    from core.moot_court import get_current_session
    sess = get_current_session()
    return f"Sessiya o'qildi (active={sess.get('active')})"

test("Plugin: moot_court session", test_moot_court_plugin)

def test_docx_generators():
    from plugins.legal_draft import build_court_docx
    from plugins.ish_yuritish import build_ish_yuritish_docx
    from plugins.contract_audit import build_legal_opinion_docx
    from plugins.legal_ocr import build_ocr_analysis_docx
    from core.case_manager import build_case_dossier_docx
    from core.moot_court import build_hearing_prep_docx

    tmp_dir = PROJECT_ROOT / "reports" / "test_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1. legal draft docx
    p1 = tmp_dir / "t1.docx"
    build_court_docx("davo_arizasi", "DA'VO ARIZASI\n\nSO'RAYMAN:\n1. Undirilsin.", p1)
    assert p1.exists() and p1.stat().st_size > 5000

    # 2. ish yuritish docx
    p2 = tmp_dir / "t2.docx"
    build_ish_yuritish_docx("buyruq", "BUYRUQ\n\nBUYURAMAN:\n1. Ishga olinsin.", p2)
    assert p2.exists() and p2.stat().st_size > 5000

    # 3. contract audit docx
    p3 = tmp_dir / "t3.docx"
    build_legal_opinion_docx("ijara", "ijarachi", "QIZIL XAVFLAR:\n1. Penya yuqori.", p3)
    assert p3.exists() and p3.stat().st_size > 5000

    # 4. ocr docx
    p4 = tmp_dir / "t4.docx"
    build_ocr_analysis_docx("qaror.pdf", "I. REKVIZITLAR:\nFIB Mirobod sudi.", p4)
    assert p4.exists() and p4.stat().st_size > 5000

    # 5. dossier docx
    p5 = tmp_dir / "t5.docx"
    build_case_dossier_docx({"case_number": "ISH-01", "case_title": "Test ish"}, p5)
    assert p5.exists() and p5.stat().st_size > 5000

    # 6. moot prep docx
    p6 = tmp_dir / "t6.docx"
    build_hearing_prep_docx({"topic": "Test"}, "I. KIRISH NUTQI:\nHurmatli sud.", p6)
    assert p6.exists() and p6.stat().st_size > 5000

    # Cleanup
    for f in tmp_dir.glob("*.docx"):
        try: f.unlink()
        except: pass
    try: tmp_dir.rmdir()
    except: pass

    return "Barcha 6 ta Word (.docx) generatorlari 100% ishlamoqda"

test("DOCX Generators (All 6 tools)", test_docx_generators)

print("\n" + "=" * 60)
print("5. GUI VA TEZKOR TUGMALAR INTEGRATSIYASI")
print("=" * 60)

def test_gui_imports():
    import ui
    from gui.window import MainWindow
    from gui.widgets import FileDropZone, IconButton, LogWidget
    return "UI va barcha vizual klasslar to'liq import bo'ldi"

test("GUI & Widget Classes", test_gui_imports)

def test_quick_actions_methods():
    from gui.window import MainWindow
    methods = [
        "_build_advokat_actions", "_on_quick_davo", "_on_quick_audit",
        "_on_quick_ish", "_on_quick_cases", "_on_quick_moot", "_on_quick_ocr"
    ]
    for m in methods:
        assert hasattr(MainWindow, m), f"MainWindow da metod yo'q: {m}"
    return "Barcha 6 ta tezkor advokatlik tugma metodlari mavjud"

test("MainWindow Quick Actions Methods", test_quick_actions_methods)

print("\n" + "=" * 60)
print("YAKUNIY NATIJALAR:")
print("=" * 60)
passed = sum(1 for r in results if r[1] == "PASS")
failed = sum(1 for r in results if r[1] == "FAIL")
print(f"Jami sinovlar: {len(results)} | Muvaffaqiyatli: {passed} | Xatoliklar: {failed}")
if failed == 0:
    print("\n>>> BARCHA FUNKSIYALAR 100% ISHCHI HOLATDA! <<<")
