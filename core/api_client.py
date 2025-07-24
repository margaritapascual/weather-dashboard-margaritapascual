# core/api_client.py
import requests
from typing import Tuple, Dict, List
import logging

class WeatherAPI:
    """Standalone OpenWeatherMap API client with no dependencies"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def geocode(self, city: str) -> Tuple[float, float]:
        """Get coordinates for a city name"""
        url = "https://api.openweathermap.org/geo/1.0/direct"
        resp = self.session.get(url, params={
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"City not found: {city}")
        return data[0]["lat"], data[0]["lon"]

    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather conditions"""
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = self.session.get(url, params={
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_daily_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict]:
        """Get daily forecast"""
        url = "https://api.openweathermap.org/data/2.5/forecast/daily"
        resp = self.session.get(url, params={
            "lat": lat,
            "lon": lon,
            "cnt": days,
            "appid": self.api_key,
            "units": "imperial"
        }, timeout=10)
        resp.raise_for_status()
        return resp.json()["list"]