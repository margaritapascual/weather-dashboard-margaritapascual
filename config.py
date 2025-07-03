# config.py

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import List

load_dotenv()

@dataclass
class Config:
    api_key: str
    database_path: str
    log_level: str = "INFO"
    max_retries: int = 3
    request_timeout: int = 10
    alert_threshold_high: float = 35.0  # °C
    alert_threshold_low: float  = 0.0   # °C
    selected_features: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls):
        raw = os.getenv("SELECTED_FEATURES", "")
        features = [f.strip() for f in raw.split(",") if f.strip()]
        return cls(
            api_key=os.getenv("WEATHER_API_KEY", ""),
            database_path=os.getenv("DATABASE_PATH", "./data/weather.db"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_retries=int(os.getenv("MAX_RETRIES", 3)),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", 10)),
            alert_threshold_high=float(os.getenv("ALERT_HIGH", 35.0)),
            alert_threshold_low =float(os.getenv("ALERT_LOW", 0.0)),
            selected_features=features
        )
