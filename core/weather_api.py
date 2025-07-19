# core/weather_api.py

import requests
from requests.exceptions import RequestException

class WeatherAPI:
    """Fetch geolocation, current conditions, and daily forecasts
       from OpenWeatherMap’s One Call API."""
    GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
    ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3):
        self.api_key     = api_key
        self.timeout     = timeout
        self.max_retries = max_retries

    def _get(self, url: str, params: dict) -> dict:
        """Internal helper to GET + retry + raise_for_status()."""
        for attempt in range(self.max_retries):
            try:
                resp = requests.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except RequestException:
                if attempt == self.max_retries - 1:
                    raise

    def geocode(self, city: str) -> tuple[float, float]:
        """Turn a city name into (lat, lon). Raises ValueError if not found."""
        params = {
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }
        data = self._get(self.GEOCODE_URL, params)
        if not data:
            raise ValueError(f"Could not find location for '{city}'")
        return data[0]["lat"], data[0]["lon"]

    def get_current(self, lat: float, lon: float) -> dict:
        """Return a dict with keys: temp, humidity, uvi, weather (list), alerts (list)."""
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,daily",
            "units": "imperial",
            "appid": self.api_key
        }
        data = self._get(self.ONECALL_URL, params)
        current = data.get("current", {})
        return {
            "temp":     current.get("temp"),
            "humidity": current.get("humidity"),
            "uvi":      current.get("uvi"),
            "weather":  current.get("weather", []),
            "alerts":   data.get("alerts", [])
        }

    def get_daily(self, lat: float, lon: float, days: int = 7) -> list[dict]:
        """Return a list of up to `days` daily forecast dicts (each with dt, temp, weather…)."""
        params = {
            "lat":     lat,
            "lon":     lon,
            "exclude": "current,minutely,hourly,alerts",
            "units":   "imperial",
            "appid":   self.api_key
        }
        data = self._get(self.ONECALL_URL, params)
        daily = data.get("daily", [])
        return daily[:days]