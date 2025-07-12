from gui import launch_gui
from config import Config
from core.weather_api import WeatherAPI

if __name__ == "__main__":
    cfg = Config.from_environment()
    api = WeatherAPI(
        cfg.api_key,
        timeout=cfg.request_timeout,
        max_retries=cfg.max_retries
    )
    launch_gui(api)
