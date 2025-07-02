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
    selected_features: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls):
        # Read a comma-separated list from ENV, e.g.
        # SELECTED_FEATURES=current_conditions_icons,temperature_graph
        raw = os.getenv("SELECTED_FEATURES", "")
        features = [f.strip() for f in raw.split(",") if f.strip()]

        return cls(
            api_key=os.getenv("WEATHER_API_KEY"),
            database_path=os.getenv("DATABASE_PATH"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_retries=int(os.getenv("MAX_RETRIES", 3)),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", 10)),
            selected_features=features
        )
