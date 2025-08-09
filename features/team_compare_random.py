# features/team_compare_random.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import random
import pandas as pd

ORANGE = "#FF8800"  # accent to match your app
BLUE   = "#00AAFF"

# Column alias → canonical name
ALIASES = {
    "city": ["city", "name", "location", "town"],
    "state": ["state", "region", "province", "state_code"],
    "country": ["country", "country_code", "nation"],
    "temp": ["temp", "temperature", "temp_f", "current_temp_f", "current_temp", "temperature_f"],
    "feels_like": ["feels_like", "feelslike", "app_temp", "apparent_temp"],
    "humidity": ["humidity", "hum", "rh"],
    "pop": ["pop", "precip_prob", "rain_chance", "precipitation_probability"],
    "pressure": ["pressure", "press", "baro"],
    "wind_speed": ["wind_speed", "wind", "wind_mph", "wind_speed_mph"],
    "wind_deg": ["wind_deg", "wind_direction", "wind_dir_deg"],
    "weather_desc": ["weather", "conditions", "description", "desc", "summary"],
    "sunrise": ["sunrise", "sunrise_local"],
    "sunset": ["sunset", "sunset_local"],
    "time_local": ["local_time", "time_local", "as_of", "timestamp_local"],
}

PREFERRED_COL_ORDER = [
    "city", "state", "country", "weather_desc", "temp", "feels_like",
    "humidity", "pop", "pressure", "wind_speed", "wind_deg", "sunrise", "sunset", "time_local"
]

NUMERIC_COLS = {"temp", "feels_like", "humidity", "pop", "pressure", "wind_speed", "wind_deg"}


def _resolve_name(col: str) -> str:
    c = col.strip().lower().replace(" ", "_")
    for k, alist in ALIASES.items():
        if c == k or c in alist:
            return k
    return c  # keep unknowns (they won't be used unless shared)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    # Rename columns to canonical keys
    rename_map = {c: _resolve_name(c) for c in df.columns}
    ndf = df.rename(columns=rename_map).copy()

    # Coerce numeric cols
    for col in NUMERIC_COLS:
        if col in ndf.columns:
            ndf[col] = pd.to_numeric(ndf[col], errors="coerce")

    # Coerce pop to 0-100 integers (if likely in 0–1, multiply by 100)
    if "pop" in ndf.columns:
        # Detect fraction vs percent
        sample = ndf["pop"].dropna()
        if not sample.empty:
            frac_like = (sample <= 1).mean() > 0.5
            if frac_like:
                ndf["pop"] = (ndf["pop"] * 100).round()
        ndf["pop"] = ndf["pop"].round()

    # Ensure a weather description column
    if "weather_desc" in ndf.columns:
        ndf["weather_desc"] = ndf["weather_desc"].astype(str)

    # Drop rows that are completely useless (no temp and no description)
    if "temp" in ndf.columns or "weather_desc" in ndf.columns:
        keep_cols = [c for c in ["temp", "weather_desc"] if c in ndf.columns]
        ndf = ndf.dropna(subset=keep_cols, how="all")

    return ndf.reset_index(drop=True)


def _list_csvs(folder: Path):
    return sorted([p for p in folder.glob("*.csv") if p.is_file()])


def _sample_valid_row(df: pd.DataFrame, tries: int = 10) -> pd.Series | None:
    if df is None or df.empty:
        return None
    candidates = df.dropna(how="all")
    if candidates.empty:
        return None
    idxs = list(candidates.index)
    for _ in range(min(tries, len(idxs))):
        row = candidates.loc[random.choice(idxs)]
        # require at least something meaningful
        if any([
            pd.notna(row.get("temp", None)),
            str(row.get("weather_desc", "")).strip() != ""
        ]):
            return row
    # fallback to first non-empty
    return candidates.iloc[0]


