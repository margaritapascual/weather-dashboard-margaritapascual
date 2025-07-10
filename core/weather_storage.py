# core/weather_storage.py

import sqlite3
import os

class WeatherStorage:
    """Keeps a rolling 30-day history of daily weather, including temp & description."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._migrate()

    def _migrate(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
        if c.fetchone():
            # check existing columns
            c.execute("PRAGMA table_info(history)")
            cols = [r[1] for r in c.fetchall()]
            expected = ["date", "precip", "humidity", "temp", "description"]
            if cols != expected:
                c.execute("DROP TABLE history")
                self.conn.commit()
                self._create_table()
        else:
            self._create_table()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE history (
                date TEXT PRIMARY KEY,
                precip REAL,
                humidity REAL,
                temp REAL,
                description TEXT
            )
        """)
        self.conn.commit()

    def save_daily(self,
                   date: str,
                   precip: float,
                   humidity: float,
                   temp: float,
                   description: str):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO history(date, precip, humidity, temp, description) "
            "VALUES (?,?,?,?,?)",
            (date, precip, humidity, temp, description)
        )
        self.conn.commit()

    def get_history(self, limit: int = 30):
        c = self.conn.cursor()
        c.execute(
            "SELECT date, precip, humidity, temp, description "
            "FROM history ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        rows = c.fetchall()
        # oldest first
        return list(reversed(rows))
