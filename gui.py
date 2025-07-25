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
from typing import Dict, List, Optional

from preferences import load_preferences, save_preferences  # ==== NEW/UPDATED ==== #

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TEXTS = {  # ==== NEW/UPDATED ==== #
    "en": {
        "title": "Weather Dashboard",
        "update_weather": "Update Weather",
        "toggle_theme": "Toggle Theme",
        "settings": "Settings",
        "no_alerts": "No weather alerts",
        "alerts_loading": "Loading...",
        "input_error": "Please enter a city name",
        "input_error_title": "Input Error",
        "error_title": "Error",
        "no_data": "Please update a city first.",
        "no_data_title": "No data",
        "forecast_title": "5-Day Forecast",
        "chart_title": "7-Day Temperature Forecast",
        "temperature_label": "Temperature ({unit})",
    },
    "es": {
        "title": "Panel del Clima",
        "update_weather": "Actualizar Clima",
        "toggle_theme": "Cambiar Tema",
        "settings": "Configuraciones",
        "no_alerts": "Sin alertas meteorológicas",
        "alerts_loading": "Cargando...",
        "input_error": "Por favor, ingresa una ciudad",
        "input_error_title": "Error de entrada",
        "error_title": "Error",
        "no_data": "Actualiza una ciudad primero.",
        "no_data_title": "Sin datos",
        "forecast_title": "Pronóstico de 5 Días",
        "chart_title": "Pronóstico de Temperatura de 7 Días",
        "temperature_label": "Temperatura ({unit})",
    }
}


