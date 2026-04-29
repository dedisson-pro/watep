"""
Script de setup MySQL pour WhatAPlant.
Lance : python setup_db.py
"""
from dotenv import load_dotenv
load_dotenv()
import os
import pymysql

HOST     = os.getenv("MYSQL_HOST", "localhost")
PORT     = int(os.getenv("MYSQL_PORT", 3306))
USER     = os.getenv("MYSQL_USER", "root")
PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME  = os.getenv("MYSQL_DB", "whataPlant")

print(f"Connexion à MySQL : {USER}@{HOST}:{PORT}")

try:
    conn = pymysql.connect(
        host=HOST, port=PORT,
        user=USER, password=PASSWORD,
        charset="utf8mb4", autocommit=True
    )
    c = conn.cursor()

    # Supprimer et recréer la base
    c.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
    print(f"✅ Base '{DB_NAME}' supprimée")

    c.execute(
        f"CREATE DATABASE `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print(f"✅ Base '{DB_NAME}' créée")

    c.execute(f"USE `{DB_NAME}`")

    c.execute("""
        CREATE TABLE scans (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path      VARCHAR(255),
            common_name     VARCHAR(255),
            scientific_name VARCHAR(255),
            family          VARCHAR(255),
            confidence      FLOAT,
            is_edible       VARCHAR(50),
            is_medicinal    VARCHAR(50),
            is_toxic        VARCHAR(50),
            is_invasive     VARCHAR(50),
            health_status   TEXT,
            ai_report       LONGTEXT,
            plantnet_raw    LONGTEXT,
            latitude        DOUBLE,
            longitude       DOUBLE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Table 'scans' créée")

    conn.close()
    print("\n🎉 Base de données prête !")

except Exception as e:
    print(f"❌ Erreur : {e}")
