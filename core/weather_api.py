import requests
from requests.exceptions import RequestException

class WeatherAPI:
    """
    Fetches weather data from OpenWeatherMap One Call API 3.0 (current, daily, alerts)
    using imperial units.
    """
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    def _one_call(self, lat: float, lon: float) -> dict:
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly",  # we only need current, daily, alerts
            "units": "imperial",
            "appid": self.api_key,
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except RequestException as e:
            raise RuntimeError(f"Weather API request failed: {e}")

    def get_current(self, lat: float, lon: float) -> dict:
        """
        Returns the 'current' block from the One Call response.
        """
        return self._one_call(lat, lon).get("current", {})

    def get_daily(self, lat: float, lon: float, days: int = 7) -> list[dict]:
        """
        Returns the first `days` entries of the 'daily' block.
        """
        return self._one_call(lat, lon).get("daily", [])[:days]

    def get_alerts(self, lat: float, lon: float) -> list[dict]:
        """
        Returns the 'alerts' array (if any) from the One Call response.
        """
        return self._one_call(lat, lon).get("alerts", [])