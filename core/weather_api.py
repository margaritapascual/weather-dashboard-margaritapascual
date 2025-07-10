import requests
from requests.exceptions import RequestException

class WeatherAPI:
    """Fetch current and daily weather via OpenWeatherMap One Call API 3.0 (°F)."""
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    def _onecall(self, lat: float, lon: float) -> dict:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,alerts",
            "units": "imperial",      # Fahrenheit
            "appid": self.api_key
        }
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_current(self, lat: float, lon: float) -> dict:
        """Return the current weather block."""
        data = self._onecall(lat, lon)
        return data["current"]

    def get_daily(self, lat: float, lon: float, days: int = 7) -> list[dict]:
        """Return up to `days` entries from the daily forecast array."""
        data = self._onecall(lat, lon)
        return data.get("daily", [])[:days]
