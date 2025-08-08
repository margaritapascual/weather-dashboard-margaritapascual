# features/team_compare_random.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import random
import pandas as pd

# --- Preferences (tweak anytime) ---
PREFERRED_GENRES = ["happy", "r&b", "hip-hop", "pop", "jazz"]

# --- Song buckets by weather category (tagged with genres) ---
SONG_BUCKETS = {
    "rain": [
        {"title":"Umbrella","artist":"Rihanna","genres":["pop","r&b","happy"]},
        {"title":"No Rain","artist":"Blind Melon","genres":["pop","happy"]},
        {"title":"Rainy Days","artist":"Mary J. Blige","genres":["r&b"]},
    ],
    "snow": [
        {"title":"Let It Snow!","artist":"Frank Sinatra","genres":["jazz","happy"]},
        {"title":"Snow (Hey Oh)","artist":"Red Hot Chili Peppers","genres":["pop"]},
        {"title":"My Favorite Things","artist":"John Coltrane","genres":["jazz"]},
    ],
    "storm": [
        {"title":"Thunderstruck","artist":"AC/DC","genres":["pop"]},
        {"title":"Lightning Bolt","artist":"Jake Bugg","genres":["pop"]},
        {"title":"All of the Lights","artist":"Kanye West","genres":["hip-hop","pop"]},
    ],
    "clear": [
        {"title":"Here Comes the Sun","artist":"The Beatles","genres":["pop","happy"]},
        {"title":"Walking on Sunshine","artist":"Katrina & The Waves","genres":["pop","happy"]},
        {"title":"Lovely Day","artist":"Bill Withers","genres":["r&b","happy"]},
    ],
    "clouds": [
        {"title":"Cloud 9","artist":"Jamiroquai","genres":["pop","funk","happy"]},
        {"title":"Blue Skies","artist":"Ella Fitzgerald","genres":["jazz","happy"]},
        {"title":"Sunday Best","artist":"Surfaces","genres":["pop","happy"]},
    ],
    "wind": [
        {"title":"Blowin’ in the Wind","artist":"Bob Dylan","genres":["pop"]},
        {"title":"The Way You Make Me Feel","artist":"Michael Jackson","genres":["pop","r&b","happy"]},
        {"title":"September","artist":"Earth, Wind & Fire","genres":["r&b","happy","pop"]},
    ],
    "hot": [
        {"title":"Heat Waves","artist":"Glass Animals","genres":["pop"]},
        {"title":"Hot in Herre","artist":"Nelly","genres":["hip-hop","pop"]},
        {"title":"Uptown Funk","artist":"Mark Ronson ft. Bruno Mars","genres":["pop","r&b","happy"]},
    ],
    "cold": [
        {"title":"Ice Ice Baby","artist":"Vanilla Ice","genres":["hip-hop","pop","happy"]},
        {"title":"Suavemente","artist":"Elvis Crespo","genres":["pop","happy"]},
        {"title":"Put Your Records On","artist":"Corinne Bailey Rae","genres":["r&b","pop","happy"]},
    ],
    "fog": [
        {"title":"Feeling Good","artist":"Nina Simone","genres":["jazz","happy"]},
        {"title":"Golden","artist":"Jill Scott","genres":["r&b","happy"]},
        {"title":"Sunflower","artist":"Post Malone & Swae Lee","genres":["hip-hop","pop","happy"]},
    ],
    "default": [
        {"title":"Weather With You","artist":"Crowded House","genres":["pop","happy"]},
        {"title":"Good as Hell","artist":"Lizzo","genres":["pop","hip-hop","happy"]},
        {"title":"Happy","artist":"Pharrell Williams","genres":["pop","happy"]},
    ],
}

def _norm_genre(g: str) -> str:
    return g.strip().lower().replace(" ", "-")

def _pick_song(category: str, preferred_genres=PREFERRED_GENRES):
    prefs = {_norm_genre(g) for g in preferred_genres}
    songs = SONG_BUCKETS.get(category, []) or SONG_BUCKETS["default"]
    filtered = [s for s in songs if any(_norm_genre(g) in prefs for g in s["genres"])]
    s = random.choice(filtered or songs)
    return s["title"], s["artist"]

# ---------- Robust CSV + row helpers ----------
def _load_csv_paths(data_dir: Path):
    """Find CSVs recursively; accept .csv/.CSV etc."""
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {data_dir}")
    return [p for p in data_dir.rglob("*") if p.is_file() and p.suffix.lower() == ".csv"]

