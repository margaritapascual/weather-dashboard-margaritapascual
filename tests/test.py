from core.weather_api import WeatherAPI

def test_weather_api():
    # Provide your actual API key here
    api = WeatherAPI(api_key="8ddd1a7540e2a9117566f9c413fc17b8")  # ← Add this
    
    print("Geocoding Miami...")
    lat, lon = api.geocode("miami")
    print(f"Coordinates: {lat}, {lon}")

    print("\nCurrent Weather:")
    current = api.get_current(lat, lon)
    print(current)

    print("\n7-Day Forecast:")
    daily = api.get_daily(lat, lon, days=7)
    print(daily)

if __name__ == "__main__":
    test_weather_api()