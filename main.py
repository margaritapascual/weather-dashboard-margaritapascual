# main.py

import tkinter as tk
from config import Config
from core.weather_api     import WeatherAPI
from core.weather_storage import WeatherStorage
from gui                  import WeatherDashboard

def main():
    cfg     = Config.from_env()
    storage = WeatherStorage(cfg.database_path)
    api     = WeatherAPI(cfg.api_key,
                         timeout=cfg.request_timeout,
                         max_retries=cfg.max_retries)

    root = tk.Tk()
    app  = WeatherDashboard(root, cfg, storage, api)
    root.mainloop()

if __name__ == "__main__":
    main()
