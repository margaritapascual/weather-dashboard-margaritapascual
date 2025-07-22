import requests

class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org/data/2.5/onecall"
    GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"

    def __init__(self, api_key, timeout=10, max_retries=3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

    def geocode(self, city_name):
        params = {
            "q": city_name,
            "limit": 1,
            "appid": self.api_key
        }
        response = requests.get(self.GEOCODE_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError("City not found.")
        return results[0]["lat"], results[0]["lon"]

    def get_forecast(self, lat, lon):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "exclude": "minutely,hourly",
            "units": "imperial"
        }
        response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
