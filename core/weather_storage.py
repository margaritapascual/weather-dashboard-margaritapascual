# core/weather_storage.py

import os
import sqlite3
from typing import List, Dict

class WeatherStorage:
    """SQLite-backed history of weather lookups."""
    def __init__(self, db_path: str):
        # Ensure parent directory exists (so sqlite can create the file)
        parent = os.path.dirname(db_path) or "."
        os.makedirs(parent, exist_ok=True)

        # Now connect
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    city        TEXT    NOT NULL,
                    country     TEXT,
                    temperature REAL,
                    description TEXT,
                    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def add_entry(self, entry: Dict):
        with self.conn:
            self.conn.execute("""
                INSERT INTO history (city, country, temperature, description)
                VALUES (:city, :country, :temperature, :description)
            """, entry)

    def get_last_n(self, n: int) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT city, country, temperature, description, timestamp
              FROM history
             ORDER BY timestamp DESC
             LIMIT ?
        """, (n,))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in rows]
