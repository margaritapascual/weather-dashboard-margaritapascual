# gui.py

import threading
import tkinter as tk
from tkinter import messagebox

from features.current_conditions_icons import show_weather_icon
from features.historical_data        import show_history
from features.temperature_graph      import embed_temperature_graph
from features.theme_switcher         import ThemeSwitcher

class MainWindow:
    def __init__(self, cfg, storage, api):
        self.cfg     = cfg
        self.storage = storage
        self.api     = api

        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("450x500")

        # — Search Bar —
        top = tk.Frame(self.root)
        top.pack(pady=10)
        tk.Label(top, text="City:").pack(side=tk.LEFT)
        self.city_var = tk.StringVar()
        tk.Entry(top, textvariable=self.city_var, width=20).pack(side=tk.LEFT)
        tk.Button(top, text="Search",  command=self.on_search).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="History", command=self.on_history).pack(side=tk.LEFT, padx=5)

        # — Error & Results —
        self.error_lbl = tk.Label(self.root, text="", fg="red")
        self.error_lbl.pack()
        self.city_lbl  = tk.Label(self.root, text="", font=("Arial",16))
        self.city_lbl.pack()
        self.temp_lbl  = tk.Label(self.root, text="", font=("Arial",14))
        self.temp_lbl.pack()
        self.desc_lbl  = tk.Label(self.root, text="", font=("Arial",12))
        self.desc_lbl.pack()

        # — Placeholder for features (icon, graph, table) —
        self.feature_frame = tk.Frame(self.root)
        self.feature_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # — Theme Switcher —
        self.theme = ThemeSwitcher(self.root)

    def on_search(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        # Run fetch+UI in background
        threading.Thread(target=self._do_search, args=(city,), daemon=True).start()

    def _do_search(self, city):
        try:
            data = self.api.fetch_current(city)
            parsed = {
                "city":        data["name"],
                "country":     data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "icon":        data["weather"][0]["icon"]
            }
            self.storage.add_entry(parsed)
            self.root.after(0, lambda: self._update_ui(parsed))

        except Exception as e:
            print("Search error:", e)
            self.root.after(0, lambda: self.show_error(f"Could not fetch weather for '{city}'."))

    def _update_ui(self, parsed):
        # clear previous feature widgets
        for w in self.feature_frame.winfo_children():
            w.destroy()

        # display the new data
        self.error_lbl.config(text="")
        self.city_lbl.config(text=f"{parsed['city']}, {parsed['country']}")
        self.temp_lbl.config(text=f"{parsed['temperature']:.1f} °C")
        self.desc_lbl.config(text=parsed['description'].capitalize())

        # show the weather icon
        show_weather_icon(self.feature_frame, parsed["icon"])

    def on_history(self):
        history = self.storage.get_last_n(7)

        # clear frame
        for w in self.feature_frame.winfo_children():
            w.destroy()

        # show history table and graph
        show_history(self.feature_frame, history)
        embed_temperature_graph(self.feature_frame, history)

    def show_error(self, msg: str):
        self.error_lbl.config(text=msg)

    def run(self):
        self.root.mainloop()


        # display text
        self.error_lbl.config(text="")
        self.city_lbl.config(text=f"{parsed['city']}, {parsed['country']}")
        self.temp_lbl.config(text=f"{parsed['temperature']:.1f} °C")
        self.desc_lbl.config(text=parsed['description'].capitalize())

        # icon
        show_weather_icon(self.feature_frame, parsed["icon"])

    def on_history(self):
        # fetch last 7
        history = self.storage.get_last_n(7)

        # clear feature frame
        for w in self.feature_frame.winfo_children():
            w.destroy()

        # table + chart
        show_history(self.feature_frame, history)
        embed_temperature_graph(self.feature_frame, history)

    def show_error(self, msg: str):
        self.error_lbl.config(text=msg)

    def run(self):
        self.root.mainloop()
