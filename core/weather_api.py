import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class WeatherAPI:
    """
    OpenWeatherMap API client using One Call API 3.0 (student plan)
    """

    BASE_URL = "https://api.openweathermap.org/data/3.0"

    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3,
                 units: str = "imperial", lang: str = "en"):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.units = units
        self.lang = lang

        retry = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # -------- public setters (used by GUI) ----------
    def set_units(self, units: str):
        self.units = units

    def set_lang(self, lang: str):
        self.lang = lang

    # -------- internal request helper ----------
    def _request(self, endpoint: str, params: dict) -> Dict:
        params['appid'] = self.api_key
        params['units'] = self.units
        params['lang']  = self.lang
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ValueError(f"API error: {str(e)}")

    def geocode(self, city: str) -> Tuple[float, float]:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': self.api_key, 'lang': self.lang}
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data['coord']['lat'], data['coord']['lon']
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding failed: {str(e)}")
            raise ValueError(f"Geocoding error: {str(e)}")

    def get_forecast_bundle(self, lat: float, lon: float) -> Dict:
        bundle = self._request("onecall", {
            'lat': lat,
            'lon': lon,
            'exclude': 'minutely,hourly',
        })
        # Compatibility: expose timezone offset on current as "timezone" (seconds)
        try:
            tz_off = bundle.get("timezone_offset", 0)
            if "current" in bundle and isinstance(bundle["current"], dict):
                bundle["current"]["timezone"] = tz_off
        except Exception:
            pass
        return bundle

    # ─── Adapter methods for gui.py ──────────────────────────────────────────

    def get_current(self, city: str) -> Dict:
        """Return the `current` dict for a given city name (with timezone injected)."""
        lat, lon = self.geocode(city)
        return self.get_forecast_bundle(lat, lon)["current"]

    def get_daily(self, city: str) -> list:
        """Return the `daily` list for a given city name."""
        lat, lon = self.geocode(city)
        return self.get_forecast_bundle(lat, lon)["daily"]

    def get_alerts(self, city: str) -> list:
        """Return the `alerts` list (possibly empty) for a given city name."""
        lat, lon = self.geocode(city)
        bundle = self.get_forecast_bundle(lat, lon)
        return bundle.get("alerts", [])

    def get_uv_index(self, coord: Dict) -> float:
        """Return the UV index from a coord/current dict."""
        return coord.get("uvi", 0.0)