def _recommendation(row: pd.Series, is_metric: bool = False) -> str:
    desc = str(row.get("weather_desc", "")).lower()
    temp = row.get("temp")
    pop = row.get("pop", 0)
    try:
        temp = float(temp) if pd.notna(temp) else None
    except Exception:
        temp = None

    if temp is not None and is_metric:
        # input likely in °F in team CSVs; leave as-is unless explicitly metric
        pass

    if "snow" in desc or "sleet" in desc:
        return "Bundle up and enjoy a cozy café."
    if "rain" in desc or pop and float(pop) >= 40:
        return "Grab an umbrella—maybe explore a museum."
    if temp is not None and 60 <= float(temp) <= 85 and ("clear" in desc or "sun" in desc):
        return "Perfect day for a park walk or outdoor café!"
    return "Dress comfortably and have a great day."


def _song_suggestion(row: pd.Series) -> tuple[str, str]:
    """Return (title - artist, mood_tag) based on weather/precip."""
    desc = str(row.get("weather_desc", "")).lower()
    temp = row.get("temp")
    pop = row.get("pop", 0)
    try:
        t = float(temp) if pd.notna(temp) else None
    except Exception:
        t = None

    # Prioritize condition keywords
    if "snow" in desc:
        return ("Let It Snow! - Ella Fitzgerald", "Jazz")
    if "rain" in desc or (pop and float(pop) >= 50):
        return ("Umbrella - Rihanna", "Pop/R&B")
    if "storm" in desc or "thunder" in desc:
        return ("Stronger - Kanye West", "Hip-Hop")
    if "cloud" in desc:
        return ("Blinding Lights - The Weeknd", "Pop")
    if "clear" in desc or "sun" in desc:
        # temp-based happy picks
        if t is not None and t >= 72:
            return ("Happy - Pharrell Williams", "Happy Pop")
        return ("Can’t Stop the Feeling! - Justin Timberlake", "Pop")

    # Fallback
    return ("Good as Hell - Lizzo", "R&B/Pop")


