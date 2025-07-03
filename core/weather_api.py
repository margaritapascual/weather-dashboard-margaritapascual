import requests
from requests.exceptions import RequestException
from .sample_weather_data import get_sample_weather

class WeatherAPI:
    """Fetch current weather from OpenWeatherMap, with sample-data fallback."""
    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def fetch_current(self, city: str) -> dict:
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(self.base_url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except RequestException as e:
                last_exc = e
                # optionally log: print(f"[WeatherAPI] attempt {attempt} failed: {e}")
        # all retries failed → fallback
        print(f"[WeatherAPI] API failure after {self.max_retries} tries: {last_exc}")
        return get_sample_weather(city)