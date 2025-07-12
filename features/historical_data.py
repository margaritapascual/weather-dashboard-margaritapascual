import os, csv
from datetime import datetime

def save_history(city: str, daily: list[dict], path: str = "./data/history.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = ["city", "date", "temp", "humidity", "description"]
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        for d in daily:
            writer.writerow({
                "city": city,
                "date": datetime.fromtimestamp(d["dt"]).isoformat(),
                "temp": d["temp"]["day"],
                "humidity": d.get("humidity"),
                "description": d["weather"][0]["description"],
            })
