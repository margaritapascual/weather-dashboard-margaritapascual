from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
candidates = ["weather_reading_margarita.csv", "weather.csv"]

input_path = None
for name in candidates:
    p = DATA_DIR / name
    if p.exists():
        input_path = p
        break

if input_path is None:
    available = "\n  - ".join(sorted(x.name for x in DATA_DIR.iterdir()))
    raise FileNotFoundError(
        f"Could not find any of {candidates} in {DATA_DIR}.\nAvailable files:\n  - {available}"
    )

cols = [
    "datetime","city","state","country",
    "temperature","feels_like","humidity","precipitation",
    "pressure","wind_speed","wind_deg","weather_desc","sunrise","sunset"
]

df = pd.read_csv(input_path, header=None, names=cols)
df['datetime'] = pd.to_datetime(df['datetime'], format='%m-%d-%y %H:%M:%S').dt.strftime('%m-%d-%Y %H:%M:%S')
df = df[cols]
# write next to data/ (change to DATA_DIR/'weather_data.csv' if you prefer in-data)
df.to_csv(Path(__file__).resolve().parent.parent / "weather_data.csv", index=False)
print(f"Wrote weather_data.csv from {input_path.name}")
