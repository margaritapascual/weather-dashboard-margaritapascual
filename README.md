# Margarita’s Weather Dashboard

A polished Tkinter app that shows current weather, forecasts, alerts, charts, and a fun Team Compare popup that samples teammates’ CSVs and suggests a song based on the weather.

✨ Features
Current conditions with icons, highs/lows, UV, humidity, precipitation %

5-day cards + detailed forecast table

Alerts banner with flashing indicator

Forecast chart (Daily, Weekly/7-Day, 30-Day)

Team Compare (Random): picks two team CSVs, compares shared fields only, validates rows (no blanks), gives a weather-based song suggestion; optional Quiz Mode

Theme toggle (Light/Dark), language toggle (EN/ES), units (°F/°C)

Preferences saved to user_preferences.json

🚀 Setup
bash
Copy
Edit
git clone <https://github.com/margaritapascual/weather-dashboard-margaritapascual.git>
cd weather-dashboard-margaritapascual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # put your OpenWeatherMap key in .env
python main.py
🧑‍🏫 Usage
Enter a city and click Update.

Use Settings to change theme, units, and language.

Team Compare (top bar):

Choose your team CSV folder.

Compare Random selects two CSVs and valid rows (no blanks), showing shared columns.

A weather-based song suggestion appears at the bottom.

Quiz Mode (optional): “Which city is warmer?” mini-game.

Suggested local folder:
/Users/margaritapascual/JTC/Pathways/weather-dashboard-margaritapascual/Team Data

📦 Build (optional)
bash
Copy
Edit
python build.py
🎬 Demo Video
Watch on Loom

📑 Slide Deck
View on Google Drive

🔖 Versioning
Current release: v1.0

📂 Structure
graphql
Copy
Edit
core/                  # API + predictor
features/              # icons, alerts, team compare
tools/                 # maintenance scripts
data/                  # local data; heavy files archived under data/archive/
Team Data/             # local CSVs for compare (not committed)
gui.py                 # main Tk app
main.py                # entry point
🛠 Troubleshooting
If the app can’t find your key, check .env.

If charts crowd, resize the window; axes are responsive.