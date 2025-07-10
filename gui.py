# gui.py

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from features.current_conditions_icons import show_weather_icon, load_icon
from features.historical_data         import show_history
from features.temperature_graph       import show_temp_chart
from features.weather_alerts          import show_alerts
from features.theme_switcher          import THEMES

class WeatherGUI:
    def __init__(self, root, api, storage, config):
        self.root          = root
        self.api           = api
        self.storage       = storage
        self.config        = config
        self.current_theme = "dark"

        self._build_ui()
        self._apply_theme(self.current_theme)
        self._load_and_display()

    def _build_ui(self):
        # ─── Top toolbar ───
        self.ctrl = tk.Frame(self.root, pady=10)
        self.ctrl.pack(fill="x")

        tk.Label(self.ctrl, text="City:").pack(side="left", padx=5)
        self.city_var = tk.StringVar(value="New York")
        tk.Entry(self.ctrl, textvariable=self.city_var, width=20)\
            .pack(side="left")

        tk.Button(self.ctrl, text="Update", command=self._reload)\
            .pack(side="left", padx=5)

        # New: Toggle Theme button
        tk.Button(self.ctrl, text="Toggle Theme", command=self._toggle_theme)\
            .pack(side="left", padx=5)

        # ─── Main split ───
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Left: current conditions + alerts
        self.current_frame = tk.Frame(self.container, width=140)
        self.current_frame.pack(side="left", fill="y", padx=5, pady=5)

        # Sidebar alert label (persistent)
        self.sidebar_alert = tk.Label(
            self.current_frame,
            text="",
            wraplength=120,
            justify="center"
        )
        self.sidebar_alert.pack(pady=(0,10))

        # Right: forecast + controls + chart
        self.right = tk.Frame(self.container)
        self.right.pack(side="left", fill="both", expand=True)

        # 7-day forecast strip
        self.forecast_frame = tk.Frame(self.right, pady=5)
        self.forecast_frame.pack(fill="x")

        # Buttons row
        self.btn_frame = tk.Frame(self.right, pady=5)
        self.btn_frame.pack(fill="x")
        for label, cmd in [
            ("Daily",      lambda: self._plot_trend("Daily")),
            ("Weekly",     lambda: self._plot_trend("Weekly")),
            ("Monthly",    lambda: self._plot_trend("Monthly")),
            ("History",    self._show_history),
            ("7-Day Temp",  lambda: show_temp_chart(self.chart_frame, self.storage.get_history(30), 7)),
            ("30-Day Temp", lambda: show_temp_chart(self.chart_frame, self.storage.get_history(30), 30)),
        ]:
            tk.Button(self.btn_frame, text=label, command=cmd).pack(side="left", padx=5)

        # Chart/Table area
        self.chart_frame = tk.Frame(self.right, padx=10, pady=10)
        self.chart_frame.pack(fill="both", expand=True)

    def _toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme(new_theme)

    def _apply_theme(self, theme_name):
        """Recolor panels and labels; leave buttons default for readability."""
        th = THEMES[theme_name]
        self.current_theme = theme_name

        # Root background
        self.root.configure(bg=th["bg"])

        # Toolbar
        self.ctrl.configure(bg=th["bg"])
        for w in self.ctrl.winfo_children():
            if isinstance(w, (tk.Label, tk.Entry)):
                w.configure(bg=th["bg"], fg=th["fg"])

        # Container & sidebar
        self.container.configure(bg=th["bg"])
        self.current_frame.configure(bg=th["bg"])
        self.sidebar_alert.configure(bg=th["bg"], fg=th["fg"])
        for w in self.current_frame.winfo_children():
            if isinstance(w, tk.Label) and w is not self.sidebar_alert:
                w.configure(bg=th["bg"], fg=th["fg"])

        # Forecast strip
        self.forecast_frame.configure(bg=th["bg"])
        for w in self.forecast_frame.winfo_children():
            w.configure(bg=th["bg"], fg=th["fg"])

        # Buttons row
        self.btn_frame.configure(bg=th["bg"])
        # Buttons remain default styled so their text stays visible

        # Chart area
        self.chart_frame.configure(bg=th["bg"])
        for w in self.chart_frame.winfo_children():
            if isinstance(w, ttk.Treeview):
                style = ttk.Style()
                style.configure("Treeview", background=th["bg"], foreground=th["fg"])
                w.configure(style="Treeview")

    def _reload(self):
        # Clear forecast, chart, and current‐conditions content (but not sidebar_alert)
        for frame in (self.current_frame, self.forecast_frame, self.chart_frame):
            for w in frame.winfo_children():
                if w is self.sidebar_alert:
                    continue
                w.destroy()

        # Reapply theme to new widgets
        self._apply_theme(self.current_theme)

        # Fetch & redraw
        self._load_and_display()

    def _load_and_display(self):
        city = self.city_var.get()
        try:
            # Geocode & fetch
            lat, lon = self._geocode(city)
            current = self.api.get_current(lat, lon)
            daily   = self.api.get_daily(lat, lon, days=7)
            alerts  = self.api.get_alerts(lat, lon)

            # Show alerts in sidebar
            show_alerts(self.sidebar_alert, alerts, THEMES[self.current_theme])

            # Save history
            today  = daily[0]
            ds     = datetime.utcfromtimestamp(today["dt"]).strftime("%Y-%m-%d")
            precip = today.get("rain", 0.0)
            hum    = today["humidity"]
            temp   = today["temp"]["day"]
            desc   = today["weather"][0]["description"]
            self.storage.save_daily(ds, precip, hum, temp, desc)

            # Sidebar: current conditions
            show_weather_icon(self.current_frame, current["weather"][0]["icon"], size=(50,50))
            tk.Label(self.current_frame, text=f"{round(current['temp'])}°F", font=("Helvetica",14))\
                .pack(pady=(5,0))
            tk.Label(self.current_frame, text=f"Humidity: {current['humidity']}%").pack()
            tk.Label(self.current_frame, text=f"UV Index: {current['uvi']}").pack(pady=(0,5))

            # Forecast + default trend
            self._show_7day(daily)
            self._plot_trend("Daily")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_history(self):
        rows = self.storage.get_history(30)
        show_history(self.chart_frame, rows)

    def _geocode(self, city: str):
        url = "http://api.openweathermap.org/geo/1.0/direct"
        r = requests.get(
            url,
            params={"q": city, "limit": 1, "appid": self.config.api_key},
            timeout=self.config.request_timeout
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            raise ValueError(f"City '{city}' not found")
        return data[0]["lat"], data[0]["lon"]

    def _show_7day(self, daily):
        self.icon_images = []
        for day in daily:
            frm = tk.Frame(self.forecast_frame, padx=10)
            frm.pack(side="left", expand=True)
            wd = datetime.utcfromtimestamp(day["dt"]).strftime("%a")
            tk.Label(frm, text=wd).pack()
            img = load_icon(day["weather"][0]["icon"], size=(50,50))
            lbl = tk.Label(frm, image=img)
            lbl.image = img
            lbl.pack()
            tk.Label(frm, text=f"{round(day['temp']['day'])}°F").pack()
            self.icon_images.append(img)

    def _plot_trend(self, period: str):
        for w in self.chart_frame.winfo_children():
            w.destroy()
        rows = self.storage.get_history(30)
        dates, precs, hums, *_ = zip(*rows)
        if period == "Weekly":
            dates, precs, hums = self._aggregate_weekly(dates, precs, hums)
        elif period == "Daily":
            dates, precs, hums = dates[-7:], precs[-7:], hums[-7:]
        fig, ax1 = plt.subplots(figsize=(8,3))
        ax2 = ax1.twinx()
        ax1.bar(dates, precs, alpha=0.6, label="Precip (mm)")
        ax2.plot(dates, hums, "-o", label="Humidity (%)")
        ax1.set_ylabel("Precip (mm)")
        ax2.set_ylabel("Humidity (%)")
        ax1.set_title(f"{period} Precip vs Humidity")
        fig.autofmt_xdate(rotation=45)
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1+h2, l1+l2, loc="upper left")
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def _aggregate_weekly(self, dates, precs, hums):
        weeks = []
        for i in range(0, len(dates), 7):
            chunk_p = precs[i:i+7]
            chunk_h = hums[i:i+7]
            label   = f"W{(i//7)+1}"
            weeks.append((label, sum(chunk_p), sum(chunk_h)/len(chunk_h)))
        ws, ps, hs = zip(*weeks)
        return ws, ps, hs
