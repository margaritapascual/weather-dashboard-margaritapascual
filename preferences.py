# preferences.py
import json
import os
from copy import deepcopy

PREF_FILE = "user_preferences.json"

DEFAULT_PREFS = {
    "version": 1,
    "language": "en",                          # "en" | "es"
    "theme": {
        "mode": "light",                       # "light" | "dark"
        "font_scale": 1.0
    },
    "units": {
        "temperature": "imperial",             # "imperial" | "metric"
        "wind_speed": "mph"                    # "mph" | "km/h" | "m/s"
    },
    "location": {
        "default_city": "New York, US",
        "favorites": []
    },
    "chart": {
        "default_type": "line"                 # "line" | "bar" | "scatter"
    },
    "time": {
        "format_24h": False
    },
    "forecast": {
        "default_tab": "5_day"
    },
    "refresh": {
        "interval_seconds": 900                # 0 disables auto-refresh
    },
    "alerts": {
        "enabled": True
    }
}


def deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge 'override' into 'base', returning the merged dict.
    """
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def load_preferences() -> dict:
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, "r") as f:
                user_prefs = json.load(f)
            prefs = deep_merge(deepcopy(DEFAULT_PREFS), user_prefs)
            return prefs
        except (json.JSONDecodeError, OSError):
            return deepcopy(DEFAULT_PREFS)
    return deepcopy(DEFAULT_PREFS)


def save_preferences(prefs: dict) -> None:
    try:
        with open(PREF_FILE, "w") as f:
            json.dump(prefs, f, indent=4)
    except OSError:
        pass
