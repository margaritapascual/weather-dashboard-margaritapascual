# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mplcursors

from core.weather_api import WeatherAPI
from core.temp_predictor import TempPredictor
from features.current_conditions_icons import load_icon
from features.weather_alerts import show_alerts
from features.team_compare_random import TeamCompareRandomFrame  # popup uses this frame
import preferences

FLASH_INTERVAL = 500  # ms for alert banner flash
TEAM_DATA_DIR = "/Users/margaritapascual/JTC/Pathways/weather-dashboard-margaritapascual/Team Data"

def launch_gui(weather_api, predictor):
    app = WeatherDashboard(weather_api, predictor)
    app.mainloop()

class WeatherDashboard(tk.Tk):
    def __init__(self, weather_api: WeatherAPI, predictor: TempPredictor):
        super().__init__()
        self.title("Margarita’s Weather Dashboard")
        self.prefs = preferences.load_preferences()
        self._team_compare_win = None  # popup handle

        # --- Tabs setup ---
        nb = ttk.Notebook(self)
        self.tab_overview = tk.Frame(nb)
        self.tab_forecast = tk.Frame(nb)
        self.tab_charts   = tk.Frame(nb)
        self.tab_alerts   = tk.Frame(nb)
        self.tab_settings = tk.Frame(nb)
        for tab,name in [
            (self.tab_overview, "Overview"),
            (self.tab_forecast, "Forecast"),
            (self.tab_charts,   "Charts"),
            (self.tab_alerts,   "Alerts"),
            (self.tab_settings, "Settings")
        ]:
            nb.add(tab, text=name)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._apply_theme(self.prefs["theme"]["mode"])
        self.geometry("1024x700")

        self.weather   = weather_api
        self.predictor = predictor

        # --- Build UI sections ---
        self._build_top_bar()
        self._build_overview()
        self._build_forecast()
        self._build_charts()
        self._build_alerts_tab()
        self._build_settings()

        # Auto-refresh
        interval = self.prefs["refresh"]["interval_seconds"]
        if interval > 0:
            self.after(interval * 1000, self.refresh_all)

        self._flash_state = False
        self.refresh_all()
        self._update_system_clock()

    # ---------- Theming ----------
    def _apply_theme(self, mode):
        dark = (mode == "dark")
        self.bg_color = "#2E3F4F" if dark else "#FFFFFF"
        self.fg_color = "#FFFFFF" if dark else "#000000"
        self.configure(bg=self.bg_color)
        for tab in (self.tab_overview, self.tab_forecast,
                    self.tab_charts,   self.tab_alerts,
                    self.tab_settings):
            tab.configure(bg=self.bg_color)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("AlertBanner.TLabel",
                        background=self.bg_color,
                        foreground=self.fg_color,
                        font=(None,14,"bold"))
        style.configure("BigTemp.TLabel",
                        background=self.bg_color,
                        foreground=self.fg_color,
                        font=(None,60,"bold"))
        style.configure("Detail.TLabel",
                        background=self.bg_color,
                        foreground=self.fg_color,
                        font=(None,16))
        style.configure("SubText.TLabel",
                        background=self.bg_color,
                        foreground=self.fg_color,
                        font=(None,14))
        self.current_theme = mode

    # ---------- Top bar ----------
    def _build_top_bar(self):
        top = tk.Frame(self, bg=self.bg_color)
        top.pack(fill="x", pady=(8,0))

        self.alert_var = tk.StringVar()
        self.alert_lbl = ttk.Label(top, textvariable=self.alert_var,
                                   style="AlertBanner.TLabel")
        self.alert_lbl.pack(fill="x")

        tk.Label(top, text="City:", bg=self.bg_color,
                 fg=self.fg_color, font=(None,14)).pack(side="left", padx=(8,0))
        self.city_var = tk.StringVar(value=self.prefs["location"]["default_city"])
        ent = ttk.Entry(top, textvariable=self.city_var,
                        width=25, font=(None,14))
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self._update_city())

        ttk.Button(top, text="Update", command=self._update_city).pack(side="left", padx=4)
        ttk.Button(top, text="Theme",  command=self._toggle_theme).pack(side="left", padx=4)

        # Team Compare popup button
        ttk.Button(top, text="Team Compare", command=self._open_team_compare).pack(side="left", padx=4)

        ttk.Button(top, text="Exit",   command=self.destroy).pack(side="left", padx=4)

    def _open_team_compare(self):
        # if already open, bring to front
        if self._team_compare_win and self._team_compare_win.winfo_exists():
            self._team_compare_win.deiconify()
            self._team_compare_win.lift()
            self._team_compare_win.focus_force()
            return

        win = tk.Toplevel(self)
        win.title("Team Compare (Random)")
        win.configure(bg=self.bg_color)
        win.bg_color = self.bg_color
        win.fg_color = self.fg_color

        # size & center
        w, h = 980, 580
        self.update_idletasks()
        try:
            px, py = self.winfo_x(), self.winfo_y()
            pw, ph = self.winfo_width(), self.winfo_height()
            x = max(0, px + (pw - w)//2)
            y = max(0, py + (ph - h)//2)
        except Exception:
            x, y = 100, 80
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.transient(self)  # keep on top

        container = tk.Frame(win, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        frm = TeamCompareRandomFrame(
            container,
            default_dir=TEAM_DATA_DIR
        )
        frm.pack(fill="both", expand=True)

        def _on_close():
            self._team_compare_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)
        self._team_compare_win = win

    def _toggle_theme(self):
        new = "light" if self.current_theme == "dark" else "dark"
        self.theme_var.set(new)
        self._save_theme()

    def _update_city(self):
        self.prefs["location"]["default_city"] = self.city_var.get()
        preferences.save_preferences(self.prefs)
        self.refresh_all()

    # ---------- Overview ----------
    def _build_overview(self):
        f = self.tab_overview
        for i in range(5):
            f.columnconfigure(i, weight=1)

        # Current icon & temp
        self.current_icon = tk.Label(f, bg=self.bg_color)
        self.current_icon.grid(row=0, column=2, pady=(20,0))
        self.current_lbl  = ttk.Label(f, text="--°", style="BigTemp.TLabel")
        self.current_lbl.grid(row=1, column=2)

        # Details
        self.details_lbl = ttk.Label(f, text="", style="Detail.TLabel", justify="center")
        self.details_lbl.grid(row=2, column=1, columnspan=3, pady=(0,10))

        # City-local clock
        self.time_lbl = ttk.Label(f,
            text="Date & Time: --",
            font=(None,20,"bold"),
            foreground="#FF8800",
            background=self.bg_color
        )
        self.time_lbl.grid(row=3, column=2, pady=(0,10))

        # System-local clock
        self.system_time_lbl = ttk.Label(f,
            text="My Time: --",
            font=(None,20,"bold"),
            foreground="#00AAFF",
            background=self.bg_color
        )
        self.system_time_lbl.grid(row=4, column=2, pady=(0,10))

        # Sunrise/Sunset
        self.sunrise_lbl = ttk.Label(f, text="Sunrise: --:--", style="Detail.TLabel")
        self.sunrise_lbl.grid(row=5, column=1)
        self.sunset_lbl  = ttk.Label(f, text="Sunset:  --:--", style="Detail.TLabel")
        self.sunset_lbl.grid(row=5, column=3)

        # Framed & expanded 5-Day Forecast
        forecast_frame = tk.Frame(f, bg=self.bg_color)
        forecast_frame.grid(row=6, column=0, columnspan=5, pady=(20,10), sticky="ew")

        tk.Label(forecast_frame,
                 text="5-Day Forecast",
                 bg=self.bg_color,
                 fg=self.fg_color,
                 font=(None,20,"bold")
        ).pack()

        cards_frame = tk.Frame(forecast_frame, bg=self.bg_color)
        cards_frame.pack(fill="x", pady=8)
        for i in range(5):
            cards_frame.columnconfigure(i, weight=1)

        self.five_cards = []
        for i in range(5):
            frm = tk.Frame(cards_frame, bg=self.bg_color)
            frm.grid(row=0, column=i, padx=8, sticky="nsew")
            ic = tk.Label(frm, bg=self.bg_color); ic.pack()
            day = ttk.Label(frm, text="--", style="SubText.TLabel"); day.pack()
            hl  = ttk.Label(frm, text="H:-- L:--", style="SubText.TLabel"); hl.pack()
            pop = ttk.Label(frm, text="--% rain", style="SubText.TLabel"); pop.pack()
            self.five_cards.append((ic, day, hl, pop))

    # ---------- Forecast ----------
    def _build_forecast(self):
        f = self.tab_forecast
        cols = ("Day","Hi","Lo","Precip")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- Charts ----------
    def _build_charts(self):
        f = self.tab_charts
        btnf = tk.Frame(f, bg=self.bg_color); btnf.pack(fill="x", pady=(10,0))
        self.freq = tk.StringVar(value=self.prefs["forecast"]["default_tab"])
        for lbl,val in [("Daily","daily"),("Weekly","weekly"),("7-Day","7_day"),
                        ("30-Day","30_day"),("Monthly","monthly")]:
            tk.Button(btnf, text=lbl, font=(None,12),
                      command=lambda v=val:self._set_freq(v)).pack(side="left", padx=5)

        fig = Figure(figsize=(6,4), dpi=100)
        self.ax = fig.add_subplot(111)
        fig.tight_layout()  # <-- do this on the Figure itself

        self.canvas = FigureCanvasTkAgg(fig, master=f)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _set_freq(self, val):
        self.freq.set(val)
        self.prefs["forecast"]["default_tab"] = val
        preferences.save_preferences(self.prefs)
        self._plot_chart()

    # ---------- Alerts ----------
    def _build_alerts_tab(self):
        f = self.tab_alerts; f.configure(bg=self.bg_color)
        self.alerts_frame = tk.Frame(f, bg=self.bg_color)
        self.alerts_frame.pack(fill="both", expand=True)

    # ---------- Settings ----------
    def _build_settings(self):
        f = self.tab_settings; f.configure(bg=self.bg_color)
        row = 0
        ttk.Label(f, text="Units:", background=self.bg_color, foreground=self.fg_color).grid(row=row, column=0, sticky="w", padx=10)
        self.unit = tk.StringVar(value=self.prefs["units"]["temperature"])
        for i,u in enumerate(("imperial","metric")):
            ttk.Radiobutton(f, text=u, variable=self.unit, value=u, command=self._save_settings).grid(row=row, column=1+i)
        row += 1
        ttk.Label(f, text="Language:", background=self.bg_color, foreground=self.fg_color).grid(row=row, column=0, sticky="w", padx=10)
        self.lang = tk.StringVar(value=self.prefs["language"])
        for i,l in enumerate(("en","es")):
            ttk.Radiobutton(f, text=l.upper(), variable=self.lang, value=l, command=self._save_settings).grid(row=row, column=1+i)
        row += 1
        ttk.Label(f, text="Theme:", background=self.bg_color, foreground=self.fg_color).grid(row=row, column=0, sticky="w", padx=10)
        self.theme_var = tk.StringVar(value=self.prefs["theme"]["mode"])
        for i,m in enumerate(("light","dark")):
            ttk.Radiobutton(f, text=m.title(), variable=self.theme_var, value=m, command=self._save_theme).grid(row=row, column=1+i)
        row += 1
        ttk.Label(f, text="Weather Alerts:", background=self.bg_color, foreground=self.fg_color).grid(row=row, column=0, sticky="w", padx=10)
        self.alert_chk = tk.BooleanVar(value=self.prefs["alerts"]["enabled"])
        for i,val in enumerate((True,False)):
            ttk.Radiobutton(f, text="On" if val else "Off", variable=self.alert_chk, value=val, command=self._save_settings).grid(row=row, column=1+i)
        row += 1
        ttk.Label(f, text="Chart Type:", background=self.bg_color, foreground=self.fg_color).grid(row=row, column=0, sticky="w", padx=10)
        self.chart_type = tk.StringVar(value=self.prefs["chart"]["default_type"])
        for i,t in enumerate(("line","bar","both")):
            ttk.Radiobutton(f, text=t.title(), variable=self.chart_type, value=t, command=self._save_settings).grid(row=row, column=1+i)

    # ---------- Prefs ----------
    def _save_theme(self):
        self.prefs["theme"]["mode"] = self.theme_var.get()
        preferences.save_preferences(self.prefs)
        self._apply_theme(self.theme_var.get())
        # re-theme popup if open
        if self._team_compare_win and self._team_compare_win.winfo_exists():
            self._team_compare_win.configure(bg=self.bg_color)
            self._team_compare_win.bg_color = self.bg_color
            self._team_compare_win.fg_color = self.fg_color
        self.refresh_all()

    def _save_settings(self):
        self.prefs["units"]["temperature"]    = self.unit.get()
        self.prefs["language"]                = self.lang.get()
        self.prefs["alerts"]["enabled"]       = self.alert_chk.get()
        self.prefs["chart"]["default_type"]   = self.chart_type.get()
        preferences.save_preferences(self.prefs)
        self.refresh_all()

    # ---------- Data refresh ----------
    def refresh_all(self):
        city   = self.city_var.get()
        cur    = self.weather.get_current(city)
        daily  = self.weather.get_daily(city)
        alerts = self.weather.get_alerts(city)

        if alerts and self.prefs["alerts"]["enabled"]:
            ev    = alerts[0]["event"]
            until = datetime.fromtimestamp(alerts[0]["end"]).strftime("%I:%M %p")
            self.alert_var.set(f"⚠ {ev} until {until}")
            self._flash_banner()
        else:
            self.alert_var.set("")
            if hasattr(self, "_flash_job"): self.after_cancel(self._flash_job)
            self.alert_lbl.configure(background=self.bg_color)

        icon = load_icon(cur["weather"][0]["icon"])
        self.current_icon.config(image=icon); self.current_icon.image = icon
        temp = round(cur["temp"])
        if self.unit.get()=="metric":
            temp = round((temp-32)*5/9)
        self.current_lbl.config(text=f"{temp}°")

        today_hi = round(daily[0]["temp"]["max"])
        today_lo = round(daily[0]["temp"]["min"])
        if self.unit.get()=="metric":
            today_hi = round((today_hi-32)*5/9)
            today_lo = round((today_lo-32)*5/9)
        pop = int(daily[0].get("pop",0)*100)
        hum = cur.get("humidity",0)
        uv  = cur.get("uvi",0)
        self.details_lbl.config(
            text=f"H:{today_hi} L:{today_lo}   Precip:{pop}%   Humidity:{hum}%   UV:{uv}"
        )

        self.tz_offset = cur.get("timezone", 0)
        self._update_clock()

        sr = datetime.fromtimestamp(cur["sunrise"]).strftime("%I:%M %p")
        ss = datetime.fromtimestamp(cur["sunset"]).strftime("%I:%M %p")
        self.sunrise_lbl.config(text=f"Sunrise: {sr}")
        self.sunset_lbl.config(text=f"Sunset:  {ss}")

        for i,card in enumerate(self.five_cards):
            if i < len(daily):
                d = daily[i]
                img2 = load_icon(d["weather"][0]["icon"])
                card[0].config(image=img2); card[0].image = img2
                day = datetime.fromtimestamp(d["dt"]).strftime("%a")
                hi2 = round(d["temp"]["max"])
                lo2 = round(d["temp"]["min"])
                if self.unit.get()=="metric":
                    hi2 = round((hi2-32)*5/9)
                    lo2 = round((lo2-32)*5/9)
                pop2 = int(d.get("pop",0)*100)
                card[1].config(text=day)
                card[2].config(text=f"H:{hi2} L:{lo2}")
                card[3].config(text=f"{pop2}% rain")

        for r in self.tree.get_children(): self.tree.delete(r)
        for d in daily:
            day = datetime.fromtimestamp(d["dt"]).strftime("%a %m/%d")
            hi3 = round(d["temp"]["max"])
            lo3 = round(d["temp"]["min"])
            if self.unit.get()=="metric":
                hi3 = round((hi3-32)*5/9)
                lo3 = round((lo3-32)*5/9)
            pop3 = int(d.get("pop",0)*100)
            self.tree.insert("", "end",
                             values=(day, f"{hi3}°", f"{lo3}°", f"{pop3}%"))

        show_alerts(alerts, self.alerts_frame,
                    {"bg":self.bg_color, "fg":self.fg_color})
        self._daily = daily
        self._plot_chart()

    # ---------- Clocks ----------
    def _update_clock(self):
        now = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=self.tz_offset)
        date_str = now.strftime("%A, %b %d, %Y")
        time_str = now.strftime("%I:%M %p")
        tz_label = f"UTC{'+' if self.tz_offset//3600>=0 else ''}{self.tz_offset//3600}"
        self.time_lbl.config(text=f"{date_str} — {time_str} ({tz_label})")
        self.after(60000, self._update_clock)

    def _update_system_clock(self):
        now = datetime.now().astimezone()
        date_str = now.strftime("%A, %b %d, %Y")
        time_str = now.strftime("%I:%M %p")
        offset = now.utcoffset().total_seconds() if now.utcoffset() else 0
        hours = int(offset // 3600)
        tz_lbl = f"UTC{'+' if hours>=0 else ''}{hours}"
        self.system_time_lbl.config(text=f"{date_str} — {time_str} ({tz_lbl})")
        self.after(60000, self._update_system_clock)

    def _flash_banner(self):
        color = "red" if self._flash_state else self.bg_color
        self.alert_lbl.configure(background=color)
        self._flash_state = not self._flash_state
        self._flash_job = self.after(FLASH_INTERVAL, self._flash_banner)

    # ---------- Charting ----------
    def _plot_chart(self):
        freq = self.freq.get()
        subset = {
            "daily":   self._daily[:1],
            "weekly":  self._daily[:7],
            "7_day":   self._daily[:7],
            "30_day":  self._daily[:30],
            "monthly": self._daily[:30],
        }.get(freq, self._daily[:7])

        dates = [datetime.fromtimestamp(d["dt"]).strftime("%m/%d") for d in subset]
        temps = [d["temp"]["day"] for d in subset]
        if self.unit.get()=="metric":
            temps = [round((t-32)*5/9) for t in temps]
        precip = [int(d.get("pop",0)*100) for d in subset]
        humid = [d.get("humidity",0) for d in subset]

        chart_type = self.chart_type.get()
        self.ax.clear()
        ax2 = self.ax.twinx()
        self.ax.set_title(f"{freq.replace('_',' ').title()} Forecast")
        self.ax.set_ylabel("Temp / Precip (%)")
        ax2.set_ylabel("Humidity (%)")

        if chart_type in ("line", "both"):
            self.ax.plot(dates, temps, marker="o", label="Temp (°F)")
            self.ax.plot(dates, precip, marker="x", linestyle="--", label="Precip (%)")
            ax2.plot(dates, humid, marker="s", linestyle=":", color="tab:blue", label="Humidity (%)")

        if chart_type in ("bar", "both"):
            width = 0.35
            x = list(range(len(dates)))
            self.ax.bar([i - width/2 for i in x], temps, width=width, alpha=0.6, label="Temp (°F)")
            self.ax.bar([i + width/2 for i in x], precip, width=width, alpha=0.4, label="Precip (%)")
            ax2.plot(dates, humid, marker="s", linestyle=":", color="tab:blue", label="Humidity (%)")

        self.ax.set_xticks(range(len(dates)))
        self.ax.set_xticklabels(dates, rotation=45)

        try:
            pdx, pt = self.predictor.get_series(self.city_var.get(), freq)
            self.ax.plot(pdx, pt, linestyle=":", color="purple", label="ML Pred")
        except Exception:
            pass

        h1, l1 = self.ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        self.ax.legend(h1 + h2, l1 + l2, loc="upper left")

        self.canvas.draw()
        mplcursors.cursor(self.ax, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()}: {sel.target[1]:.1f}")
        )
