# scheduler.py

import time
import schedule
from config import Config
from core.weather_api import WeatherAPI
from features.historical_data import save_history

# --- Configure your job once ---
def fetch_and_save():
    city = "New York"   # ← Change this to whatever city you want logged daily
    cfg = Config.from_environment()
    api = WeatherAPI(
        cfg.api_key,
        timeout=cfg.request_timeout,
        max_retries=cfg.max_retries
    )

    try:
        lat, lon = api.geocode(city)
        daily = api.get_daily(lat, lon, days=7)
        save_history(city, daily)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Saved history for {city}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching {city}: {e}")

# Schedule it for 8:00 AM every day
schedule.every().day.at("08:00").do(fetch_and_save)

# --- Keep the scheduler running ---
if __name__ == "__main__":
    print("Scheduler started, will run daily at 08:00")
    while True:
        schedule.run_pending()
        time.sleep(30)
