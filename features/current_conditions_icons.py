# features/current_conditions_icons.py

import os
import tkinter as tk
from PIL import Image, ImageTk

# map OWM codes → your local icon filenames
ICON_MAP = {
    "01d": "sun.png",       "01n": "moon.png",
    "02d": "partly_cloudy.png",    "02n": "partly_cloudy_night.png",
    "03d": "cloud.png",     "03n": "cloud.png",
    "04d": "cloudy.png",    "04n": "cloudy.png",
    "09d": "rain.png",      "09n": "rain.png",
    "10d": "rain_sun.png",  "10n": "rain_moon.png",
    "11d": "storm.png",     "11n": "storm.png",
    "13d": "snow.png",      "13n": "snow.png",
    "50d": "mist.png",      "50n": "mist.png",
}

# __file__ is features/current_conditions_icons.py
_THIS_DIR   = os.path.dirname(__file__)
ICONS_DIR   = os.path.join(_THIS_DIR, "icons")   # now points at features/icons

def load_icon(icon_code: str, size=(50,50)) -> ImageTk.PhotoImage:
    """
    1) Load the local icon at <project>/features/icons/<filename>.
    2) Fail fast if missing so you’ll spot it immediately.
    Returns a PhotoImage resized to `size`.
    """
    fn = ICON_MAP.get(icon_code)
    if not fn:
        raise KeyError(f"No mapping for icon code '{icon_code}' in ICON_MAP")
    path = os.path.join(ICONS_DIR, fn)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Expected icon file not found: {path}")

    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def show_weather_icon(parent: tk.Frame, icon_code: str, size=(50,50)) -> tk.Label:
    """
    Pack a Label into `parent` with the icon for `icon_code`.
    Returns the Label (so you can place text next to it, etc.).
    """
    img = load_icon(icon_code, size=size)
    lbl = tk.Label(parent, image=img, bg=parent["bg"])
    lbl.image = img
    lbl.pack(pady=5)
    return lbl
