import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import io
import requests
import threading
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherDashboard(tk.Tk):
    def __init__(self, weather_api, predictor):
        super().__init__()
        self.weather_api = weather_api
        self.predictor = predictor

        self.themes = {
            'light': {
                'bg': '#d8b4f8',
                'fg': '#000000',
                'sidebar_bg': '#c084fc',
                'btn_bg': '#e9d5ff',
                'btn_fg': '#000000',
                'chart_bg': '#f5f0ff',
                'alert_bg': '#ffcccc'
            },
            'dark': {
                'bg': '#5a189a',
                'fg': '#ffffff',
                'sidebar_bg': '#3c096c',
                'btn_bg': '#7b2cbf',
                'btn_fg': '#ffffff',
                'chart_bg': '#2d004b',
                'alert_bg': '#660000'
            }
        }
        self.current_theme = 'light'

        self.title("Weather Dashboard")
        self.geometry("1000x700")
        self._setup_ui()
        self._set_initial_state()

    def _setup_ui(self):
        self.main_frame = tk.Frame(self, bg=self.themes[self.current_theme]['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.main_frame, bg=self.themes[self.current_theme]['sidebar_bg'], width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.content = tk.Frame(self.main_frame, bg=self.themes[self.current_theme]['bg'])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self):
        theme = self.themes[self.current_theme]

        self.weather_icon = tk.Label(self.sidebar, bg=theme['sidebar_bg'])
        self.weather_icon.pack(pady=20)

        self.current_temp = tk.Label(self.sidebar, text="--°F", font=('Helvetica', 24),
                                     bg=theme['sidebar_bg'], fg=theme['fg'])
        self.current_temp.pack()

        self.humidity_label = tk.Label(self.sidebar, text="Humidity: --%",
                                       bg=theme['sidebar_bg'], fg=theme['fg'])
        self.humidity_label.pack()

        self.uv_label = tk.Label(self.sidebar, text="UV Index: --",
                                 bg=theme['sidebar_bg'], fg=theme['fg'])
        self.uv_label.pack(pady=(0, 20))

        self.alert_label = tk.Label(self.sidebar, text="No alerts", wraplength=230, justify=tk.LEFT,
                                    bg=theme['alert_bg'], fg=theme['fg'])
        self.alert_label.pack(fill=tk.X, padx=5, pady=5)

        self.city_entry = tk.Entry(self.sidebar)
        self.city_entry.pack(pady=10, padx=10, fill=tk.X)

        self.update_btn = tk.Button(self.sidebar, text="Update Weather",
                                    command=self._update_weather,
                                    bg=theme['btn_bg'], fg=theme['btn_fg'])
        self.update_btn.pack(pady=5, fill=tk.X)

        self.theme_btn = tk.Button(self.sidebar, text="Toggle Theme",
                                   command=self._toggle_theme,
                                   bg=theme['btn_bg'], fg=theme['btn_fg'])
        self.theme_btn.pack(pady=5, fill=tk.X)

    def _build_content(self):
        theme = self.themes[self.current_theme]
        self.forecast_frame = tk.Frame(self.content, bg=theme['bg'])
        self.forecast_frame.pack(fill=tk.X, padx=10, pady=10)

        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor=theme['chart_bg'])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(theme['chart_bg'])

        self.chart = FigureCanvasTkAgg(self.figure, master=self.content)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _update_theme_colors(self):
        theme = self.themes[self.current_theme]
        self.main_frame.config(bg=theme['bg'])
        self.sidebar.config(bg=theme['sidebar_bg'])
        self.content.config(bg=theme['bg'])

        widgets = [
            self.current_temp, self.humidity_label, self.uv_label,
            self.alert_label, self.update_btn, self.theme_btn
        ]

        for widget in widgets:
            if widget == self.alert_label:
                widget.config(bg=theme['alert_bg'], fg=theme['fg'])
            elif isinstance(widget, tk.Label):
                widget.config(bg=theme['sidebar_bg'], fg=theme['fg'])
            elif isinstance(widget, tk.Button):
                widget.config(bg=theme['btn_bg'], fg=theme['btn_fg'])

        self.figure.set_facecolor(theme['chart_bg'])
        self.ax.set_facecolor(theme['chart_bg'])

        if hasattr(self, 'forecast_data'):
            self._update_chart(self.forecast_data)
        self.chart.draw()

    def _toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self._update_theme_colors()

    def _update_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return
        self.alert_label.config(text="Loading...", fg='blue')
        threading.Thread(target=self._fetch_weather_data, args=(city,), daemon=True).start()

    def _fetch_weather_data(self, city: str):
        try:
            lat, lon = self.weather_api.geocode(city)
            forecast_data = self.weather_api.get_forecast_bundle(lat, lon)
            current_data = forecast_data['current']
            self.after(0, lambda: self._update_display(current_data, forecast_data))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _update_display(self, current_data: Dict, forecast_data: Dict):
        self.current_data = current_data
        self.forecast_data = forecast_data

        self.current_temp.config(text=f"{current_data['temp']}°F")
        self.humidity_label.config(text=f"Humidity: {current_data['humidity']}%")
        self.uv_label.config(text=f"UV Index: {current_data.get('uvi', 'N/A')}")
        self._update_weather_icon(current_data['weather'][0]['icon'])

        alerts = forecast_data.get('alerts', [])
        if alerts:
            alert_text = "\n".join(f"{a['event']}: {a['description'][:100]}..." for a in alerts)
            self.alert_label.config(text=alert_text, fg='red')
        else:
            self.alert_label.config(text="No weather alerts", fg=self.themes[self.current_theme]['fg'])

        self._update_forecast(forecast_data)
        self._update_chart(forecast_data)

    def _update_weather_icon(self, icon_code: str):
        try:
            url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
            response = requests.get(url, stream=True)
            image_data = Image.open(io.BytesIO(response.content))
            image = ImageTk.PhotoImage(image_data)
            self.weather_icon.config(image=image)
            self.weather_icon.image = image
        except Exception as e:
            logger.error(f"Failed to load weather icon: {str(e)}")

    def _update_forecast(self, forecast_data: Dict):
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            self.forecast_frame,
            text="5-Day Forecast",
            font=('Helvetica', 14, 'bold'),
            bg=self.themes[self.current_theme]['bg'],
            fg=self.themes[self.current_theme]['fg']
        )
        title.pack(pady=(0, 10))

        for day in forecast_data['daily'][:5]:
            day_frame = tk.Frame(self.forecast_frame, bg=self.themes[self.current_theme]['bg'])
            day_frame.pack(side=tk.LEFT, padx=5, pady=5)

            date = datetime.fromtimestamp(day['dt']).strftime('%a %m/%d')
            tk.Label(day_frame, text=date, bg=self.themes[self.current_theme]['bg'],
                     fg=self.themes[self.current_theme]['fg']).pack()

            icon_code = day['weather'][0]['icon']
            try:
                url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                response = requests.get(url, stream=True)
                image_data = Image.open(io.BytesIO(response.content)).resize((50, 50))
                image = ImageTk.PhotoImage(image_data)
                icon_label = tk.Label(day_frame, image=image, bg=self.themes[self.current_theme]['bg'])
                icon_label.image = image
                icon_label.pack()
            except:
                pass

            temp = day['temp']
            tk.Label(day_frame, text=f"{temp['day']:.0f}° / {temp['night']:.0f}°",
                     bg=self.themes[self.current_theme]['bg'],
                     fg=self.themes[self.current_theme]['fg']).pack()

    def _update_chart(self, forecast_data: Dict):
        try:
            self.ax.clear()
            dates = [datetime.fromtimestamp(day['dt']) for day in forecast_data['daily']]
            temps = [day['temp']['day'] for day in forecast_data['daily']]
            day_nums = list(range(len(dates)))
            predictions = self.predictor.predict(day_nums)

            self.ax.plot(dates, temps, 'o-', label='Actual Temp')

            if predictions and len(predictions) == len(dates):
                self.ax.plot(dates, predictions, 's--', label='ML Prediction')

            theme = self.themes[self.current_theme]
            self.ax.set_title("7-Day Temperature Forecast", color=theme['fg'])
            self.ax.set_ylabel("Temperature (°F)", color=theme['fg'])
            self.ax.legend()
            self.ax.tick_params(colors=theme['fg'])
            for spine in self.ax.spines.values():
                spine.set_color(theme['fg'])

            self.figure.autofmt_xdate()
            self.chart.draw()
        except Exception as e:
            logger.error(f"Failed to update chart: {str(e)}")

    def _set_initial_state(self):
        self._update_theme_colors()


def launch_gui(weather_api, predictor):
    try:
        app = WeatherDashboard(weather_api, predictor)
        app.mainloop()
    except Exception as e:
        logger.error(f"Failed to launch GUI: {str(e)}")
        raise
