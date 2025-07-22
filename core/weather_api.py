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

    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

        # Retry setup
        retry = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _request(self, endpoint: str, params: dict) -> Dict:
        """Generic request handler"""
        params['appid'] = self.api_key
        params['units'] = 'imperial'

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
        """Get lat/lon for a city using current weather endpoint"""
        # This endpoint is still v2.5
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.api_key
        }
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data['coord']['lat'], data['coord']['lon']
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding failed: {str(e)}")
            raise ValueError(f"Geocoding error: {str(e)}")

    def get_forecast_bundle(self, lat: float, lon: float) -> Dict:
        """
        Fetch current, daily forecast, and alerts from One Call API 3.0.
        This returns: current, minutely, hourly, daily, alerts
        """
        return self._request("onecall", {
            'lat': lat,
            'lon': lon,
            'exclude': 'minutely,hourly',
        })
