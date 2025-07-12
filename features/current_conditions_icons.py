import os
from PIL import Image, ImageTk

ICON_MAP = {
    "01d": "sun.png", "01n": "moon.png",
    "02d": "partly_cloudy.png", "02n": "partly_cloudy_night.png",
    "03d": "cloud.png", "03n": "cloud.png",
    "04d": "cloudy.png", "04n": "cloudy.png",
    "09d": "rain.png", "09n": "rain.png",
    "10d": "rain_sun.png", "10n": "rain_moon.png",
    "11d": "storm.png", "11n": "storm.png",
    "13d": "snow.png", "13n": "snow.png",
    "50d": "mist.png", "50n": "mist.png",
}
_THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(_THIS_DIR, "icons")

def load_icon(icon_code: str, size=(50,50)):
    fn = ICON_MAP.get(icon_code)
    if not fn:
        raise KeyError(f"No mapping for icon code '{icon_code}'")
    path = os.path.join(ICONS_DIR, fn)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Icon not found: {path}")
    img = Image.open(path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)