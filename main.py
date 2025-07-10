from tkinter import Tk
from config import Config
from core.weather_api import WeatherAPI
from core.weather_storage import WeatherStorage
from gui import WeatherGUI

def main():
    # Load configuration (with dotenv fallback)
    cfg = Config.from_env()
    print("▶︎ Loaded API key:", cfg.api_key)  # Debug: show which key is in use

    api = WeatherAPI(cfg.api_key, timeout=cfg.request_timeout)
    storage = WeatherStorage(cfg.db_path)

    root = Tk()
    WeatherGUI(root, api, storage, cfg)
    root.mainloop()

if __name__ == "__main__":
    main()
