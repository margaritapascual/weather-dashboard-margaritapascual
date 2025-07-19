import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from features.theme_switcher import create_theme_menu
from core.weather_api import WeatherAPI
from features.current_conditions_icons import load_icon
from features.historical_data import save_history

# Color themes (dark-mode buttons are now light gray with black text)
themes = {
	'light': dict(
		bg='#005f6a',
		sidebar_bg='#044f4f',
		fg='white',
		btn_bg='white',
		btn_fg='black'
	),
	'dark': dict(
		bg='#222222',
		sidebar_bg='#111111',
		fg='white',
		btn_bg='#888888',   # lighter gray so text shows up
		btn_fg='black'
	),
}

class WeatherDashboard(tk.Tk):
	def __init__(self, weather_api: WeatherAPI):
		super().__init__()
		self.weather_api = weather_api
		self.title("Weather Dashboard")
		self.geometry("800x600")

		# Initial theme & menu
		self.current_theme = 'light'
		self._apply_theme_recursively()
		create_theme_menu(self, self.select_theme)

		self.sidebar_width = 200
		self._build_widgets()

	def select_theme(self, name):
		"""Called by the Theme menu or Toggle button."""
		self.current_theme = name
		self._apply_theme_recursively()
		try:
			self.chart.draw()
		except:
			pass

	def _apply_theme_recursively(self, widget=None):
		"""Walk the widget tree and apply background/foreground colors."""
		if widget is None:
			widget = self
		t = themes[self.current_theme]

		# Try setting background everywhere
		try:
			widget.configure(background=t['bg'])
		except tk.TclError:
			pass

		# Labels & Buttons: also set fg/bg
		if isinstance(widget, (tk.Label, tk.Button)):
			widget.configure(
				background=(t['btn_bg'] if isinstance(widget, tk.Button) else t['bg']),
				foreground=(t['btn_fg'] if isinstance(widget, tk.Button) else t['fg'])
			)

		for child in widget.winfo_children():
			self._apply_theme_recursively(child)

	def _build_widgets(self):
		# Sidebar
		self.sidebar = tk.Frame(
			self,
			background=themes[self.current_theme]['sidebar_bg'],
			width=self.sidebar_width
		)
		self.sidebar.pack(side='left', fill='y')
		self.sidebar.pack_propagate(False)

		self.sb_icon = tk.Label(
			self.sidebar,
			background=themes[self.current_theme]['sidebar_bg']
		)
		self.sb_icon.pack(pady=10)

		self.sb_temp = tk.Label(
			self.sidebar,
			text="--°F",
			font=('Helvetica', 20),
			background=themes[self.current_theme]['sidebar_bg'],
			foreground=themes[self.current_theme]['fg']
		)
		self.sb_temp.pack()

		self.sb_humidity = tk.Label(
			self.sidebar,
			text="Humidity: --%",
			background=themes[self.current_theme]['sidebar_bg'],
			foreground=themes[self.current_theme]['fg']
		)
		self.sb_humidity.pack()

		self.sb_uv = tk.Label(
			self.sidebar,
			text="UV Index: --",
			background=themes[self.current_theme]['sidebar_bg'],
			foreground=themes[self.current_theme]['fg']
		)
		self.sb_uv.pack(pady=(0,10))

		self.sb_alert = tk.Label(
			self.sidebar,
			text="",
			wraplength=self.sidebar_width-10,
			background=themes[self.current_theme]['sidebar_bg'],
			foreground=themes[self.current_theme]['fg'],
			justify='left'
		)
		self.sb_alert.pack(pady=(0,20))

		# Controls
		self.ctrl_frame = tk.Frame(
			self,
			background=themes[self.current_theme]['bg']
		)
		self.ctrl_frame.pack(fill='x', padx=10, pady=5)

		tk.Label(
			self.ctrl_frame,
			text="City:",
			background=themes[self.current_theme]['bg'],
			foreground=themes[self.current_theme]['fg']
		).pack(side='left')

		self.city_entry = tk.Entry(self.ctrl_frame)
		self.city_entry.pack(side='left', padx=5)

		for label, cmd in [("Update", self.on_update),
						   ("Toggle Theme", self.toggle_theme)]:
			btn = tk.Button(
				self.ctrl_frame,
				text=label,
				background=themes[self.current_theme]['btn_bg'],
				foreground=themes[self.current_theme]['btn_fg'],
				activebackground=themes[self.current_theme]['bg'],
				activeforeground=themes[self.current_theme]['btn_fg'],
				highlightbackground=themes[self.current_theme]['btn_bg'],  # macOS hack
				command=cmd
			)
			btn.pack(side='left', padx=5)

		# Forecast icons
		self.forecast_frame = tk.Frame(
			self,
			background=themes[self.current_theme]['bg']
		)
		self.forecast_frame.pack(fill='x', padx=10, pady=5)

		# Mode buttons
		self.mode_frame = tk.Frame(
			self,
			background=themes[self.current_theme]['bg']
		)
		self.mode_frame.pack(fill='x', padx=10)
		modes = ['Daily', 'Weekly', 'Monthly', '7-Day Temp', '30-Day Temp']
		for m in modes:
			btn = tk.Button(
				self.mode_frame,
				text=m,
				background=themes[self.current_theme]['btn_bg'],
				foreground=themes[self.current_theme]['btn_fg'],
				activebackground=themes[self.current_theme]['bg'],
				activeforeground=themes[self.current_theme]['btn_fg'],
				highlightbackground=themes[self.current_theme]['btn_bg'],
				command=lambda t=m: self.on_mode(t)
			)
			btn.pack(side='left', padx=4)

		# Main plotting area
		self.main_frame = tk.Frame(self, background='white')
		self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
		self.fig = Figure(figsize=(5,3), dpi=100)
		self.ax = self.fig.add_subplot(111)
		self.chart = FigureCanvasTkAgg(self.fig, master=self.main_frame)
		self.chart.get_tk_widget().pack(fill='both', expand=True)

	def toggle_theme(self):
		new = 'dark' if self.current_theme=='light' else 'light'
		self.select_theme(new)

	def on_update(self):
		city = self.city_entry.get().strip()
		if not city:
			messagebox.showwarning("Input needed", "Enter a city.")
			return

		try:
			lat, lon = self.weather_api.geocode(city)
			self.last_lat, self.last_lon = lat, lon

			current = self.weather_api.get_current(lat, lon)

			# Alerts pop-up
			alerts = current.get('alerts', [])
			if alerts:
				for alert in alerts:
					title = alert.get('event', "Weather Alert")
					desc  = alert.get('description', "")
					messagebox.showwarning(title, desc)
			else:
				messagebox.showinfo("No Alerts", "There are no active weather alerts.")

			self._update_sidebar(current)
			daily = self.weather_api.get_daily(lat, lon, days=7)
			self._update_forecast(daily)
			save_history(city, daily)

		except Exception as e:
			messagebox.showerror("Error", str(e))

	def _update_sidebar(self, current):
		icon = load_icon(current['weather'][0]['icon'], size=(50,50))
		if icon:
			self.sb_icon.config(image=icon)
			self.sb_icon.image = icon
		self.sb_temp.config(text=f"{current['temp']}°F")
		self.sb_humidity.config(text=f"Humidity: {current['humidity']}%")
		self.sb_uv.config(text=f"UV Index: {current['uvi']}")
		alerts = current.get('alerts', [])
		self.sb_alert.config(
			text="\n".join(a['description'] for a in alerts) if alerts else ""
		)

	def _update_forecast(self, daily):
		for w in self.forecast_frame.winfo_children():
			w.destroy()

		for day in daily:
			f = tk.Frame(self.forecast_frame, background=themes[self.current_theme]['bg'])
			f.pack(side='left', padx=4)

			dn = datetime.fromtimestamp(day['dt']).strftime('%a')
			tk.Label(f, text=dn,
					 background=themes[self.current_theme]['bg'],
					 foreground=themes[self.current_theme]['fg']).pack()

			try:
				icon = load_icon(day['weather'][0]['icon'], size=(40,40))
				if icon:
					lbl = tk.Label(f, image=icon,
								   background=themes[self.current_theme]['bg'])
					lbl.image = icon
					lbl.pack()
			except:
				pass

			tmax = day['temp'].get('max')
			tmin = day['temp'].get('min')
			if tmax is not None and tmin is not None:
				tk.Label(f, text=f"{tmax:.0f}° | {tmin:.0f}°",
						 background=themes[self.current_theme]['bg'],
						 foreground=themes[self.current_theme]['fg'],
						 font=('Helvetica',10)).pack(pady=(2,0))

	def on_mode(self, mode):
		if not hasattr(self, 'last_lat'):
			messagebox.showwarning("No data", "Please update a city first.")
			return

		days_map = {
			'Daily':    1,
			'Weekly':   7,
			'7-Day Temp':7,
			'Monthly':  30,
			'30-Day Temp':30
		}
		days = days_map.get(mode, 7)

		series   = self.weather_api.get_daily(self.last_lat, self.last_lon, days=days)
		dates    = [datetime.fromtimestamp(d['dt']) for d in series]
		temps    = [(d['temp']['day'] if isinstance(d['temp'], dict) else d['temp'])
					for d in series]
		humidity = [d.get('humidity', 0) for d in series]
		precip   = [d.get('rain', d.get('pop', 0)) for d in series]

		self.ax.clear()
		self.ax.plot(dates, temps, marker='o', label='Temp (°F)')
		self.ax.set_ylabel("Temp (°F)")

		ax2 = self.ax.twinx()
		ax2.plot(dates, humidity, marker='s', linestyle='--', label='Humidity (%)')
		ax2.bar(dates, precip, alpha=0.3, width=0.2, label='Precip (mm)')

		self.ax.legend(loc='upper left')
		ax2.legend(loc='upper right')
		self.ax.set_title(f"{mode} Forecast")

		self.fig.autofmt_xdate()
		self.chart.draw()

def launch_gui(weather_api: WeatherAPI):
	app = WeatherDashboard(weather_api)
	app.mainloop()
