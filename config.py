from dataclasses import dataclass
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# read .env into os.environ
load_dotenv()

@dataclass
class Config:
    api_key: str
    database_path: str
    log_level: str
    max_retries: int
    request_timeout: int

    @classmethod
    def from_environment(cls):
        """Load and validate configuration from environment"""
        api_key = os.getenv("WEATHER_API_KEY", "")
        if not api_key:
            logger.error("Missing WEATHER_API_KEY in environment")
            raise ValueError("Weather API key is required")

        database_path = os.getenv("DATABASE_PATH", "./data/weather.db")
        if not database_path.endswith('.db'):
            logger.warning(f"Unexpected database path extension: {database_path}")

        try:
            max_retries = int(os.getenv("MAX_RETRIES", "3"))
            request_timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))
        except ValueError as e:
            logger.error(f"Invalid numeric config value: {str(e)}")
            raise ValueError("Invalid configuration values") from e

        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level not in valid_log_levels:
            logger.warning(f"Invalid log level {log_level}, defaulting to INFO")
            log_level = "INFO"

        return cls(
            api_key=api_key,
            database_path=database_path,
            log_level=log_level,
            max_retries=max_retries,
            request_timeout=request_timeout
        )