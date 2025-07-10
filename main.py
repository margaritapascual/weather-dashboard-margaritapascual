# main.py

import tkinter as tk
from config import Config
from core.weather_api import WeatherAPI
from core.weather_storage import WeatherStorage
from gui import WeatherGUI

def main():
    # Load configuration
    cfg = Config.from_env()

    # Initialize API client and storage
    api     = WeatherAPI(cfg.api_key, cfg.request_timeout)
    storage = WeatherStorage(cfg.db_path)

    # Create and size the root window
    root = tk.Tk()
    root.title("Weather Dashboard")
    root.geometry("900x600")    # ensure it's large enough to see

    # Build and run the GUI
    WeatherGUI(root, api, storage, cfg)
    root.mainloop()

if __name__ == "__main__":
    main()
