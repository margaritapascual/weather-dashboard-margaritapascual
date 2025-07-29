# scheduler.py
import os
import pandas as pd
from datetime import datetime
from core.weather_api import WeatherAPI

# ——— CONFIG ———
# Require your real API key from the env
API_KEY = os.environ["OPENWEATHER_API_KEY"]
# print(f"Loaded API key: {API_KEY[:4]}…")  # verify env var is working

OUT_CSV = "data/weather.csv"
CITIES = [
    {"city": "New York", "state": "NY",   "country": "USA"},
    {"city": "London",   "state": "",     "country": "UK"},
    {"city": "Tokyo",    "state": "",     "country": "Japan"},
]
# ——————————

API = WeatherAPI(api_key=API_KEY)

def fetch_and_build_rows():
    rows = []
    now_str = datetime.utcnow().strftime("%m-%d-%y %H:%M:%S")
    # We know get_daily exists
    fetch = lambda city: API.get_daily(city)

    for loc in CITIES:
        raw = fetch(loc["city"])
        for entry in raw:
            rows.append({
                "current time (mm-dd-yy hh:mm:ss)": now_str,
                "City":           loc["city"],
                "State":          loc["state"],
                "Country":        loc["country"],
                "Temperature":    entry["temp"]["day"],
                "Feels Like":     entry.get("feels_like", {}).get("day"),
                "Humidity":       entry.get("humidity"),
                "Precipitation":  entry.get("rain", 0),
                "Pressure":       entry.get("pressure"),
                "Wind Speed":     entry.get("wind_speed"),
                "Wind Direction": entry.get("wind_deg"),
                "Visibility":     entry.get("visibility"),
                "Sunrise":        datetime.utcfromtimestamp(entry["sunrise"]).strftime("%H:%M:%S"),
                "Sunset":         datetime.utcfromtimestamp(entry["sunset"]).strftime("%H:%M:%S"),
            })
    return rows

def append_to_csv(rows, out_path=OUT_CSV):
    df = pd.DataFrame(rows)
    header = not os.path.exists(out_path)
    df.to_csv(out_path, mode="a", index=False, header=header)
    print(f"✅ Appended {len(df)} rows to {out_path}")

if __name__ == "__main__":
    rows = fetch_and_build_rows()
    append_to_csv(rows)
