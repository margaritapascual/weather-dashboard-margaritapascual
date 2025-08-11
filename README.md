# Margarita’s Weather Dashboard

A polished Tkinter app that shows current weather, forecasts, alerts, charts, and a fun Team Compare popup that samples teammates’ CSVs and suggests a song based on the weather.

✨ Features

- Current conditions with icons, highs/lows, UV, humidity, precipitation %
- 5-day forecast cards + detailed forecast table
- Alerts banner with flashing indicator
- Forecast chart (Daily, Weekly/7-Day, 30-Day)
- Team Compare (Random): Picks two team CSVs, compares shared fields only, validates rows (no blanks), gives a weather-based song suggestion; optional Quiz Mode
- Theme toggle (Light/Dark), language toggle (EN/ES), units (°F/°C)
- Preferences saved to user_preferences.json

## 🚀 Setup

### Clone the repository

git clone <https://github.com/margaritapascual/weather-dashboard-margaritapascual.git>

### Navigate into the project folder

cd weather-dashboard-margaritapascual

### Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Add your OpenWeatherMap API key

cp .env.example .env   # Open .env and insert your API key

### Run the app

python main.py

## 🧑‍🏫 Usage

Enter a city and click Update.
Use Settings to change theme, units, and language.
Team Compare (top bar):

- Choose your team CSV folder.
- “Compare Random” selects two CSVs and valid rows (no blanks), showing shared columns.
- A weather-based song suggestion appears at the bottom.
Quiz Mode (optional): “Which city is warmer?” mini-game.
💡 Suggested local folder for team CSVs:
/Users/margaritapascual/JTC/Pathways/weather-dashboard-margaritapascual/Team Data

## 📦 Build (optional)

python build.py

## 🎬 Demo Video

Watch on Loom: <https://www.loom.com/share/468fbee8180943d6b51778cb1ec955e7?sid=e64ab81c-c03a-4404-be99-c11455a8ef1e>

## 📑 Slide Deck

View on Google Drive: [Margarita's Weatherdashboard Capstone.pdf](https://drive.google.com/file/d/1NQ1d0zgKoMLa52gQIWdw7V_KZXS2ybEv/view?usp=drive_link)

## 🔖 Versioning

Current release: v1.0

## 📂 Project Structure

core/                  # API + predictor
features/              # icons, alerts, team compare
tools/                 # maintenance scripts
data/                  # local data; heavy files archived under data/archive/
Team Data/             # local CSVs for compare (not committed)
gui.py                 # main Tk app
main.py                # entry point

## 🛠 Troubleshooting

- If the app can’t find your key, check .env.
- If charts appear crowded, resize the window — axes are responsive.
