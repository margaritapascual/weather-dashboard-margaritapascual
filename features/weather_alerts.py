# features/weather_alerts.py

from tkinter import messagebox

def check_alerts(root, temp: float, high: float, low: float):
    """Popup warnings if temp ≥ high or ≤ low."""
    if temp >= high:
        messagebox.showwarning("Heat Alert", f"{temp:.1f}°C ≥ {high}°C")
    if temp <= low:
        messagebox.showwarning("Cold Alert", f"{temp:.1f}°C ≤ {low}°C")
