# gui.py

import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from features.current_conditions_icons import show_weather_icon

class WeatherGUI:
    def __init__(self, root, api, storage, config):
        self.root     = root
        self.api      = api
        self.storage  = storage
        self.config   = config

        self._build_ui()
        self._load_and_display()

    def _build_ui(self):
        # Window setup
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")
        self.root.configure(bg="#008080")   # teal

        # Top toolbar
        ctrl = tk.Frame(self.root, pady=10, bg="#008080")
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="City:", bg="#008080", fg="white")\
            .pack(side="left", padx=5)
        self.city_var = tk.StringVar(value="New York")
        tk.Entry(ctrl, textvariable=self.city_var, width=20)\
            .pack(side="left")
        tk.Button(ctrl, text="Update", command=self._reload)\
            .pack(side="left", padx=5)

        # Container for sidebar + main content
        container = tk.Frame(self.root, bg="#008080")
        container.pack(fill="both", expand=True)

        # ─── Left sidebar: current conditions ───
        self.current_frame = tk.Frame(
            container, width=120, bg="#008080"
        )
        self.current_frame.pack(
            side="left", fill="y", padx=5, pady=5
        )

        # ─── Right main: forecast + charts ───
        main = tk.Frame(container, bg="#008080")
        main.pack(side="left", fill="both", expand=True)

        # 7-day forecast strip
        self.forecast_frame = tk.Frame(main, pady=5, bg="#008080")
        self.forecast_frame.pack(fill="x")

        # Trend buttons
        btn_frame = tk.Frame(main, bg="#008080")
        btn_frame.pack(pady=5)
        for period in ("Daily", "Weekly", "Monthly"):
            tk.Button(
                btn_frame, text=period,
                command=lambda p=period: self._plot_trend(p)
            ).pack(side="left", padx=5)

        # Chart area (for trends)
        self.chart_frame = tk.Frame(main, bg="#008080")
        self.chart_frame.pack(
            fill="both", expand=True, padx=10, pady=10
        )

    def _reload(self):
        # Clear old
        for w in self.forecast_frame.winfo_children(): w.destroy()
        for w in self.chart_frame.winfo_children(): w.destroy()
        for w in self.current_frame.winfo_children(): w.destroy()
        # Fetch & redraw
        self._load_and_display()

    def _load_and_display(self):
        city = self.city_var.get()
        try:
            # 1) Geocode
            lat, lon = self._geocode(city)

            # 2) Fetch data
            current = self.api.get_current(lat, lon)
            daily   = self.api.get_daily(lat, lon, days=7)

            # 3) Save history (you may extend storage to take temp/desc later)
            today = daily[0]
            ds    = datetime.utcfromtimestamp(today["dt"])\
                         .strftime("%Y-%m-%d")
            precip = today.get("rain", 0.0)
            hum    = today["humidity"]
            # (update your storage.save_daily signature if you add temp/desc)
            self.storage.save_daily(ds, precip, hum)

            # 4) Populate sidebar: current conditions
            # ──────────────────────────────────────────
            # Icon (50×50)
            show_weather_icon(
                self.current_frame,
                current["weather"][0]["icon"],
                size=(50,50)
            )
            # Temp & feels like
            tk.Label(
                self.current_frame,
                text=f"{round(current['temp'])}°F",
                bg="#008080", fg="white",
                font=("Helvetica", 14)
            ).pack(pady=(5,0))
            tk.Label(
                self.current_frame,
                text=f"Feels like {round(current['feels_like'])}°F",
                bg="#008080", fg="white"
            ).pack()
            # Description
            tk.Label(
                self.current_frame,
                text=current["weather"][0]["description"].capitalize(),
                bg="#008080", fg="white"
            ).pack(pady=(5,0))
            # Humidity & UV index
            tk.Label(
                self.current_frame,
                text=f"Humidity: {current['humidity']}%",
                bg="#008080", fg="white"
            ).pack()
            tk.Label(
                self.current_frame,
                text=f"UV Index: {current['uvi']}",
                bg="#008080", fg="white"
            ).pack(pady=(0,5))
            # ──────────────────────────────────────────

            # 5) Draw 7-day forecast & initial trend
            self._show_7day(daily)
            self._plot_trend("Daily")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _geocode(self, city: str):
        url = "http://api.openweathermap.org/geo/1.0/direct"
        r = __import__("requests").get(
            url,
            params={"q": city, "limit": 1, "appid": self.config.api_key},
            timeout=self.config.request_timeout
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            raise ValueError(f"City '{city}' not found")
        return data[0]["lat"], data[0]["lon"]

    def _show_7day(self, daily: list[dict]):
        self.icon_images = []
        for day in daily:
            frm = tk.Frame(self.forecast_frame, padx=10, bg="#008080")
            frm.pack(side="left", expand=True)

            wd = datetime.utcfromtimestamp(day["dt"]).strftime("%a")
            tk.Label(
                frm, text=wd, bg="#008080", fg="white"
            ).pack()

            icon_code = day["weather"][0]["icon"]
            img = __import__("features.current_conditions_icons", 
                             fromlist=["load_icon"]
                            ).load_icon(icon_code, size=(50,50))
            lbl = tk.Label(frm, image=img, bg="#008080")
            lbl.image = img
            lbl.pack()

            temp_f = round(day["temp"]["day"])
            tk.Label(
                frm, text=f"{temp_f}°F", bg="#008080", fg="white"
            ).pack()

            self.icon_images.append(img)

    def _plot_trend(self, period: str):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        for w in self.chart_frame.winfo_children(): w.destroy()

        rows = self.storage.get_history(30)
        dates, precs, hums = zip(*rows)

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
            label = f"W{(i//7)+1}"
            weeks.append((label, sum(chunk_p), sum(chunk_h)/len(chunk_h)))
        ws, ps, hs = zip(*weeks)
        return ws, ps, hs
