# Weather Dashboard App

A desktop application that fetches and displays current weather conditions, alerts, and multi-day forecasts ## Repository
[https://github.com/margaritapascual/weather-dashboard-margaritapascual](https://github.com/margaritapascual/weather-dashboard-margaritapascual)

## Features

- **Current Conditions** (temperature, humidity, UV index, icons)  
- **Weather Alerts** via pop-up dialogs  
- **Multi-day Forecasts**: Daily, 7-Day, and 30-Day charts (temperature, humidity, precipitation)  - **Theme Toggle** (light/dark mode)  
- **Historical Data** saved to a local SQLite database  
- **Easy Configuration** via `.env` or `config.py`

## Getting Started

### Prerequisites

- Python 3.10 or higher  
- An OpenWeatherMap API key  
- Git

### Installation

1. **Clone the repository**  

   ```bash
   python -m venv .venv 
   source .venv/bin/activate # macOS/Linux 
   .venv\Scripts\activate.bat # Windows 
   ```

2. **Install dependencies**  

   ```bash
   pip install -r requirements.txt 
   ```

3. **Configure environment variables**  

   - Copy `.env.example` to `.env`  
   - Edit `.env` to include your API key and settings:

   ```ini
   WEATHER_API_KEY=your_api_key_here 
   REQUEST_TIMEOUT=10 
   MAX_RETRIES=3 
   ```

### Usage

```bash
python main.py 
```

- Enter a city name in the input field and click **Update**.  
- Use the **Mode** buttons to switch between Daily, 7-Day Temp, and 30-Day Temp charts.  
- Toggle between light and dark themes with the **Toggle Theme** button.  

## Repository Structure

```plaintext
weather-dashboard-margaritapascual/ 
weather-dashboard-margaritapascual/
│
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
│
├─ main.py
├─ gui.py
├─ config.py
│
├─ core/
│  ├─ api/
│  │   └─ weather_api.py
│  ├─ db/
│  │   ├─ db.py
│  │   └─ weather_storage.py
│  └─ jobs/
│      └─ weather_jobs.py
│
├─ features/
│  ├─ current_conditions_icons.py
│  ├─ historical_data.py
│  ├─ temperature_graph.py
│  └─ theme_switcher.py
│
├─ data/
│  └─ weather.db
│
├─ tests/
│  └─ test_*.py
│
└─ docs/
   ├─ ui-mockups/
   │   ├─ 01-empty-launch.png
   │   ├─ 02-current-conditions.png
   │   ├─ 03-7day-icons.png
   │   ├─ 04-7day-temp-chart.png
   │   ├─ 05-30day-temp-chart.png
   │   └─ 06-dark-theme.png
   └─ timeline.md