class WeatherDashboard(tk.Tk):
    def __init__(self, weather_api, predictor):
        super().__init__()
        self.weather_api = weather_api
        self.predictor = predictor

        # ==== NEW/UPDATED ==== #
        self.preferences = load_preferences()
        self.language = self.preferences["language"]
        self.current_theme = self.preferences["theme"]["mode"]
        self.default_city = self.preferences["location"]["default_city"]
        self.temp_unit = self.preferences["units"]["temperature"]  # "imperial"/"metric"
        self.chart_default_type = self.preferences["chart"]["default_type"]

        self.themes = {
            'light': {
                'bg': '#d8b4f8',
                'fg': '#000000',
                'sidebar_bg': '#c084fc',
                'btn_bg': '#e9d5ff',
                'btn_fg': '#000000',
                'chart_bg': '#ffffff',
                'alert_bg': '#ffcccc'
            },
            'dark': {
                'bg': '#3b0a4e',
                'fg': '#ffffff',
                'sidebar_bg': '#4b0d5f',
                'btn_bg': '#c084fc',
                'btn_fg': '#000000',
                'chart_bg': '#ffffff',
                'alert_bg': '#660000'
            }
        }

        self.title(TEXTS[self.language]["title"])
        self.geometry("1000x700")
        self._setup_ui()
        self._set_initial_state()

        # ==== NEW/UPDATED (optional auto-refresh) ==== #
        interval = self.preferences["refresh"]["interval_seconds"]
        if interval and interval > 0:
            self.after(interval * 1000, self._auto_refresh)

    # ==== NEW/UPDATED ==== #
    def _auto_refresh(self):
        """Auto refresh using default city if none typed, based on prefs interval."""
        try:
            city = self.city_entry.get().strip() or self.default_city
            if city:
                self._trigger_update_weather(city)
        finally:
            interval = self.preferences["refresh"]["interval_seconds"]
            if interval and interval > 0:
                self.after(interval * 1000, self._auto_refresh)

    def _setup_ui(self):
        # Main layout
        self.main_frame = tk.Frame(self, bg=self.themes[self.current_theme]['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(
            self.main_frame,
            bg=self.themes[self.current_theme]['sidebar_bg'],
            width=250
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.content = tk.Frame(
            self.main_frame,
            bg=self.themes[self.current_theme]['bg']
        )
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self):
        theme = self.themes[self.current_theme]
        t = TEXTS[self.language]

        self.weather_icon = tk.Label(self.sidebar, bg=theme['sidebar_bg'])
        self.weather_icon.pack(pady=20)

        # will be updated later with unit symbol
        self.current_temp = tk.Label(
            self.sidebar, text="--°", font=('Helvetica', 24),
            bg=theme['sidebar_bg'], fg=theme['fg']
        )
        self.current_temp.pack()

        self.humidity_label = tk.Label(
            self.sidebar, text="Humidity: --%",
            bg=theme['sidebar_bg'], fg=theme['fg']
        )
        self.humidity_label.pack()

        self.uv_label = tk.Label(
            self.sidebar, text="UV Index: --",
            bg=theme['sidebar_bg'], fg=theme['fg']
        )
        self.uv_label.pack(pady=(0, 20))

        self.alert_label = tk.Label(
            self.sidebar, text=t["no_alerts"], wraplength=230, justify=tk.LEFT,
            anchor='nw', height=10, padx=5, pady=5,
            bg=theme['alert_bg'], fg=theme['fg']
        )
        self.alert_label.pack(fill=tk.X, padx=5, pady=5)

        self.city_entry = tk.Entry(self.sidebar)
        self.city_entry.pack(pady=10, padx=10, fill=tk.X)
        self.city_entry.insert(0, self.default_city)  # ==== NEW/UPDATED ==== #

        self.update_btn = tk.Button(
            self.sidebar, text=t["update_weather"],
            command=self._update_weather,
            bg=theme['btn_bg'], fg=theme['btn_fg']
        )
        self.update_btn.pack(pady=5, fill=tk.X)

        self.theme_btn = tk.Button(
            self.sidebar, text=t["toggle_theme"],
            command=self._toggle_theme,
            bg=theme['btn_bg'], fg=theme['btn_fg']
        )
        self.theme_btn.pack(pady=5, fill=tk.X)

        # ==== NEW/UPDATED (Settings button) ==== #
        self.settings_btn = tk.Button(
            self.sidebar, text=t["settings"],
            command=self.open_settings_window,
            bg=theme['btn_bg'], fg=theme['btn_fg']
        )
        self.settings_btn.pack(pady=5, fill=tk.X)

    def _build_content(self):
        theme = self.themes[self.current_theme]
        t = TEXTS[self.language]

        # Forecast icons with title
        self.forecast_frame = tk.Frame(self.content, bg=theme['bg'])
        self.forecast_frame.pack(fill=tk.X, padx=10, pady=10)
        self.forecast_title_label = tk.Label(
            self.forecast_frame,
            text=t["forecast_title"],
            font=('Helvetica', 14, 'bold'),
            bg=theme['bg'], fg=theme['fg']
        )
        self.forecast_title_label.pack(pady=(0,5))

        # Mode buttons for chart view
        self.mode_frame = tk.Frame(self.content, bg=theme['bg'])
        self.mode_frame.pack(fill=tk.X, padx=10)
        for mode in ['Daily', 'Weekly', 'Monthly', '7-Day Temp', '30-Day Temp']:
            btn = tk.Button(
                self.mode_frame, text=mode,
                command=lambda m=mode: self.on_mode(m),
                bg=theme['btn_bg'], fg=theme['btn_fg'],
                activebackground=theme['bg'], highlightbackground=theme['btn_bg']
            )
            btn.pack(side=tk.LEFT, padx=4)

        # Chart area
        self.figure = Figure(
            figsize=(8, 4), dpi=100, facecolor=theme['chart_bg']
        )
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(theme['chart_bg'])

        self.chart = FigureCanvasTkAgg(self.figure, master=self.content)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _apply_language(self):  # ==== NEW/UPDATED ==== #
        t = TEXTS[self.language]
        self.title(t["title"])
        self.update_btn.config(text=t["update_weather"])
        self.theme_btn.config(text=t["toggle_theme"])
        self.settings_btn.config(text=t["settings"])
        # If no alerts currently
        if not getattr(self, "forecast_data", None) or not self.forecast_data.get('alerts'):
            self.alert_label.config(text=t["no_alerts"])
        self.forecast_title_label.config(text=t["forecast_title"])

    def _update_theme_colors(self):
        theme = self.themes[self.current_theme]
        self.main_frame.config(bg=theme['bg'])
        self.sidebar.config(bg=theme['sidebar_bg'])
        self.content.config(bg=theme['bg'])

        for widget in [
            self.current_temp, self.humidity_label, self.uv_label,
            self.alert_label, self.update_btn, self.theme_btn, self.settings_btn
        ]:
            if widget == self.alert_label:
                widget.config(bg=theme['alert_bg'], fg=theme['fg'])
            elif isinstance(widget, tk.Label):
                # current_temp/humidity/uv are in sidebar
                widget.config(bg=theme['sidebar_bg'], fg=theme['fg'])
            elif isinstance(widget, tk.Button):
                widget.config(bg=theme['btn_bg'], fg=theme['btn_fg'])

        # forecast frame labels
        for child in self.forecast_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=theme['bg'], fg=theme['fg'])

        # mode buttons
        for child in self.mode_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(bg=theme['btn_bg'], fg=theme['btn_fg'],
                             activebackground=theme['bg'], highlightbackground=theme['btn_bg'])

        # chart
        self.figure.set_facecolor(theme['chart_bg'])
        self.ax.set_facecolor(theme['chart_bg'])
        self.chart.draw()

    def _toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.preferences["theme"]["mode"] = self.current_theme  # persist
        save_preferences(self.preferences)
        self._update_theme_colors()

    def _update_weather(self):
        t = TEXTS[self.language]
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning(t["input_error_title"], t["input_error"])
            return
        self._trigger_update_weather(city)

    def _trigger_update_weather(self, city: str):  # ==== NEW/UPDATED (extracted) ==== #
        t = TEXTS[self.language]
        self.alert_label.config(text=t["alerts_loading"], fg='blue')
        threading.Thread(
            target=self._fetch_weather_data,
            args=(city,), daemon=True
        ).start()

    def _fetch_weather_data(self, city: str):
        try:
            lat, lon = self.weather_api.geocode(city)

            # If your weather_api supports units, pass them. If not, it will ignore.
            try:
                forecast_data = self.weather_api.get_forecast_bundle(lat, lon, units=self.temp_unit)
            except TypeError:
                forecast_data = self.weather_api.get_forecast_bundle(lat, lon)

            current_data = forecast_data['current']
            self.after(0, lambda: self._update_display(current_data, forecast_data))
        except Exception as e:
            t = TEXTS[self.language]
            self.after(0, lambda msg=str(e): messagebox.showerror(t["error_title"], msg))

    def _format_temp(self, value: float) -> str:  # ==== NEW/UPDATED ==== #
        unit_symbol = "°F" if self.temp_unit == "imperial" else "°C"
        return f"{value:.0f}{unit_symbol}"

    def _update_display(self, current_data: Dict, forecast_data: Dict):
        self.current_data = current_data
        self.forecast_data = forecast_data

        # Update sidebar
        temp = current_data['temp']
        # (Assume API already returns the correct units according to self.temp_unit)
        self.current_temp.config(text=self._format_temp(temp))
        self.humidity_label.config(text=f"Humidity: {current_data['humidity']}%")
        self.uv_label.config(text=f"UV Index: {current_data.get('uvi', 'N/A')}")
        self._update_weather_icon(current_data['weather'][0]['icon'])

        # Alerts
        alerts = forecast_data.get('alerts', [])
        t = TEXTS[self.language]
        if alerts:
            text = "\n".join(f"{a['event']}: {a['description'][:100]}..." for a in alerts)
            self.alert_label.config(text=text, fg='red')
        else:
            self.alert_label.config(text=t["no_alerts"], fg=self.themes[self.current_theme]['fg'])

        # Forecast icons and chart
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
        # Clear existing forecast widgets (keep the title label)
        for widget in self.forecast_frame.winfo_children():
            if widget is not self.forecast_title_label and isinstance(widget, tk.Frame):
                widget.destroy()

        # Render up to 5 days
        for day in forecast_data.get('daily', [])[:5]:
            day_frame = tk.Frame(self.forecast_frame, bg=self.themes[self.current_theme]['bg'])
            day_frame.pack(side=tk.LEFT, padx=5, pady=5)

            # format date (24h flag doesn't matter for daily)
            date_str = datetime.fromtimestamp(day['dt']).strftime('%a %m/%d')
            tk.Label(
                day_frame, text=date_str,
                bg=self.themes[self.current_theme]['bg'],
                fg=self.themes[self.current_theme]['fg']
            ).pack()

            try:
                icon_code = day['weather'][0]['icon']
                url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                resp = requests.get(url, stream=True)
                img_data = Image.open(io.BytesIO(resp.content)).resize((50, 50))
                photo = ImageTk.PhotoImage(img_data)
                icon_label = tk.Label(day_frame, image=photo, bg=self.themes[self.current_theme]['bg'])
                icon_label.image = photo
                icon_label.pack()
            except Exception as e:
                logger.error(f"Failed to load forecast icon: {str(e)}")

            temp = day.get('temp', {})
            day_temp = temp.get('day', 0) if isinstance(temp, dict) else temp
            night_temp = temp.get('night', day_temp) if isinstance(temp, dict) else day_temp
            tk.Label(
                day_frame, text=f"{self._format_temp(day_temp)} / {self._format_temp(night_temp)}",
                bg=self.themes[self.current_theme]['bg'],
                fg=self.themes[self.current_theme]['fg']
            ).pack(pady=(2,0))

    def _update_chart(self, forecast_data: Dict):
        try:
            self.ax.clear()
            dates = [datetime.fromtimestamp(d['dt']) for d in forecast_data.get('daily', [])]
            temps = [d['temp']['day'] for d in forecast_data.get('daily', [])]
            preds = self.predictor.predict(list(range(len(dates)))) if self.predictor else []

            # Choose default chart type - for simplicity only affects the temp series
            chart_type = self.chart_default_type  # "line", "bar", "scatter"

            if chart_type == "bar":
                self.ax.bar(dates, temps, label='Actual Temp')
            elif chart_type == "scatter":
                self.ax.scatter(dates, temps, label='Actual Temp')
            else:
                self.ax.plot(dates, temps, 'o-', label='Actual Temp')

            if preds and len(preds) == len(dates):
                self.ax.plot(dates, preds, 's--', label='Prediction')

            theme = self.themes[self.current_theme]
            t = TEXTS[self.language]
            unit_symbol = "°F" if self.temp_unit == "imperial" else "°C"

            self.ax.set_title(t["chart_title"], color=theme['fg'])
            self.ax.set_ylabel(t["temperature_label"].format(unit=unit_symbol), color=theme['fg'])
            self.ax.legend()
            self.ax.tick_params(colors=theme['fg'])
            for spine in self.ax.spines.values():
                spine.set_color(theme['fg'])

            self.figure.autofmt_xdate()
            self.chart.draw()
        except Exception as e:
            logger.error(f"Failed to update chart: {str(e)}")

    def on_mode(self, mode: str):
        t = TEXTS[self.language]
        if not hasattr(self, 'forecast_data'):
            messagebox.showwarning(t["no_data_title"], t["no_data"])
            return
        days_map = {'Daily': 1, 'Weekly': 7, '7-Day Temp': 7, 'Monthly': 30, '30-Day Temp': 30}
        days = days_map.get(mode, 7)
        series = self.forecast_data.get('daily', [])[:days]
        self._update_chart({'daily': series})

    def _set_initial_state(self):
        self._apply_language()      # ==== NEW/UPDATED ==== #
        self._update_theme_colors()
        # Optionally auto-load default city on start:
        if self.default_city:
            self._trigger_update_weather(self.default_city)

    # ==== NEW/UPDATED (Settings Window) ==== #
    def open_settings_window(self):
        win = tk.Toplevel(self)
        win.title(TEXTS[self.language]["settings"])
        win.geometry("400x400")

        theme = self.themes[self.current_theme]

        # Helpers
        def labeled_row(parent, label_text):
            frame = tk.Frame(parent, bg=theme['bg'])
            frame.pack(fill=tk.X, padx=10, pady=4)
            lbl = tk.Label(frame, text=label_text, bg=theme['bg'], fg=theme['fg'])
            lbl.pack(side=tk.LEFT)
            return frame

        # Language
        lang_frame = labeled_row(win, "Language")
        lang_var = tk.StringVar(value=self.preferences["language"])
        tk.OptionMenu(lang_frame, lang_var, "en", "es").pack(side=tk.RIGHT)

        # Theme
        theme_frame = labeled_row(win, "Theme Mode")
        theme_var = tk.StringVar(value=self.preferences["theme"]["mode"])
        tk.OptionMenu(theme_frame, theme_var, "light", "dark").pack(side=tk.RIGHT)

        # Temperature units
        unit_frame = labeled_row(win, "Temperature Units")
        unit_var = tk.StringVar(value=self.preferences["units"]["temperature"])
        tk.OptionMenu(unit_frame, unit_var, "imperial", "metric").pack(side=tk.RIGHT)

        # Chart default type
        chart_frame = labeled_row(win, "Default Chart Type")
        chart_var = tk.StringVar(value=self.preferences["chart"]["default_type"])
        tk.OptionMenu(chart_frame, chart_var, "line", "bar", "scatter").pack(side=tk.RIGHT)

        # Default city
        city_frame = labeled_row(win, "Default City")
        city_var = tk.StringVar(value=self.preferences["location"]["default_city"])
        tk.Entry(city_frame, textvariable=city_var).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # 24h time
        time_frame = labeled_row(win, "24h Time Format")
        time_var = tk.BooleanVar(value=self.preferences["time"]["format_24h"])
        tk.Checkbutton(time_frame, variable=time_var, bg=theme['bg']).pack(side=tk.RIGHT)

        # Refresh interval
        refresh_frame = labeled_row(win, "Auto-Refresh (sec)")
        refresh_var = tk.StringVar(value=str(self.preferences["refresh"]["interval_seconds"]))
        tk.Entry(refresh_frame, textvariable=refresh_var).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Save button
        def on_save():
            try:
                self.preferences["language"] = lang_var.get()
                self.preferences["theme"]["mode"] = theme_var.get()
                self.preferences["units"]["temperature"] = unit_var.get()
                self.preferences["chart"]["default_type"] = chart_var.get()
                self.preferences["location"]["default_city"] = city_var.get()
                self.preferences["time"]["format_24h"] = bool(time_var.get())
                self.preferences["refresh"]["interval_seconds"] = int(refresh_var.get())

                save_preferences(self.preferences)

                # Apply immediately
                self.language = self.preferences["language"]
                self.current_theme = self.preferences["theme"]["mode"]
                self.temp_unit = self.preferences["units"]["temperature"]
                self.chart_default_type = self.preferences["chart"]["default_type"]
                self.default_city = self.preferences["location"]["default_city"]

                self.city_entry.delete(0, tk.END)
                self.city_entry.insert(0, self.default_city)

                self._apply_language()
                self._update_theme_colors()

                # Re-run auto-refresh schedule
                # (We keep it simple: the next tick will respect the new interval)
                messagebox.showinfo("Saved", "Preferences saved.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Refresh interval must be an integer.")

        save_btn = tk.Button(win, text="Save", command=on_save,
                             bg=theme['btn_bg'], fg=theme['btn_fg'])
        save_btn.pack(pady=20)

        # Apply theme to window
        win.config(bg=theme['bg'])
        for child in win.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=theme['bg'])

def launch_gui(weather_api, predictor):
    try:
        app = WeatherDashboard(weather_api, predictor)
        app.mainloop()
    except Exception as e:
        logger.error(f"Failed to launch GUI: {str(e)}")
        raise
