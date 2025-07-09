import sqlite3
import os

class WeatherStorage:
    """Keeps a rolling 30-day history of daily precip & humidity."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                date TEXT PRIMARY KEY,
                precip REAL,
                humidity REAL
            )
        """)
        self.conn.commit()

    def save_daily(self, date: str, precip: float, humidity: float):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO history(date, precip, humidity) VALUES (?,?,?)",
            (date, precip, humidity)
        )
        self.conn.commit()

    def get_history(self, limit: int = 30) -> list[tuple[str,float,float]]:
        c = self.conn.cursor()
        c.execute(
            "SELECT date, precip, humidity FROM history ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        rows = c.fetchall()
        # return oldest-first
        return list(reversed(rows))
