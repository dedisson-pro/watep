import os
import json
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scans.db")

# Test PostgreSQL connectivity at startup; fall back to SQLite if unavailable
USE_POSTGRES = False
if DATABASE_URL:
    try:
        import psycopg2
        import psycopg2.extras
        _test = psycopg2.connect(DATABASE_URL)
        _test.close()
        USE_POSTGRES = True
        print("✅ PostgreSQL connecté")
    except Exception as _e:
        print(f"⚠️  PostgreSQL indisponible ({_e}) — bascule sur SQLite")


def get_db():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id              SERIAL PRIMARY KEY,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path      TEXT,
                common_name     TEXT,
                scientific_name TEXT,
                family          TEXT,
                confidence      REAL,
                is_edible       TEXT,
                is_medicinal    TEXT,
                is_toxic        TEXT,
                is_invasive     TEXT,
                health_status   TEXT,
                ai_report       TEXT,
                plantnet_raw    TEXT,
                latitude        REAL,
                longitude       REAL
            )
        """)
        print("Base PostgreSQL prete")
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path      TEXT,
                common_name     TEXT,
                scientific_name TEXT,
                family          TEXT,
                confidence      REAL,
                is_edible       TEXT,
                is_medicinal    TEXT,
                is_toxic        TEXT,
                is_invasive     TEXT,
                health_status   TEXT,
                ai_report       TEXT,
                plantnet_raw    TEXT,
                latitude        REAL,
                longitude       REAL
            )
        """)
        print("Base SQLite prete")
    conn.commit()
    cur.close()
    conn.close()


def save_scan(data: dict) -> int:
    conn = get_db()
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute("""
            INSERT INTO scans (image_path, common_name, scientific_name, family, confidence,
                is_edible, is_medicinal, is_toxic, is_invasive, health_status,
                ai_report, plantnet_raw, latitude, longitude)
            VALUES (%(image_path)s, %(common_name)s, %(scientific_name)s, %(family)s, %(confidence)s,
                %(is_edible)s, %(is_medicinal)s, %(is_toxic)s, %(is_invasive)s, %(health_status)s,
                %(ai_report)s, %(plantnet_raw)s, %(latitude)s, %(longitude)s)
            RETURNING id
        """, data)
        scan_id = cur.fetchone()[0]
    else:
        cur.execute("""
            INSERT INTO scans (image_path, common_name, scientific_name, family, confidence,
                is_edible, is_medicinal, is_toxic, is_invasive, health_status,
                ai_report, plantnet_raw, latitude, longitude)
            VALUES (:image_path, :common_name, :scientific_name, :family, :confidence,
                :is_edible, :is_medicinal, :is_toxic, :is_invasive, :health_status,
                :ai_report, :plantnet_raw, :latitude, :longitude)
        """, data)
        scan_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return scan_id


def get_all_scans():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scans ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_scan_by_id(scan_id: int):
    conn = get_db()
    cur = conn.cursor()
    if USE_POSTGRES:
        cur.execute("SELECT * FROM scans WHERE id = %s", (scan_id,))
    else:
        cur.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def get_dashboard_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scans")
    total = cur.fetchone()[0]
    cur.execute("""
        SELECT scientific_name, COUNT(*) as count FROM scans
        GROUP BY scientific_name ORDER BY count DESC LIMIT 5
    """)
    top_plants = [{"scientific_name": r[0], "count": r[1]} for r in cur.fetchall()]
    cur.execute("SELECT COUNT(*) FROM scans WHERE is_edible='Oui'")
    edible = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scans WHERE is_medicinal='Oui'")
    medicinal = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scans WHERE is_toxic='Oui'")
    toxic = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scans WHERE is_invasive='Oui'")
    invasive = cur.fetchone()[0]
    cur.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count FROM scans
        GROUP BY day ORDER BY day DESC LIMIT 7
    """)
    recent = [{"day": str(r[0]), "count": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {
        "total": total,
        "top_plants": top_plants,
        "by_category": {"edible": edible, "medicinal": medicinal, "toxic": toxic, "invasive": invasive},
        "recent": recent
    }
