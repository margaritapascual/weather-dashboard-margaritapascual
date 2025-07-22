from core.weather_api import WeatherAPI

# Use your own key here
API_KEY = "8ddd1a7540e2a9117566f9c413fc17b8"

def run_test():
    print("🌎 Geocoding 'Miami'...")
    api = WeatherAPI(api_key=API_KEY)

    try:
        lat, lon = api.geocode("Miami")
        print(f"✅ Coordinates: lat={lat}, lon={lon}")

        print("\n📡 Fetching current weather + alerts...")
        current_data = api.get_current(lat, lon)

        print("✅ Current data keys:", list(current_data.keys()))

        if "alerts" in current_data:
            print("\n🚨 ALERTS FOUND:")
            for alert in current_data["alerts"]:
                print(f"- {alert['event']}: {alert['description'][:100]}...")
        else:
            print("\n🔕 No alerts found in the response.")

        print("\n🌤️ Fetching 5-day forecast...")
        forecast = api.get_daily(lat, lon)
        for day in forecast:
            dt = day['dt']
            temp = day['temp']
            print(f"• Date: {dt}, High: {temp['max']}°F, Low: {temp['min']}°F")

    except Exception as e:
        print("❌ Error occurred:", e)

if __name__ == "__main__":
    run_test()
