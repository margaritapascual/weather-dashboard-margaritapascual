import os
from dataclasses import dataclass

@dataclass
class Config:
    api_key: str
    db_path: str
    request_timeout: int = 10

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("WEATHER_API_KEY"),
            db_path=os.getenv("DATABASE_PATH", "./data/weather.db"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
        )
