import os
import sys
import logging
import requests
from dotenv import load_dotenv
from tkinter import messagebox

# 1. Force load .env
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

# 2. Immediate key validation
if not API_KEY or len(API_KEY) != 32:
    messagebox.showerror("Invalid Key", "Check .env file - key must be 32 chars")
    sys.exit(1)

# 3. Direct test
try:
    print(f"Testing key: {API_KEY[:4]}...{API_KEY[-4:]}")
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": "London", "appid": API_KEY, "units": "imperial"},
        timeout=10
    )
    
    if response.status_code == 200:
        print("Key works! Launching app...")
        from gui import launch_gui
        from core.weather_api import WeatherAPI
        from core.temp_predictor import TempPredictor  # Add this import
        launch_gui(WeatherAPI(API_KEY), TempPredictor())
    else:
        messagebox.showerror(
            "API Rejected",
            f"Status {response.status_code}\n{response.text}"
        )
except Exception as e:
    messagebox.showerror("Connection Failed", str(e))