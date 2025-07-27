#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox
import requests
from dotenv import load_dotenv

from core.weather_api import WeatherAPI
from core.temp_predictor import TempPredictor
from gui import launch_gui

def main():
    # 1) Create & hide root so messageboxes have a valid parent
    root = tk.Tk()
    root.withdraw()

    # 2) Load .env
    load_dotenv()
    API_KEY = os.getenv("WEATHER_API_KEY")

    # 3) Validate key presence
    if not API_KEY:
        messagebox.showerror(
            title="Invalid Key",
            message="WEATHER_API_KEY is not set in your .env",
            parent=root
        )
        root.destroy()
        sys.exit(1)

    # 4) Validate key length
    if len(API_KEY) != 32:
        messagebox.showerror(
            title="Invalid Key",
            message=f"API key length is {len(API_KEY)}; it must be 32 characters.",
            parent=root
        )
        root.destroy()
        sys.exit(1)

    # 5) Test & launch
    try:
        print(f"Testing key: {API_KEY[:4]}...{API_KEY[-4:]}")
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": "London", "appid": API_KEY, "units": "imperial"},
            timeout=10
        )
        if resp.status_code == 200:
            print("Key works! Launching app…")
            root.destroy()
            launch_gui(WeatherAPI(API_KEY), TempPredictor())
        else:
            messagebox.showerror(
                title="API Rejected",
                message=f"Status {resp.status_code}\n\n{resp.text}",
                parent=root
            )
            root.destroy()
            sys.exit(1)

    except Exception as e:
        messagebox.showerror(
            title="Connection Failed",
            message=str(e),
            parent=root
        )
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
