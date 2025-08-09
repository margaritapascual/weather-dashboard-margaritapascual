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

# --- Minimal i18n helper (EN/ES) ---
I18N = {
    "en": {
        "app_title": "Margarita’s Weather Dashboard",
        "tab_overview": "Overview",
        "tab_forecast": "Forecast",
        "tab_charts": "Charts",
        "tab_alerts": "Alerts",
        "tab_settings": "Settings",
        "label_city": "City:",
        "btn_update": "Update",
        "btn_theme":  "Theme",
        "btn_team_compare": "Team Compare",
        "btn_exit":   "Exit",
        "forecast_title": "5-Day Forecast",
        "sunrise": "Sunrise",
        "sunset":  "Sunset",
        "table_day": "Day", "table_hi": "Hi", "table_lo": "Lo", "table_precip": "Precip",
        "chart_title": "Forecast",
        "alerts_until": "until",
        "chart_daily": "Daily",
        "chart_7day": "7-Day",
        "chart_30day": "30-Day",
        "rain_word": "rain",
        "temp_label_f": "Temp (°F)",
        "temp_label_c": "Temp (°C)",
    },
    "es": {
        "app_title": "Panel del Clima de Margarita",
        "tab_overview": "Resumen",
        "tab_forecast": "Pronóstico",
        "tab_charts": "Gráficas",
        "tab_alerts": "Alertas",
        "tab_settings": "Ajustes",
        "label_city": "Ciudad:",
        "btn_update": "Actualizar",
        "btn_theme":  "Tema",
        "btn_team_compare": "Comparar Equipo",
        "btn_exit":   "Salir",
        "forecast_title": "Pronóstico de 5 Días",
        "sunrise": "Amanecer",
        "sunset":  "Atardecer",
        "table_day": "Día", "table_hi": "Máx", "table_lo": "Mín", "table_precip": "Lluvia",
        "chart_title": "Pronóstico",
        "alerts_until": "hasta",
        "chart_daily": "Diario",
        "chart_7day": "7 Días",
        "chart_30day": "30 Días",
        "rain_word": "lluvia",
        "temp_label_f": "Temp (°F)",
        "temp_label_c": "Temp (°C)",
    }
}
def t(key, lang):  # tiny helper
    return I18N.get(lang, I18N["en"]).get(key, I18N["en"].get(key, key))

def launch_gui(weather_api, predictor):
    app = WeatherDashboard(weather_api, predictor)
    app.mainloop()