def _sample_random_row(df: pd.DataFrame):
    my_row = df.sample(1).iloc[0]
    print (my_row)
    return my_row

def _row_map(row: pd.Series) -> dict:
    """Normalize keys: lowercase, spaces->_, strip."""
    return {str(k).strip().lower().replace(" ", "_"): row[k] for k in row.index}

def _first(r: dict, *names, default=""):
    """Return first present value (by alt names) from a normalized row map."""
    for n in names:
        key = n.lower().replace(" ", "_")
        if key in r and pd.notna(r[key]):
            return r[key]
    return default

# ---------- Weather classification ----------
def _classify_weather(row) -> str:
    r = _row_map(row)
    desc = str(_first(r, "weather", "weather_desc", "conditions", "description", default="")).lower()

    # Precip probability & amount
    pop = _first(r, "pop", default=0.0)
    try:
        pop = float(pop)
        if pop <= 1: pop *= 100
    except Exception:
        pop = 0.0
    try:
        precip = float(_first(r, "precipitation", "precip", "rain", default=0.0))
    except Exception:
        precip = 0.0

    # Wind
    try:
        wind = float(_first(r, "wind_speed", "wind", "wind_mph", "wind_speed_mph", default=0.0))
    except Exception:
        wind = 0.0

    # Temp
    try:
        temp = float(_first(r, "temp", "temperature", "feels_like", "temp_f", "tempf", default=0.0))
    except Exception:
        temp = 0.0

    # Snow fields (if present)
    snow_amt = 0.0
    for k in ("snow", "snow_1h", "snow_3h"):
        if k in r:
            try: snow_amt = max(snow_amt, float(r.get(k, 0)))
            except Exception: pass

    if any(k in desc for k in ("thunder", "storm", "lightning")):
        return "storm"
    if "snow" in desc or snow_amt > 0:
        return "snow"
    if any(k in desc for k in ("rain","drizzle","shower")) or precip > 0 or pop >= 50:
        return "rain"
    if any(k in desc for k in ("fog","mist","haze","smoke")):
        return "fog"
    if wind >= 20 or "wind" in desc:
        return "wind"
    if temp >= 90:
        return "hot"
    if temp <= 40:
        return "cold"
    if any(k in desc for k in ("clear","sun")):
        return "clear"
    if "cloud" in desc or "overcast" in desc:
        return "clouds"
    return "default"

def _recommend(row) -> str:
    category = _classify_weather(row)
    title, artist = _pick_song(category, PREFERRED_GENRES)

    if category == "rain":
        msg = "Likely rain—umbrella/museum day."
    elif category == "snow":
        msg = "Snowy—bundle up and watch for slick roads."
    elif category == "storm":
        msg = "Storms around—limit outdoor plans."
    elif category == "fog":
        msg = "Foggy—take it easy on the roads."
    elif category == "wind":
        msg = "Windy—secure hats/umbrellas."
    elif category == "hot":
        msg = "Very warm—hydrate and take shade breaks."
    elif category == "cold":
        msg = "Chilly—layers recommended."
    elif category == "clear":
        msg = "Sunny and pleasant—great day to be outside."
    elif category == "clouds":
        msg = "Cloudy but fine for most plans."
    else:
        msg = "Dress comfortably."

    return f"{msg}  ♪ “{title}” — {artist}"

