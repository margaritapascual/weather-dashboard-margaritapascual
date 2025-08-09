# tools/train_baseline.py

import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

# 1) Load without parse_dates so we can inspect the headers
df = pd.read_csv("data/history_cleaned.csv")
print("Columns in history_cleaned.csv:", list(df.columns))

# 2) Figure out your timestamp column
if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"])
elif "date" in df.columns:
    # e.g. if you have a 'date' column in YYYY-MM-DD or similar
    df["datetime"] = pd.to_datetime(df["date"])
elif "dt" in df.columns:
    # e.g. UNIX timestamps
    df["datetime"] = pd.to_datetime(df["dt"], unit="s")
else:
    raise KeyError(
        "Could not find a timestamp column in history_cleaned.csv. "
        "Expected one of ['datetime','date','dt'], but got: "
        f"{list(df.columns)}"
    )

# 3) Compute days since first record
first_day = df["datetime"].min()
df["day"] = (df["datetime"] - first_day).dt.days

# 4) Train the model
model = LinearRegression().fit(df[["day"]], df["temp"])

# 5) Save it for your GUI
joblib.dump(model, "data/temp_model.pkl")
print("✅ Model saved to data/temp_model.pkl")