class WeatherDashboard(tk.Tk):
    def __init__(self, weather_api: WeatherAPI, predictor: TempPredictor):
        super().__init__()
        self.prefs = preferences.load_preferences()
        self.title(t("app_title", self.prefs["language"]))

        self._team_compare_win = None  # popup handle
        self.weather   = weather_api
        self.predictor = predictor

        # --- Tabs setup ---
        self.nb = ttk.Notebook(self)
        self.tab_overview = tk.Frame(self.nb)
        self.tab_forecast = tk.Frame(self.nb)
        self.tab_charts   = tk.Frame(self.nb)
        self.tab_alerts   = tk.Frame(self.nb)
        self.tab_settings = tk.Frame(self.nb)
        for tab,name_key in [
            (self.tab_overview, "tab_overview"),
            (self.tab_forecast, "tab_forecast"),
            (self.tab_charts,   "tab_charts"),
            (self.tab_alerts,   "tab_alerts"),
            (self.tab_settings, "tab_settings")
        ]:
            self.nb.add(tab, text=t(name_key, self.prefs["language"]))
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._apply_theme(self.prefs["theme"]["mode"])
        self.geometry("1024x700")

        # --- Build UI sections ---
        self._build_top_bar()
        self._build_overview()
        self._build_forecast()
        self._build_charts()
        self._build_alerts_tab()
        self._build_settings()

        # --- Bottom status bar clock (city-local, persistent) ---
        self.status = tk.Label(self, anchor="w", bg=self.bg_color, fg=self.fg_color, font=(None, 12))
        self.status.pack(side="bottom", fill="x")

        # Auto-refresh
        interval = self.prefs["refresh"]["interval_seconds"]
        if interval > 0:
            self.after(interval * 1000, self.refresh_all)

        self._flash_state = False
        self.refresh_all()  # also sets tz_offset
        self._update_clock()

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
        lang = self.prefs["language"]
        top = tk.Frame(self, bg=self.bg_color)
        top.pack(fill="x", pady=(8,0))

        self.alert_var = tk.StringVar()
        self.alert_lbl = ttk.Label(top, textvariable=self.alert_var, style="AlertBanner.TLabel")
        self.alert_lbl.pack(fill="x")

        self.lbl_city = tk.Label(top, text=t("label_city", lang), bg=self.bg_color,
                                 fg=self.fg_color, font=(None,14))
        self.lbl_city.pack(side="left", padx=(8,0))

        self.city_var = tk.StringVar(value=self.prefs["location"]["default_city"])
        ent = ttk.Entry(top, textvariable=self.city_var, width=25, font=(None,14))
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: self._update_city())

        self.btn_update = ttk.Button(top, text=t("btn_update", lang), command=self._update_city)
        self.btn_update.pack(side="left", padx=4)
        self.btn_theme  = ttk.Button(top, text=t("btn_theme", lang),  command=self._toggle_theme)
        self.btn_theme.pack(side="left", padx=4)
        self.btn_team   = ttk.Button(top, text=t("btn_team_compare", lang), command=self._open_team_compare)
        self.btn_team.pack(side="left", padx=4)
        self.btn_exit   = ttk.Button(top, text=t("btn_exit", lang),   command=self.destroy)
        self.btn_exit.pack(side="left", padx=4)

    def _open_team_compare(self):
        # if already open, bring to front
        if self._team_compare_win and self._team_compare_win.winfo_exists():
            self._team_compare_win.deiconify()
            self._team_compare_win.lift()
            self._team_compare_win.focus_force()
            return

        win = tk.Toplevel(self)
        win.title(t("btn_team_compare", self.prefs["language"]))
        win.configure(bg=self.bg_color)
        win.bg_color = self.bg_color
        win.fg_color = self.fg_color

        # size & center
        w, h = 980, 620
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

        frm = TeamCompareRandomFrame(container, default_dir=TEAM_DATA_DIR)
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

        # Sunrise/Sunset
        self.sunrise_lbl = ttk.Label(f, text=f"{t('sunrise', self.prefs['language'])}: --:--", style="Detail.TLabel")
        self.sunrise_lbl.grid(row=3, column=1)
        self.sunset_lbl  = ttk.Label(f, text=f"{t('sunset', self.prefs['language'])}:  --:--", style="Detail.TLabel")
        self.sunset_lbl.grid(row=3, column=3)

        # Framed & expanded 5-Day Forecast
        forecast_frame = tk.Frame(f, bg=self.bg_color)
        forecast_frame.grid(row=4, column=0, columnspan=5, pady=(20,10), sticky="ew")

        self.forecast_title_label = tk.Label(
            forecast_frame,
            text=t("forecast_title", self.prefs["language"]),
            bg=self.bg_color, fg=self.fg_color, font=(None,20,"bold")
        )
        self.forecast_title_label.pack()

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
            pop = ttk.Label(frm, text=f"--% {t('rain_word', self.prefs['language'])}", style="SubText.TLabel"); pop.pack()
            self.five_cards.append((ic, day, hl, pop))

    # ---------- Forecast ----------
    def _build_forecast(self):
        self._rebuild_forecast_tree(self.prefs["language"])

    def _rebuild_forecast_tree(self, lang):
        f = self.tab_forecast
        for child in f.winfo_children():
            child.destroy()
        cols = (t("table_day", lang), t("table_hi", lang), t("table_lo", lang), t("table_precip", lang))
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- Charts ----------
    def _build_charts(self):
        # Bring back: Daily • 7-Day • 30-Day
        f = self.tab_charts
        btnf = tk.Frame(f, bg=self.bg_color); btnf.pack(fill="x", pady=(10,0))
        default_freq = self.prefs["forecast"].get("default_tab", "7_day")
        if default_freq not in ("daily","7_day","30_day"):
            default_freq = "7_day"
        self.freq = tk.StringVar(value=default_freq)

        # buttons with localized labels
        self.btn_daily  = tk.Button(btnf, text=t("chart_daily",  self.prefs["language"]),
                                    font=(None,12), command=lambda:self._set_freq("daily"))
        self.btn_week   = tk.Button(btnf, text=t("chart_7day",   self.prefs["language"]),
                                    font=(None,12), command=lambda:self._set_freq("7_day"))
        self.btn_30day  = tk.Button(btnf, text=t("chart_30day",  self.prefs["language"]),
                                    font=(None,12), command=lambda:self._set_freq("30_day"))
        for b in (self.btn_daily, self.btn_week, self.btn_30day):
            b.pack(side="left", padx=5)

        fig = Figure(figsize=(6,4), dpi=100)
        self.ax = fig.add_subplot(111)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=f)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _set_freq(self, val):
        self.freq.set(val)
        # keep saving so next open matches last choice
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
        for i,t_ in enumerate(("line","bar","both")):
            ttk.Radiobutton(f, text=t_.title(), variable=self.chart_type, value=t_, command=self._save_settings).grid(row=row, column=1+i)

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

    def _apply_language_texts(self):
        """Update all labels/buttons/tab titles/headings to the current language."""
        lang = self.prefs["language"]
        # Window + tabs
        self.title(t("app_title", lang))
        self.nb.tab(self.tab_overview, text=t("tab_overview", lang))
        self.nb.tab(self.tab_forecast, text=t("tab_forecast", lang))
        self.nb.tab(self.tab_charts,   text=t("tab_charts",   lang))
        self.nb.tab(self.tab_alerts,   text=t("tab_alerts",   lang))
        self.nb.tab(self.tab_settings, text=t("tab_settings", lang))
        # Top bar widgets
        self.lbl_city.config(text=t("label_city", lang))
        self.btn_update.config(text=t("btn_update", lang))
        self.btn_theme.config(text=t("btn_theme", lang))
        self.btn_team.config(text=t("btn_team_compare", lang))
        self.btn_exit.config(text=t("btn_exit", lang))
        # Overview labels
        self.forecast_title_label.config(text=t("forecast_title", lang))
        # Rebuild forecast table (headings are localized)
        self._rebuild_forecast_tree(lang)
        # Rebuild chart buttons text
        self.btn_daily.config(text=t("chart_daily", lang))
        self.btn_week.config(text=t("chart_7day", lang))
        self.btn_30day.config(text=t("chart_30day", lang))
        # Update popup title if open
        if self._team_compare_win and self._team_compare_win.winfo_exists():
            self._team_compare_win.title(t("btn_team_compare", lang))

    def _save_settings(self):
        new_units = self.unit.get()
        new_lang  = self.lang.get()

        self.prefs["units"]["temperature"]  = new_units
        self.prefs["language"]              = new_lang
        self.prefs["alerts"]["enabled"]     = self.alert_chk.get()
        self.prefs["chart"]["default_type"] = self.chart_type.get()
        preferences.save_preferences(self.prefs)

        # Update API client
        try:
            self.weather.set_lang(new_lang)
            self.weather.set_units(new_units)
        except Exception:
            pass

        self._apply_theme(self.theme_var.get())
        self._apply_language_texts()
        self.refresh_all()

    # ---------- Data refresh ----------
    def refresh_all(self):
        lang = self.prefs["language"]
        city   = self.city_var.get()
        cur    = self.weather.get_current(city)
        daily  = self.weather.get_daily(city)
        alerts = self.weather.get_alerts(city)

        if alerts and self.prefs["alerts"]["enabled"]:
            ev    = alerts[0]["event"]
            until = datetime.fromtimestamp(alerts[0]["end"]).strftime("%I:%M %p")
            self.alert_var.set(f"⚠ {ev} {t('alerts_until', lang)} {until}")
            self._flash_banner()
        else:
            self.alert_var.set("")
            if hasattr(self, "_flash_job"): self.after_cancel(self._flash_job)
            self.alert_lbl.configure(background=self.bg_color)

        icon = load_icon(cur["weather"][0]["icon"])
        self.current_icon.config(image=icon); self.current_icon.image = icon
        temp = round(cur["temp"])
        if self.prefs["units"]["temperature"] == "metric":
            temp = round((temp-32)*5/9)
        self.current_lbl.config(text=f"{temp}°")

        today_hi = round(daily[0]["temp"]["max"])
        today_lo = round(daily[0]["temp"]["min"])
        if self.prefs["units"]["temperature"] == "metric":
            today_hi = round((today_hi-32)*5/9)
            today_lo = round((today_lo-32)*5/9)
        pop = int(daily[0].get("pop",0)*100)
        hum = cur.get("humidity",0)
        uv  = cur.get("uvi",0)
        self.details_lbl.config(
            text=f"H:{today_hi} L:{today_lo}   Precip:{pop}%   Humidity:{hum}%   UV:{uv}"
        )

        # City-local timezone offset is injected by WeatherAPI
        self.tz_offset = cur.get("timezone", 0)

        sr = datetime.fromtimestamp(cur["sunrise"]).strftime("%I:%M %p")
        ss = datetime.fromtimestamp(cur["sunset"]).strftime("%I:%M %p")
        self.sunrise_lbl.config(text=f"{t('sunrise', lang)}: {sr}")
        self.sunset_lbl.config(text=f"{t('sunset',  lang)}:  {ss}")

        # Update forecast cards
        for i,card in enumerate(self.five_cards):
            if i < len(daily):
                d = daily[i]
                img2 = load_icon(d["weather"][0]["icon"])
                card[0].config(image=img2); card[0].image = img2
                day = datetime.fromtimestamp(d["dt"]).strftime("%a")
                hi2 = round(d["temp"]["max"])
                lo2 = round(d["temp"]["min"])
                if self.prefs["units"]["temperature"] == "metric":
                    hi2 = round((hi2-32)*5/9)
                    lo2 = round((lo2-32)*5/9)
                pop2 = int(d.get("pop",0)*100)
                card[1].config(text=day)
                card[2].config(text=f"H:{hi2} L:{lo2}")
                card[3].config(text=f"{pop2}% {t('rain_word', lang)}")

        # Update forecast table
        for r in self.tree.get_children(): self.tree.delete(r)
        for d in daily:
            day = datetime.fromtimestamp(d["dt"]).strftime("%a %m/%d")
            hi3 = round(d["temp"]["max"])
            lo3 = round(d["temp"]["min"])
            if self.prefs["units"]["temperature"] == "metric":
                hi3 = round((hi3-32)*5/9)
                lo3 = round((lo3-32)*5/9)
            pop3 = int(d.get("pop",0)*100)
            self.tree.insert("", "end",
                             values=(day, f"{hi3}°", f"{lo3}°", f"{pop3}%"))

        show_alerts(alerts, self.alerts_frame,
                    {"bg":self.bg_color, "fg":self.fg_color})
        self._daily = daily
        self._plot_chart()

    # ---------- Clock (status bar only) ----------
    def _update_clock(self):
        now = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=self.tz_offset)
        date_str = now.strftime("%A, %b %d, %Y")
        time_str = now.strftime("%I:%M %p")
        tz_label = f"UTC{'+' if self.tz_offset//3600>=0 else ''}{self.tz_offset//3600}"
        self.status.config(text=f"{date_str} — {time_str}  ({tz_label})")
        self.after(60000, self._update_clock)

    def _flash_banner(self):
        color = "red" if self._flash_state else self.bg_color
        self.alert_lbl.configure(background=color)
        self._flash_state = not self._flash_state
        self._flash_job = self.after(FLASH_INTERVAL, self._flash_banner)

    # ---------- Charting ----------
    def _plot_chart(self):
        lang = self.prefs["language"]
        freq = self.freq.get()

        if freq == "daily":
            subset = self._daily[:1]
            subtitle = t("chart_daily", lang)
        elif freq == "30_day":
            subset = self._daily[:30]  # One Call may provide fewer than 30; we show what we have
            subtitle = t("chart_30day", lang)
        else:
            subset = self._daily[:7]
            subtitle = t("chart_7day", lang)

        dates = [datetime.fromtimestamp(d["dt"]).strftime("%m/%d") for d in subset]
        # prefer "day" temp if present, else fallback to max
        temps_raw = [d["temp"].get("day", d["temp"]["max"]) for d in subset]
        is_metric = (self.prefs["units"]["temperature"] == "metric")
        temps = [round((t-32)*5/9) for t in temps_raw] if is_metric else temps_raw
        precip = [int(d.get("pop",0)*100) for d in subset]
        humid = [d.get("humidity",0) for d in subset]

        chart_type = self.chart_type.get()
        self.ax.clear()
        ax2 = self.ax.twinx()
        self.ax.set_title(f"{t('chart_title', lang)} — {subtitle}")
        self.ax.set_ylabel("Temp / Precip (%)")
        ax2.set_ylabel("Humidity (%)")

        temp_label = t("temp_label_c", lang) if is_metric else t("temp_label_f", lang)

        if chart_type in ("line", "both"):
            self.ax.plot(dates, temps, marker="o", label=temp_label)
            self.ax.plot(dates, precip, marker="x", linestyle="--", label="Precip (%)")
            ax2.plot(dates, humid, marker="s", linestyle=":", color="tab:blue", label="Humidity (%)")

        if chart_type in ("bar", "both"):
            width = 0.35
            x = list(range(len(dates)))
            self.ax.bar([i - width/2 for i in x], temps, width=width, alpha=0.6, label=temp_label)
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
