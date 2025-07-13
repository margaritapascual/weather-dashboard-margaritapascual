# core/weather_jobs.py

import os
from datetime import datetime

from core.weather_api import WeatherAPI
from core.db          import get_connection, save_weather

# —————————————
# 1. Edit this list to include every city you care about.
#    You can also load it from a JSON/env var or external file if you prefer.
# —————————————
CITIES = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Miami",
]

def fetch_and_store_today() -> None:
    """
    Geocode + fetch current weather for each city in CITIES,
    then save it to the SQLite DB.
    """
    api = WeatherAPI(os.getenv("WEATHER_API_KEY"))
    conn = get_connection()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M")

    for city in CITIES:
        try:
            wx = api.current(city)            # uses the new `.current(city)` alias
            save_weather(conn, city, wx)      # upserts into history(date,location,...)
            print(f"[{now}] ✔ {city}: {wx['temp']}°F, {wx['description']}")
        except Exception as err:
            # don’t crash the whole loop if one city fails
            print(f"[{now}] ✖ {city}: {err}")

    conn.close()
    print(f"[{now}]  -- finished saving weather for {len(CITIES)} cities")


if __name__ == "__main__":
    fetch_and_store_today()
