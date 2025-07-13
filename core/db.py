# core/db.py
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "weather.db"

def get_connection() -> sqlite3.Connection:
    """Open (or create) the SQLite database."""
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)

def save_weather(conn: sqlite3.Connection, city: str, wx: dict) -> None:
    """
    Upsert today's weather for `city`.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO history
          (date, location, precip, humidity, temp, description)
        VALUES
          (date('now'), ?, ?, ?, ?, ?)
        """,
        (
            city,
            wx["precip"],
            wx["humidity"],
            wx["temp"],
            wx["description"],
        ),
    )
    conn.commit()
