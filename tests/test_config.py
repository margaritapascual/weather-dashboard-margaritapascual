# tests/test_config.py

import os
import tempfile
import pytest
from config import Config

def test_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("WEATHER_API_KEY",    "KEY123")
    monkeypatch.setenv("DATABASE_PATH",      str(tmp_path/"weather.db"))
    monkeypatch.setenv("LOG_LEVEL",          "DEBUG")
    monkeypatch.setenv("MAX_RETRIES",        "5")
    monkeypatch.setenv("REQUEST_TIMEOUT",    "7")
    monkeypatch.setenv("SELECTED_FEATURES",  "current,history,graph")

    cfg = Config.from_env()
    assert cfg.api_key == "KEY123"
    assert cfg.database_path.endswith("weather.db")
    assert cfg.log_level == "DEBUG"
    assert cfg.max_retries == 5
    assert cfg.request_timeout == 7
    assert "history" in cfg.selected_features
