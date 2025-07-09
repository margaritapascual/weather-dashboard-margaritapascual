from tkinter import Tk
from config import Config
from core.weather_api import WeatherAPI
from core.weather_storage import WeatherStorage
from gui import WeatherGUI

def main():
    cfg     = Config.from_env()
    api     = WeatherAPI(cfg.api_key, timeout=cfg.request_timeout)
    storage = WeatherStorage(cfg.db_path)

    root = Tk()
    WeatherGUI(root, api, storage, cfg)
    root.mainloop()

if __name__ == "__main__":
    main()
