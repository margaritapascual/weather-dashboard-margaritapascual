# main.py
"""Main application entry point"""

import sys
from pathlib import Path

# allow imports from project root
sys.path.append(str(Path(__file__).parent))

from config import Config
from core import WeatherAPI, StorageManager, DataProcessor
from gui import MainWindow
from features import load_features

class WeatherDashboardApp:
    """Main application controller"""
    
    def __init__(self):
        # load everything from .env
        cfg = Config.from_env()
        
        # Initialize core modules with cfg values
        self.api       = WeatherAPI(api_key=cfg.api_key,
                                    timeout=cfg.request_timeout)
        self.storage   = StorageManager(db_path=cfg.database_path)
        self.processor = DataProcessor()
        
        # Initialize GUI
        self.window = MainWindow()
        
        # Keep a ref to cfg for later if needed
        self.cfg = cfg
        
        # Load features based on cfg.selected_features
        self.features = {}
        for feat in cfg.selected_features:
            klass = load_features(feat)
            if klass:
                inst = klass({
                    "api":       self.api,
                    "storage":   self.storage,
                    "processor": self.processor
                })
                inst.initialize(self.window.feature_frame)
                self.features[feat] = inst
        
        # Setup GUI callbacks
        self.window.register_callback('search',  self.handle_search)
        self.window.register_callback('refresh', self.handle_refresh)
    
    def handle_search(self, city: str):
        raw = self.api.fetch_weather(city)
        if not raw:
            return
        processed = self.processor.process_api_response(raw)
        self.storage.save_weather(raw)
        self.window.display_weather(processed)
        for feat in self.features.values():
            feat.update(processed)
    
    def run(self):
        self.window.run()

if __name__ == "__main__":
    WeatherDashboardApp().run()
