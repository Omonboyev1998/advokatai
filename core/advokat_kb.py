"""
Advokat AI — Huquqiy Bilimlar Bazasi (Knowledge Base & Search Engine).
Exports papkasidagi 8,186 ta yuridik holatlar, qonun moddalari va advokat
taktikalarini tezkor qidiruv (SQLite FTS5) uchun indekslaydi va boshqaradi.
"""

from __future__ import annotations
import json
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import sys

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
EXPORTS_DIR = PROJECT_ROOT / "exports"
DATASET_PATH = EXPORTS_DIR / "advokat_ai_sft_chatml.jsonl"

def _get_kb_db_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / "memory" / "advokat_knowledge.db"
        if p.exists():
            return p
    if getattr(sys, "frozen", False):
        p = Path(sys.executable).parent / "memory" / "advokat_knowledge.db"
        if p.exists():
            return p
    return PROJECT_ROOT / "memory" / "advokat_knowledge.db"

DB_PATH = _get_kb_db_path()


def _clean_text(text: str) -> str:
    """Qidiruv uchun matnni tozalash."""
    # Belgilarni tozalash, so'zlarni ajratish
    return re.sub(r"[^\w\s]", " ", text).strip()


def init_database(force_rebuild: bool = False) -> int:
    """
    Ma'lumotlar bazasini tekshiradi va kerak bo'lsa exports faylidan indekslaydi.
    Qaytaradi: Indekslangan yozuvlar soni.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not DATASET_PATH.exists():
        print(f"[ADVOKAT_KB] Xatolik: {DATASET_PATH} topilmadi.")
        return 0

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Jadval mavjudligini tekshirish
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legal_knowledge'")
    table_exists = cursor.fetchone() is not None

    if table_exists and not force_rebuild:
        cursor.execute("SELECT COUNT(*) FROM legal_knowledge")
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return count

    # Jadvalni yaratish (FTS5 virtual jadvali)
    cursor.execute("DROP TABLE IF EXISTS legal_knowledge")
    cursor.execute("""
        CREATE VIRTUAL TABLE legal_knowledge USING fts5(
            query,
            response,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    batch = []
    total = 0

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                messages = item.get("messages", [])
                if len(messages) >= 3:
                    user_q = messages[1].get("content", "").strip()
                    assist_r = messages[2].get("content", "").strip()
                    if user_q and assist_r:
                        batch.append((user_q, assist_r))
                        total += 1
                        if len(batch) >= 1000:
                            cursor.executemany(
                                "INSERT INTO legal_knowledge(query, response) VALUES (?, ?)",
                                batch
                            )
                            batch.clear()
            except Exception:
                continue

    if batch:
        cursor.executemany(
            "INSERT INTO legal_knowledge(query, response) VALUES (?, ?)",
            batch
        )

    conn.commit()
    conn.close()
    print(f"[ADVOKAT_KB] Muvaffaqiyatli indekslandi: {total} ta yuridik holat.")
    return total


def search_legal_knowledge(query: str, limit: int = 2) -> List[Dict[str, str]]:
    """
    Foydalanuvchi savoli bo'yicha eng mos yuridik holat va advokat maslahatlarini topadi.
    """
    if not DB_PATH.exists():
        init_database()

    cleaned = _clean_text(query)
    words = [w for w in cleaned.split() if len(w) > 2]
    if not words:
        return []

    # Qidiruv so'rovini shakllantirish: so'zlar bo'yicha OR va NEAR qidiruv
    # FTS5 da "word1* OR word2*"
    match_query = " OR ".join([f'"{w}"*' for w in words[:8]])

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    results = []
    try:
        # BM25 tartiblash bo'yicha eng yuqori reytingdagi natijalarni olish
        cursor.execute("""
            SELECT query, response, rank
            FROM legal_knowledge
            WHERE legal_knowledge MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (match_query, limit))

        rows = cursor.fetchall()
        for r in rows:
            results.append({
                "query": r[0],
                "response": r[1]
            })
    except Exception as e:
        # Agar FTS sintaksisida xatolik bo'lsa oddiy LIKE bilan fallback
        wildcard = f"%{words[0]}%"
        cursor.execute("""
            SELECT query, response FROM legal_knowledge
            WHERE query LIKE ? OR response LIKE ?
            LIMIT ?
        """, (wildcard, wildcard, limit))
        for r in cursor.fetchall():
            results.append({
                "query": r[0],
                "response": r[1]
            })
    finally:
        conn.close()

    return results


def search_statutes(query: str, limit: int = 2) -> List[Dict[str, str]]:
    """
    O'zbekiston Respublikasi Kodekslari va Oliy Sud Plenumi qarorlarining
    rasmiy moddalarini qidiradi.
    """
    if not DB_PATH.exists():
        return []

    cleaned = _clean_text(query)
    words = [w for w in cleaned.split() if len(w) > 2]
    if not words:
        return []

    match_query = " OR ".join([f'"{w}"*' for w in words[:8]])
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    results = []

    try:
        cursor.execute("""
            SELECT code_name, article_no, title, content, rank
            FROM legal_statutes_fts
            WHERE legal_statutes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (match_query, limit))

        for r in cursor.fetchall():
            results.append({
                "code_name": r[0],
                "article_no": r[1],
                "title": r[2],
                "content": r[3]
            })
    except Exception:
        wildcard = f"%{words[0]}%"
        cursor.execute("""
            SELECT code_name, article_no, title, content
            FROM legal_statutes
            WHERE code_name LIKE ? OR article_no LIKE ? OR title LIKE ? OR content LIKE ?
            LIMIT ?
        """, (wildcard, wildcard, wildcard, wildcard, limit))
        for r in cursor.fetchall():
            results.append({
                "code_name": r[0],
                "article_no": r[1],
                "title": r[2],
                "content": r[3]
            })
    finally:
        conn.close()

    return results


def search_hybrid_legal(query: str, statute_limit: int = 2, precedent_limit: int = 2) -> Dict[str, Any]:
    """
    Gibrid qidiruv: Rasmiy qonun moddasi + Sud pretsedenti va amaliy advokatlik taktikasi.
    """
    statutes = search_statutes(query, limit=statute_limit)
    precedents = search_legal_knowledge(query, limit=precedent_limit)
    return {
        "statutes": statutes,
        "precedents": precedents
    }


def init_ish_yuritish_database() -> int:
    """
    O'zbek tilida ish yuritish qoidalari va hujjat namunalarini bazaga kiritadi.
    """
    try:
        from core.ish_yuritish_data import ISH_YURITISH_RULES
    except ImportError:
        try:
            from ish_yuritish_data import ISH_YURITISH_RULES
        except ImportError:
            return 0

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ish_yuritish_kb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            doc_type TEXT,
            title TEXT,
            procedure TEXT,
            keywords TEXT
        )
    """)

    cursor.execute("DROP TABLE IF EXISTS ish_yuritish_fts")
    cursor.execute("""
        CREATE VIRTUAL TABLE ish_yuritish_fts USING fts5(
            category,
            doc_type,
            title,
            procedure,
            keywords,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM ish_yuritish_kb")
    count = cursor.fetchone()[0]

    if count == 0:
        for r in ISH_YURITISH_RULES:
            cursor.execute("""
                INSERT INTO ish_yuritish_kb (category, doc_type, title, procedure, keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (r["category"], r["doc_type"], r["title"], r["procedure"], r["keywords"]))

    # FTS ni qayta to'ldirish
    cursor.execute("DELETE FROM ish_yuritish_fts")
    cursor.execute("""
        INSERT INTO ish_yuritish_fts (category, doc_type, title, procedure, keywords)
        SELECT category, doc_type, title, procedure, keywords FROM ish_yuritish_kb
    """)

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM ish_yuritish_kb")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def search_ish_yuritish(query: str, limit: int = 3) -> List[Dict[str, str]]:
    """
    O'zbek tilida ish yuritish, ariza, buyruq, xat, akt, bayonnoma qoidalari bo'yicha qidiruv.
    """
    if not DB_PATH.exists():
        return []

    # Baza jadvallarini tekshirish
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ish_yuritish_kb'")
    if not cursor.fetchone():
        conn.close()
        init_ish_yuritish_database()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

    cleaned = _clean_text(query)
    words = [w for w in cleaned.split() if len(w) > 2]
    if not words:
        conn.close()
        return []

    match_query = " OR ".join([f'"{w}"*' for w in words[:8]])
    results = []

    try:
        cursor.execute("""
            SELECT category, doc_type, title, procedure, rank
            FROM ish_yuritish_fts
            WHERE ish_yuritish_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (match_query, limit))

        for r in cursor.fetchall():
            results.append({
                "category": r[0],
                "doc_type": r[1],
                "title": r[2],
                "procedure": r[3]
            })
    except Exception:
        wildcard = f"%{words[0]}%"
        cursor.execute("""
            SELECT category, doc_type, title, procedure
            FROM ish_yuritish_kb
            WHERE title LIKE ? OR procedure LIKE ? OR keywords LIKE ?
            LIMIT ?
        """, (wildcard, wildcard, wildcard, limit))
        for r in cursor.fetchall():
            results.append({
                "category": r[0],
                "doc_type": r[1],
                "title": r[2],
                "procedure": r[3]
            })
    finally:
        conn.close()

    return results


if __name__ == "__main__":
    count = init_database(force_rebuild=False)
    print(f"Jami keyslar: {count}")
    iy_count = init_ish_yuritish_database()
    print(f"Ish yuritish me'yorlari: {iy_count}")
    test_iy = search_ish_yuritish("ishga qabul qilish buyrugi qanday yoziladi")
    print(f"Test ish yuritish qidiruvi: {len(test_iy)} ta")
    for item in test_iy:
        print(f"  -> [{item['category']}] {item['title']}")

