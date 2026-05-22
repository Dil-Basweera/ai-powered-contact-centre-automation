import os
import sqlite3


def get_connection():

    # Ensure database directory exists
    os.makedirs(
        "database",
        exist_ok=True
    )

    conn = sqlite3.connect(
        "database/tickets.db",
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        customer_name TEXT,

        email TEXT,

        query TEXT,

        category TEXT,

        priority TEXT,

        department TEXT,

        escalated INTEGER,

        passport_number TEXT,

        nationality TEXT,

        expiry_date TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    conn.close()