import requests
from requests.exceptions import RequestException

class WeatherAPI:
    """Fetch current and daily weather via OpenWeatherMap One Call."""
    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    def _onecall(self, lat: float, lon: float) -> dict:
        url = "https://api.openweathermap.org/data/2.5/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": self.api_key
        }
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_current(self, lat: float, lon: float) -> dict:
        data = self._onecall(lat, lon)
        return data["current"]

    def get_daily(self, lat: float, lon: float, days: int = 7) -> list[dict]:
        data = self._onecall(lat, lon)
        return data["daily"][:days]
