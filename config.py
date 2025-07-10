# config.py

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()   # pip install python-dotenv

@dataclass
class Config:
    api_key: str
    db_path: str
    request_timeout: int = 10

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("WEATHER_API_KEY", "8ddd1a7540e2a9117566f9c413fc17b8"),
            db_path=os.getenv("DATABASE_PATH", "./data/weather.db"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
        )
