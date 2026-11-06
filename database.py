
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "support_tickets.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'Unclassified',
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()
