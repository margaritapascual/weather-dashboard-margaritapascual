# features/current_conditions_icons.py

import os
import tkinter as tk

ICON_MAP = {
    "01d": "sun.png",       "01n": "moon.png",
    "02d": "partly_cloudy.png", "02n": "partly_cloudy_night.png",
    "03d": "cloud.png",     "03n": "cloud.png",
    "04d": "cloudy.png",    "04n": "cloudy.png",
    "09d": "rain.png",      "09n": "rain.png",
    "10d": "rain_sun.png",  "10n": "rain_moon.png",
    "11d": "storm.png",     "11n": "storm.png",
    "13d": "snow.png",      "13n": "snow.png",
    "50d": "mist.png",      "50n": "mist.png",
}

def load_icon(icon_code: str) -> tk.PhotoImage:
    fn = ICON_MAP.get(icon_code, "unknown.png")
    path = os.path.join(os.path.dirname(__file__), "icons", fn)
    return tk.PhotoImage(file=path)

def show_weather_icon(parent: tk.Frame, icon_code: str):
    img = load_icon(icon_code)
    lbl = tk.Label(parent, image=img)
    lbl.image = img
    lbl.pack(pady=5)
    return lbl
