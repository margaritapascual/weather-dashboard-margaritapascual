# tests/test_config.py

import os
from dotenv import load_dotenv

def test_api_key_loaded():
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    assert api_key is not None and api_key != "", "API key should be loaded from .env"
