# main.py
from config import Config
from core.weather_api import WeatherAPI
from gui import MainWindow
from core.weather_api import WeatherAPI

def main():
    # Load config (API key + timeout)
    cfg = Config.from_env()
    
    # Instantiate API client
    api = WeatherAPI(api_key=cfg.api_key, timeout=cfg.request_timeout)
    
    # Instantiate GUI
    window = MainWindow()
    
    # Real search handler
    def handle_search(city: str):
        try:
            # 1. Fetch current weather JSON
            data = api.fetch_current(city)
            
            # 2. Parse out the bits we need
            parsed = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "description": data["weather"][0]["description"],
            }
            
            # 3. Display in GUI
            window.display_weather(parsed)
            
        except Exception as e:
            # On error (bad city, network, etc.) show a message
            window.show_error(f"Error: could not fetch weather for '{city}'")
            print("Fetch error:", e)  # also log to console for debugging
    
    # Hook up the real handler
    window.register_callback('search', handle_search)
    
    # Start the UI loop
    window.run()

if __name__ == "__main__":
    main()