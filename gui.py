# gui.py

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from features.current_conditions_icons import show_weather_icon
from features.theme_switcher         import ThemeSwitcher
from features.weather_alerts         import check_alerts
from features.historical_data        import show_history
from features.temperature_graph      import embed_temperature_graph

class WeatherDashboard:
    def __init__(self, root, cfg, storage, api):
        self.root    = root
        self.cfg     = cfg
        self.storage = storage
        self.api     = api

        # Window setup
        self.root.title("🌦️ Weather Dashboard")
        self.root.geometry("960x720")
        self.root.configure(bg="#f0f4f7")

        # State variables
        self.city_var         = tk.StringVar()
        self.date_range_var   = tk.StringVar(value="7 days")
        self.temperature_unit = tk.StringVar(value="F")
        self.show_humidity    = tk.BooleanVar(value=True)

        # Build UI
        self.create_widgets()

    def create_widgets(self):
        # Title
        ttk.Label(
            self.root,
            text="☁️ Weather Dashboard",
            font=("Helvetica", 20, "bold"),
            background=self.root["bg"]
        ).grid(row=0, column=0, columnspan=4, pady=10)

        # Controls frame
        ctrl = ttk.LabelFrame(self.root, text="Controls", padding=10)
        ctrl.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctrl.columnconfigure(1, weight=1)

        ttk.Label(ctrl, text="City:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(ctrl, textvariable=self.city_var).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(ctrl, text="Date Range:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(
            ctrl,
            textvariable=self.date_range_var,
            values=["7 days", "14 days", "30 days"],
            state="readonly"
        ).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(ctrl, text="Units:").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(ctrl, text="°F", variable=self.temperature_unit, value="F")\
            .grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(ctrl, text="°C", variable=self.temperature_unit, value="C")\
            .grid(row=2, column=2, sticky="w")

        ttk.Checkbutton(
            ctrl,
            text="Show Humidity",
            variable=self.show_humidity
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        ttk.Button(ctrl, text="🔄 Update", command=self.on_update_clicked)\
            .grid(row=4, column=0, sticky="ew", pady=10)
        ttk.Button(ctrl, text="🧹 Clear", command=self.on_clear_clicked)\
            .grid(row=4, column=1, sticky="ew", pady=10)
        ttk.Button(ctrl, text="💾 Save", command=self.on_save_clicked)\
            .grid(row=4, column=2, sticky="ew", pady=10)

        # Theme toggle
        self.theme = ThemeSwitcher(self.root)
        self.theme.button.grid(row=1, column=3, padx=10, pady=10, sticky="ne")

        # Current weather display
        disp = ttk.LabelFrame(self.root, text="Current Weather", padding=10)
        disp.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")
        disp.columnconfigure(1, weight=1)

        ttk.Label(disp, text="Location:").grid(row=0, column=0, sticky="w", pady=2)
        self.location_label = ttk.Label(disp, text="--")
        self.location_label.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(disp, text="Temperature:").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_label = ttk.Label(disp, text="--")
        self.temp_label.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(disp, text="Humidity:").grid(row=2, column=0, sticky="w", pady=2)
        self.hum_label = ttk.Label(disp, text="--")
        self.hum_label.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(disp, text="Conditions:").grid(row=3, column=0, sticky="w", pady=2)
        self.cond_label = ttk.Label(disp, text="--")
        self.cond_label.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Label(disp, text="Precipitation:").grid(row=4, column=0, sticky="w", pady=2)
        self.precip_label = ttk.Label(disp, text="--")
        self.precip_label.grid(row=4, column=1, sticky="w", pady=2)

        # Icon container
        self.icon_container = tk.Frame(disp)
        self.icon_container.grid(row=5, column=0, columnspan=2, pady=5)

        # Chart and history frame
        viz = ttk.LabelFrame(self.root, text="📊 Weather Trends", padding=10)
        viz.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        viz.columnconfigure(0, weight=1)
        viz.rowconfigure(1, weight=1)

        # History table
        self.history_frame = ttk.Frame(viz)
        self.history_frame.grid(row=0, column=0, sticky="nsew", pady=(0,10))

        # Chart canvas
        self.figure = Figure(figsize=(8,4), dpi=100)
        self.ax     = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, viz)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        # Layout weights on root
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

    def on_update_clicked(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city.")
            return
        threading.Thread(target=self._fetch_and_update, args=(city,), daemon=True).start()

    def on_save_clicked(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city before saving.")
            return
        # Gather history for this city and date range
        history = self.storage.get_last_n(30)
        recs = [r for r in history if r["city"].lower() == city.lower()]
        if not recs:
            messagebox.showinfo("No Data", f"No history to save for '{city}'.")
            return
        start, end = self.get_date_range()
        plot_data = [
            r for r in recs
            if start <= datetime.fromisoformat(r["timestamp"]) <= end
        ]
        # Prompt for filename
        fname = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not fname:
            return
        try:
            with open(fname, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        'timestamp','city','country','temperature',
                        'humidity','description','precipitation'
                    ]
                )
                writer.writeheader()
                for row in plot_data:
                    writer.writerow(row)
            messagebox.showinfo("Saved", f"History saved to {fname}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def _fetch_and_update(self, city):
        try:
            raw = self.api.fetch_current(city)
            parsed = {
                "timestamp": datetime.now().isoformat(),
                "city":          raw["name"],
                "country":       raw["sys"]["country"],
                "temperature":   raw["main"]["temp"],
                "humidity":      raw["main"]["humidity"],
                "description":   raw["weather"][0]["description"],
                "icon":          raw["weather"][0]["icon"],
                "precipitation": raw.get("rain", {}).get("1h", 0.0)
            }
            # Alerts
            check_alerts(
                self.root,
                parsed["temperature"],
                self.cfg.alert_threshold_high,
                self.cfg.alert_threshold_low
            )

            # Store & refresh display
            self.storage.add_entry(parsed)
            self.root.after(0, self.update_display)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Fetch Error", f"Could not fetch weather for '{city}'.\n{e}"))

    def on_clear_clicked(self):
        self.city_var.set("")

