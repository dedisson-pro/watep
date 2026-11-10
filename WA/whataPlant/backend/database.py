import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "whataPlant.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    conn.commit()
    conn.close()
    print("✅ Base SQLite prête")

def save_scan(data: dict) -> int:
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO scans (image_path, common_name, scientific_name, family, confidence,
            is_edible, is_medicinal, is_toxic, is_invasive, health_status,
            ai_report, plantnet_raw, latitude, longitude)
        VALUES (:image_path, :common_name, :scientific_name, :family, :confidence,
            :is_edible, :is_medicinal, :is_toxic, :is_invasive, :health_status,
            :ai_report, :plantnet_raw, :latitude, :longitude)
    """, data)
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id

def get_all_scans():
    conn = get_db()
    rows = conn.execute("SELECT * FROM scans ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_scan_by_id(scan_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_dashboard_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    top_plants = conn.execute("""
        SELECT scientific_name, COUNT(*) as count FROM scans
        GROUP BY scientific_name ORDER BY count DESC LIMIT 5
    """).fetchall()
    edible   = conn.execute("SELECT COUNT(*) FROM scans WHERE is_edible='Oui'").fetchone()[0]
    medicinal= conn.execute("SELECT COUNT(*) FROM scans WHERE is_medicinal='Oui'").fetchone()[0]
    toxic    = conn.execute("SELECT COUNT(*) FROM scans WHERE is_toxic='Oui'").fetchone()[0]
    invasive = conn.execute("SELECT COUNT(*) FROM scans WHERE is_invasive='Oui'").fetchone()[0]
    recent   = conn.execute("""
        SELECT date(created_at) as day, COUNT(*) as count FROM scans
        GROUP BY day ORDER BY day DESC LIMIT 7
    """).fetchall()
    conn.close()
    return {
        "total": total,
        "top_plants": [dict(r) for r in top_plants],
        "by_category": {"edible": edible, "medicinal": medicinal, "toxic": toxic, "invasive": invasive},
        "recent": [dict(r) for r in recent]
    }
