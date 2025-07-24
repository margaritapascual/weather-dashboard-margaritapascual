# build.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--add-data=features/icons;features/icons',
    '--name=WeatherDashboard'
])