class TeamCompareRandomFrame(tk.Frame):
    """
    Themed comparison frame with:
      - Directory picker
      - Compare Random (shared columns only)
      - Song suggestion
      - Fun Mode (Quiz): “Which city is warmer today?” with score
    """

    def __init__(self, master, default_dir: str | None = None):
        super().__init__(master, bg=self._get_bg(master))
        self._bg = self._get_bg(master)
        self._fg = self._get_fg(master)
        self._accent = ORANGE

        self.dir_var = tk.StringVar(value=default_dir or "")
        self.score = 0
        self.rounds = 0
        self.fun_cache = None  # store last left/right tuples for quiz reveal

        # --- Header ---
        top = tk.Frame(self, bg=self._bg)
        top.pack(fill="x")
        tk.Label(top, text="Team Data Folder:", bg=self._bg, fg=self._fg, font=(None, 12, "bold")).pack(side="left", padx=(4, 6))
        self.ent_dir = ttk.Entry(top, textvariable=self.dir_var, width=70)
        self.ent_dir.pack(side="left", padx=4, pady=8)
        ttk.Button(top, text="Browse…", command=self._browse).pack(side="left", padx=4)
        ttk.Button(top, text="Compare Random", command=self.compare_random).pack(side="left", padx=6)

        # Fun mode controls
        fm = tk.Frame(self, bg=self._bg)
        fm.pack(fill="x", pady=(4, 0))
        self.fun_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fm, text="Fun Mode (Quiz)", variable=self.fun_var, command=self._toggle_fun).pack(side="left", padx=4)
        self.btn_round = ttk.Button(fm, text="Play Round", command=self.play_round, state="disabled")
        self.btn_round.pack(side="left", padx=6)
        self.lbl_score = tk.Label(fm, text="Score: 0 / 0", bg=self._bg, fg=self._fg, font=(None, 12))
        self.lbl_score.pack(side="right", padx=6)

        # Selected file labels
        sel = tk.Frame(self, bg=self._bg)
        sel.pack(fill="x", pady=(6, 4))
        self.file_left = tk.Label(sel, text="Left: —", bg=self._bg, fg=self._fg, font=(None, 11, "bold"))
        self.file_left.pack(side="left", padx=6)
        self.file_right = tk.Label(sel, text="Right: —", bg=self._bg, fg=self._fg, font=(None, 11, "bold"))
        self.file_right.pack(side="right", padx=6)

        # Table (Field + Left + Right)
        table_frame = tk.Frame(self, bg=self._bg)
        table_frame.pack(fill="both", expand=True, padx=6, pady=6)

        cols = ("field", "left", "right")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree.heading("field", text="Field")
        self.tree.heading("left",  text="Left")
        self.tree.heading("right", text="Right")
        self.tree.column("field", width=160, anchor="center")
        self.tree.column("left",  width=360, anchor="center")
        self.tree.column("right", width=360, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Song / Recommendation area
        info = tk.Frame(self, bg=self._bg)
        info.pack(fill="x", pady=(4, 8))
        self.lbl_reco = tk.Label(info, text="", bg=self._bg, fg=self._fg, font=(None, 12))
        self.lbl_reco.pack(side="left", padx=6)
        self.lbl_song = tk.Label(info, text="", bg=self._bg, fg=self._accent, font=(None, 14, "bold"))
        self.lbl_song.pack(side="right", padx=6)

        # Guess buttons (hidden unless fun mode & round active)
        guess = tk.Frame(self, bg=self._bg)
        guess.pack(fill="x", pady=(0, 4))
        self.btn_guess_left  = ttk.Button(guess, text="Guess Left",  command=lambda: self._reveal_choice("left"))
        self.btn_guess_right = ttk.Button(guess, text="Guess Right", command=lambda: self._reveal_choice("right"))
        self.btn_guess_left.pack_forget()
        self.btn_guess_right.pack_forget()

    # ---------------- UI helpers ----------------
    def _get_bg(self, widget):
        try:
            return widget.cget("bg")
        except Exception:
            return "#2E3F4F"

    def _get_fg(self, widget):
        # Walk up to find a fg_color attr set by the app; fallback to white/black based on bg
        node = widget
        while node is not None:
            fg = getattr(node, "fg_color", None)
            if fg:
                return fg
            node = getattr(node, "master", None)
        # fallback
        bg = self._get_bg(widget)
        return "#FFFFFF" if bg.lower() != "#ffffff" else "#000000"

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get() or str(Path.home()))
        if d:
            self.dir_var.set(d)

    # ---------------- Core actions ----------------
    def compare_random(self):
        folder = Path(self.dir_var.get().strip() or ".")
        if not folder.exists():
            messagebox.showerror("Folder not found", f"Cannot find: {folder}")
            return
        csvs = _list_csvs(folder)
        if len(csvs) < 2:
            messagebox.showwarning("Need more files", "Select a folder with at least two CSV files.")
            return

        left_path, right_path = random.sample(csvs, 2)
        df_l = _normalize_df(self._safe_read(left_path))
        df_r = _normalize_df(self._safe_read(right_path))
        row_l = _sample_valid_row(df_l)
        row_r = _sample_valid_row(df_r)

        if row_l is None or row_r is None:
            messagebox.showwarning("No usable data", "Could not find valid rows in one or both files.")
            return

        # update labels
        self.file_left.config(text=f"Left: {left_path.name}")
        self.file_right.config(text=f"Right: {right_path.name}")

        self._render_shared_table(row_l, row_r)

        # show rec + song for the "nicer" city (choose by higher temp)
        left_t  = float(row_l.get("temp")) if pd.notna(row_l.get("temp")) else float("-inf")
        right_t = float(row_r.get("temp")) if pd.notna(row_r.get("temp")) else float("-inf")
        best = row_l if left_t >= right_t else row_r

        rec = _recommendation(best)
        song, mood = _song_suggestion(best)
        self.lbl_reco.config(text=rec)
        self.lbl_song.config(text=f"♫ {song}  ({mood})")

        # clear quiz state
        self.fun_cache = None
        self._hide_guess_buttons()

    def _render_shared_table(self, row_l: pd.Series, row_r: pd.Series, hide_city_names: bool = False):
        # Determine shared keys (keep preferred order, then extras)
        shared = [c for c in PREFERRED_COL_ORDER if c in row_l.index and c in row_r.index]
        extras = [c for c in row_l.index.intersection(row_r.index) if c not in shared]
        cols = shared + extras
        if not cols:
            cols = sorted(list(row_l.index.intersection(row_r.index)))

        # Clear table
        for r in self.tree.get_children():
            self.tree.delete(r)

        # Render as Field → Left/Right rows
        def fmt(v, key):
            if pd.isna(v):
                return "—"
            if key == "pop":
                try:
                    return f"{int(round(float(v)))}%"
                except Exception:
                    return str(v)
            if key in ("temp", "feels_like"):
                try:
                    return f"{round(float(v))}°"
                except Exception:
                    return str(v)
            return str(v)

        for key in cols:
            left_val  = fmt(row_l.get(key, ""), key)
            right_val = fmt(row_r.get(key, ""), key)
            label_key = key.replace("_", " ").title()
            if hide_city_names and key in ("city", "state", "country"):
                left_val = right_val = "???"
            self.tree.insert("", "end", values=(label_key, left_val, right_val))

    def _safe_read(self, path: Path) -> pd.DataFrame | None:
        try:
            return pd.read_csv(path)
        except Exception:
            # try with latin-1 as fallback
            try:
                return pd.read_csv(path, encoding="latin-1")
            except Exception:
                return None

    # ---------------- Fun Mode (Quiz) ----------------
    def _toggle_fun(self):
        enabled = self.fun_var.get()
        self.btn_round.config(state="normal" if enabled else "disabled")
        if not enabled:
            self._hide_guess_buttons()
            self.fun_cache = None

    def play_round(self):
        """Start a quiz round: pick two files, sample rows, hide city names, and allow a guess."""
        folder = Path(self.dir_var.get().strip() or ".")
        csvs = _list_csvs(folder)
        if len(csvs) < 2:
            messagebox.showwarning("Need more files", "Select a folder with at least two CSV files.")
            return

        left_path, right_path = random.sample(csvs, 2)
        df_l = _normalize_df(self._safe_read(left_path))
        df_r = _normalize_df(self._safe_read(right_path))
        row_l = _sample_valid_row(df_l)
        row_r = _sample_valid_row(df_r)
        if row_l is None or row_r is None:
            messagebox.showwarning("No usable data", "Could not find valid rows in one or both files.")
            return

        # Update labels (hide city names in table; keep file names at top)
        self.file_left.config(text=f"Left: {left_path.name}")
        self.file_right.config(text=f"Right: {right_path.name}")
        self._render_shared_table(row_l, row_r, hide_city_names=True)

        # store for reveal
        self.fun_cache = (left_path, right_path, row_l, row_r)
        self._show_guess_buttons()
        self.lbl_reco.config(text="Which city is warmer today?")
        self.lbl_song.config(text="")

    def _show_guess_buttons(self):
        self.btn_guess_left.pack(side="left", padx=6)
        self.btn_guess_right.pack(side="left", padx=6)

    def _hide_guess_buttons(self):
        self.btn_guess_left.pack_forget()
        self.btn_guess_right.pack_forget()

    def _reveal_choice(self, guess_side: str):
        if not self.fun_cache:
            return
        left_path, right_path, row_l, row_r = self.fun_cache

        left_t  = float(row_l.get("temp")) if pd.notna(row_l.get("temp")) else float("-inf")
        right_t = float(row_r.get("temp")) if pd.notna(row_r.get("temp")) else float("-inf")
        correct_side = "left" if left_t >= right_t else "right"
        correct_row  = row_l if correct_side == "left" else row_r

        self.rounds += 1
        if guess_side == correct_side:
            self.score += 1
            msg = "✅ Correct!"
        else:
            msg = "❌ Not quite."

        # Re-render table with city names revealed
        self._render_shared_table(row_l, row_r, hide_city_names=False)

        # Show recommendation and song
        rec = _recommendation(correct_row)
        song, mood = _song_suggestion(correct_row)
        self.lbl_reco.config(text=f"{msg} {rec}")
        self.lbl_song.config(text=f"♫ {song}  ({mood})")

        self.lbl_score.config(text=f"Score: {self.score} / {self.rounds}")
        self._hide_guess_buttons()
        self.fun_cache = None
