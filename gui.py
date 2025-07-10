import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherGUI:
    def __init__(self, root, api, storage, config):
        self.root = root
        self.api = api
        self.storage = storage
        self.config = config
        self.icon_images = []
        self._build_ui()
        self._load_and_display()

    def _build_ui(self):
        # Window settings
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")
        # Set teal background for entire window
        self.root.configure(bg="#008080")

        # Optional overlay background image
        try:
            bg_img = Image.open("bg.png").resize((900,600))
            self._bg_photo = ImageTk.PhotoImage(bg_img)
            lbl = tk.Label(self.root, image=self._bg_photo)
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            pass  # Use teal background when no image

        # Top control bar
        ctrl = tk.Frame(self.root, bg="#008080", pady=10)
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="City:", bg="#008080", fg="white").pack(side="left", padx=5)
        self.city_var = tk.StringVar(value="New York")
        tk.Entry(ctrl, textvariable=self.city_var, width=20).pack(side="left", padx=5)
        tk.Button(ctrl, text="Update", command=self._reload).pack(side="left", padx=5)

        # 7-day forecast frame
        self.forecast_frame = tk.Frame(self.root, bg="#008080", pady=5)
        self.forecast_frame.pack(fill="x")

        # Trend selection buttons
        btn_frame = tk.Frame(self.root, bg="#008080")
        btn_frame.pack(pady=5)
        for period in ("Daily", "Weekly", "Monthly"):
            tk.Button(
                btn_frame,
                text=period,
                command=lambda p=period: self._plot_trend(p)
            ).pack(side="left", padx=5)

        # Chart display area
        self.chart_frame = tk.Frame(self.root, bg="#008080")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _reload(self):
        # Clear existing forecast and charts
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self._load_and_display()

    def _load_and_display(self):
        city = self.city_var.get()
        try:
            lat, lon = self._geocode(city)
            daily = self.api.get_daily(lat, lon, days=7)

            # Save today's data
            today = daily[0]
            date_str = datetime.utcfromtimestamp(today["dt"]).strftime("%Y-%m-%d")
            precip = today.get("rain", 0.0)
            humidity = today["humidity"]
            self.storage.save_daily(date_str, precip, humidity)

            # Display forecast and initial trend
            self._show_7day(daily)
            self._plot_trend("Daily")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _geocode(self, city: str) -> tuple[float, float]:
        url = "http://api.openweathermap.org/geo/1.0/direct"
        response = requests.get(
            url,
            params={"q": city, "limit": 1, "appid": self.config.api_key},
            timeout=self.config.request_timeout
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"City '{city}' not found")
        return data[0]["lat"], data[0]["lon"]

    def _show_7day(self, daily: list[dict]):
        self.icon_images.clear()
        for day in daily:
            frame = tk.Frame(self.forecast_frame, bg="#008080", padx=10)
            frame.pack(side="left", expand=True)
            wd = datetime.utcfromtimestamp(day["dt"]).strftime("%a")
            tk.Label(frame, text=wd, bg="#008080", fg="white").pack()
            icon_code = day["weather"][0]["icon"]
            icon_img = self._fetch_icon(icon_code)
            lbl = tk.Label(frame, image=icon_img, bg="#008080")
            lbl.image = icon_img
            lbl.pack()
            temp = round(day["temp"]["day"])
            tk.Label(frame, text=f"{temp}°C", bg="#008080", fg="white").pack()
            self.icon_images.append(icon_img)

    def _fetch_icon(self, code: str) -> ImageTk.PhotoImage:
        url = f"http://openweathermap.org/img/wn/{code}@2x.png"
        response = requests.get(url, timeout=self.config.request_timeout)
        img = Image.open(BytesIO(response.content)).resize((50, 50))
        return ImageTk.PhotoImage(img)

    def _plot_trend(self, period: str):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        rows = self.storage.get_history(30)
        dates, precs, hums = zip(*rows)

        if period == "Weekly":
            dates, precs, hums = self._aggregate_weekly(dates, precs, hums)
        elif period == "Daily":
            dates, precs, hums = dates[-7:], precs[-7:], hums[-7:]

        fig, ax1 = plt.subplots(figsize=(8, 3))
        ax2 = ax1.twinx()
        ax1.bar(dates, precs, alpha=0.6, label="Precip (mm)")
        ax2.plot(dates, hums, "-o", label="Humidity (%)")
        ax1.set_ylabel("Precip (mm)")
        ax2.set_ylabel("Humidity (%)")
        ax1.set_title(f"{period} Precip vs Humidity")
        fig.autofmt_xdate(rotation=45)

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc="upper left")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def _aggregate_weekly(self, dates, precs, hums):
        weeks = []
        for i in range(0, len(dates), 7):
            chunk_p = precs[i:i+7]
            chunk_h = hums[i:i+7]
            label = f"W{(i // 7) + 1}"
            weeks.append((label, sum(chunk_p), sum(chunk_h) / len(chunk_h)))
        ws, ps, hs = zip(*weeks)
        return ws, ps, hs
