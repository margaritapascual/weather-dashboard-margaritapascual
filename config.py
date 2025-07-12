# config.py

from dataclasses import dataclass
from dotenv import load_dotenv
import os

# read .env into os.environ
load_dotenv()

@dataclass
class Config:
    api_key: str
    database_path: str
    log_level: str = "INFO"
    max_retries: int = 3
    request_timeout: int = 10

    @classmethod
    def from_environment(cls):
        return cls(
            api_key         = os.getenv("WEATHER_API_KEY", ""),
            database_path   = os.getenv("DATABASE_PATH", "./data/weather.db"),
            log_level       = os.getenv("LOG_LEVEL", "INFO"),
            max_retries     = int(os.getenv("MAX_RETRIES", 3)),
            request_timeout = int(os.getenv("REQUEST_TIMEOUT", 10)),
        )
