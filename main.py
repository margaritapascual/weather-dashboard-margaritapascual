# main.py

from config import Config
from core.weather_api     import WeatherAPI
from core.weather_storage import WeatherStorage
from gui                  import MainWindow

def main():
    cfg     = Config.from_env()
    storage = WeatherStorage(cfg.database_path)
    api     = WeatherAPI(cfg.api_key, timeout=cfg.request_timeout, max_retries=cfg.max_retries)

    app = MainWindow(cfg, storage, api)
    app.run()

if __name__ == "__main__":
    main()
