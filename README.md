# Margarita’s Weather Dashboard

A polished Tkinter app that shows current weather, forecasts, alerts, charts, and a fun **Team Compare** popup that samples teammates’ CSVs and suggests a **song** based on the weather.

## ✨ Features

- Current conditions with icons, highs/lows, UV, humidity, precip %
- 5-day cards + detailed forecast table
- Alerts banner with flashing indicator
- Forecast chart (Daily, Weekly/7-Day, 30-Day)
- **Team Compare (Random):** picks two team CSVs, compares shared fields only, validates rows (no blanks), gives a weather-based song suggestion; optional **Quiz Mode**
- Theme toggle (Light/Dark), language toggle (EN/ES), units (°F/°C)
- Preferences saved to `user_preferences.json`

## 🚀 Setup
```bash
git clone <YOUR-REPO-URL>
cd weather-dashboard-margaritapascual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # put your OpenWeatherMap key in .env
python main.py

🧑‍🏫 Usage
Enter a city and click Update.

Use Settings to change theme, units, language.

Click Team Compare (top bar):

Choose your team CSV folder.

Compare Random selects two CSVs and valid rows (no blanks), shows shared columns.

Weather-based song suggestion appears at the bottom.

Quiz Mode (optional): “Which city is warmer?” mini-game.

Suggested local folder:
/Users/margaritapascual/JTC/Pathways/weather-dashboard-margaritapascual/Team Dat📦 Build (optional)
bash
Copy
Edit
python build.py
🎬 Demo Video
https://www.loom.com/share/468fbee8180943d6b51778cb1ec955e7?sid=e2811482-44e8-44ef-be9e-7218c9d2e75e

📑 Slide Deck
https://drive.google.com/file/d/1NQ1d0zgKoMLa52gQIWdw7V_KZXS2ybEv/view?usp=drive_link

🔖 Versioning
Current release: v1.0

📂 Structure
graphql
Copy
Edit
core/                  # API + predictor
features/              # icons, alerts, team compare
tools/                 # maintenance (repo_cleaner)
data/                  # local data; heavy files archived under data/archive/
Team Data/             # local CSVs for compare (not committed)
gui.py                 # main Tk app
main.py                # entry point
🛠 Troubleshooting
If the app can’t find your key, check .env.

If charts crowd, resize the window; axes are responsive.
MD

sql
Copy
Edit

Then commit it:

```bash
git add README.md
git commit -m "docs: final README for v1.0"a