# ---------- UI ----------
class TeamCompareRandomFrame(ttk.Frame):
    def __init__(self, parent, default_dir: str | Path | None = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._init_theme()

        # Default directory guess if not provided
        if default_dir is None:
            for guess in [Path("../Capstone_Team_8/data"), Path("Team Data"), Path("data")]:
                if guess.exists():
                    default_dir = str(guess.resolve())
                    break
        self.dir_var = tk.StringVar(value=str(default_dir) if default_dir else "")

        self._build_ui()

    # Theming to match your app
    def _init_theme(self):
        root = self.winfo_toplevel()
        self._bg = getattr(root, "bg_color", "#FFFFFF")
        self._fg = getattr(root, "fg_color", "#000000")
        self._font = ("Helvetica", 12)

        style = ttk.Style(self)
        try: style.theme_use("clam")
        except Exception: pass

        style.configure("TeamRandom.TFrame", background=self._bg)
        style.configure("TeamRandom.TLabel", background=self._bg, foreground=self._fg, font=self._font)
        style.configure("TeamRandom.TButton", font=self._font)
        style.configure("TeamRandom.TEntry", fieldbackground=self._bg, foreground=self._fg, insertcolor=self._fg)
        style.configure("TeamRandom.Treeview", background=self._bg, fieldbackground=self._bg, foreground=self._fg, rowheight=24)
        style.configure("TeamRandom.Treeview.Heading", background=self._bg, foreground=self._fg, font=(self._font[0], self._font[1], "bold"))

        self.configure(style="TeamRandom.TFrame")

    def _build_ui(self):
        r = 0
        ttk.Label(self, text="Team Data Folder:", style="TeamRandom.TLabel").grid(row=r, column=0, sticky="w", padx=(0,6), pady=(6,0))
        ttk.Entry(self, textvariable=self.dir_var, width=60, style="TeamRandom.TEntry").grid(row=r, column=1, sticky="ew", pady=(6,0))
        ttk.Button(self, text="Browse…", command=self._browse, style="TeamRandom.TButton").grid(row=r, column=2, padx=6, pady=(6,0))
        ttk.Button(self, text="Compare Random", command=self._compare, style="TeamRandom.TButton").grid(row=r, column=3, pady=(6,0))
        r += 1

        # Status line: shows folder, file count, picks
        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, style="TeamRandom.TLabel").grid(row=r, column=0, columnspan=4, sticky="w", pady=(6,6))
        r += 1

        cols = ("file","datetime","city","state","country","temp","feels","hum","precip","wind","desc")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8, style="TeamRandom.Treeview")
        headings = {
            "file":"File","datetime":"Datetime","city":"City","state":"State","country":"Country",
            "temp":"Temp(°F)","feels":"Feels(°F)","hum":"Humidity","precip":"Precip","wind":"Wind","desc":"Weather"
        }
        for cid, text in headings.items():
            self.tree.heading(cid, text=text, anchor="w")
            self.tree.column(cid, width=120, stretch=True, anchor="w")
        self.tree.grid(row=r, column=0, columnspan=4, sticky="nsew", pady=(10,0))
        r += 1

        self.notes = tk.Text(self, height=5, wrap="word", borderwidth=0, highlightthickness=1)
        self.notes.grid(row=r, column=0, columnspan=4, sticky="nsew", pady=(10,10))
        self.notes.configure(bg=self._bg, fg=self._fg, insertbackground=self._fg, font=self._font)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(r-1, weight=1)
        self.rowconfigure(r, weight=1)

    def _browse(self):
        start = self.dir_var.get() or str(Path.home())
        path = filedialog.askdirectory(
            title="Select Team Data folder",
            initialdir=start
        )
        if path:
            self.dir_var.set(path)


    def _compare(self):
        try:
            data_dir = Path(self.dir_var.get()).expanduser().resolve()
            csvs = _load_csv_paths(data_dir)
            if len(csvs) < 2:
                self.status_var.set(f"Using: {data_dir} — found {len(csvs)} CSVs (need ≥ 2)")
                messagebox.showwarning("Need more files", f"Found {len(csvs)} CSVs in {data_dir} (need ≥ 2).")
                return

            f1, f2 = random.sample(csvs, 2)
            self.status_var.set(f"Using: {data_dir} — found {len(csvs)} CSVs | Picked: {f1.name} vs {f2.name}")

            df1, df2 = pd.read_csv(f1), pd.read_csv(f2)
            row1, row2 = _sample_random_row(df1), _sample_random_row(df2)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear table
        for i in self.tree.get_children():
            self.tree.delete(i)

        def insert(file_path: Path, row: pd.Series):
            r = _row_map(row)
            self.tree.insert("", "end", values=(
                file_path.name,
                _first(r, "datetime"),
                _first(r, "city"),
                _first(r, "state"),
                _first(r, "country"),
                _first(r, "temperature","temp","temp_f","tempf"),
                _first(r, "feels_like","apparent_temperature","heat_index"),
                _first(r, "humidity","hum","rh"),
                _first(r, "precipitation","precip","rain","pop"),
                _first(r, "wind_speed","wind","wind_mph","wind_speed_mph"),
                _first(r, "weather","weather_desc","conditions","description"),
            ))

        insert(f1, row1)
        insert(f2, row2)

        # Notes with upbeat, genre-aware song based on EACH city’s row
        self.notes.delete("1.0","end")
        self.notes.insert("end", f"{f1.stem}: {_recommend(row1)}\n{f2.stem}: {_recommend(row2)}\n")
