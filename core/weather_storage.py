import sqlite3
import os

class WeatherStorage:
    """Keeps a rolling 30-day history of daily precip & humidity, migrating old schemas if needed."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._migrate_if_needed()
        self._create_table()

    def _migrate_if_needed(self):
        # If existing table schema does not have 'date', drop and recreate
        c = self.conn.cursor()
        c.execute("PRAGMA table_info(history)")
        cols = [row[1] for row in c.fetchall()]
        if cols and 'date' not in cols:
            c.execute("DROP TABLE IF EXISTS history")
            self.conn.commit()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                date TEXT PRIMARY KEY,
                precip REAL,
                humidity REAL
            )
            """
        )
        self.conn.commit()

    def save_daily(self, date: str, precip: float, humidity: float):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO history(date, precip, humidity) VALUES (?, ?, ?)",
            (date, precip, humidity)
        )
        self.conn.commit()

    def get_history(self, limit: int = 30):
        c = self.conn.cursor()
        c.execute(
            "SELECT date, precip, humidity FROM history ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        rows = c.fetchall()
        # Return oldest-first for plotting
        return list(reversed(rows))