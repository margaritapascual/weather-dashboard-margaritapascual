# scheduler.py (data pull and CSV cleaning)
import pandas as pd
from core.weather_api import WeatherAPI
from datetime import datetime

API_KEY = 'YOUR_API_KEY'
CITIES = ['New York', 'London', 'Tokyo']
API = WeatherAPI(api_key=API_KEY)

# Fetch and append data for each city
rows = []
for city in CITIES:
    # daily forecast data
    for entry in API.get_forecast(city, freq='daily'):
        rows.append({
            'datetime': datetime.utcfromtimestamp(entry['dt']),
            'city': city,
            'temp_c': entry['temp']['day'],
            'humidity_pct': entry['humidity'],
            'pressure_hpa': entry['pressure'],
            'wind_speed_m_s': entry.get('wind_speed'),
            'wind_deg': entry.get('wind_deg'),
            'uvi': entry.get('uvi'),
            'weather_main': entry['weather'][0]['main'],
            'weather_desc': entry['weather'][0]['description'],
            'sunrise': datetime.utcfromtimestamp(entry['sunrise']),
            'sunset': datetime.utcfromtimestamp(entry['sunset']),
            'retrieval_time': datetime.utcnow(),
        })
# Load existing data
try:
    df = pd.read_csv('data/weather_clean.csv', parse_dates=['datetime', 'sunrise', 'sunset', 'retrieval_time'])
except FileNotFoundError:
    df = pd.DataFrame()

new_df = pd.DataFrame(rows)
# Concatenate and clean
combined = pd.concat([df, new_df], ignore_index=True)
# Drop duplicates by datetime+city
combined.drop_duplicates(subset=['datetime', 'city'], inplace=True)
# Sort and save
combined.sort_values(['city', 'datetime'], inplace=True)
combined.to_csv('data/weather_clean.csv', index=False)