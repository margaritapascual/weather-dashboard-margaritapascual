#Main app logic
# main.py
"""Main application entry point"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core import WeatherAPI, StorageManager, DataProcessor
from gui import MainWindow
from features import load_features
import config

class WeatherDashboardApp:
    """Main application controller"""
    
    def __init__(self):
        # Initialize core modules
        self.api = WeatherAPI(config.API_KEY)
        self.storage = StorageManager()
        self.processor = DataProcessor()
        
        # Initialize GUI
        self.window = MainWindow()
        
        # Core modules dictionary for features
        self.core_modules = {
            'api': self.api,
            'storage': self.storage,
            'processor': self.processor
        }
        
        # Initialize features
        self.features = {}
        self.initialize_features()
        
        # Setup callbacks
        self.setup_callbacks()
    
    def initialize_features(self):
        """Load and initialize selected features"""
        for feature_name in config.SELECTED_FEATURES:
            feature_class = load_features(feature_name)
            if feature_class:
                feature = feature_class(self.core_modules)
                self.features[feature_name] = feature
                
                # Create feature UI
                feature.initialize(self.window.feature_frame)
    
    def setup_callbacks(self):
        """Setup GUI callbacks"""
        self.window.register_callback('search', self.handle_search)
        self.window.register_callback('refresh', self.handle_refresh)
    
    def handle_search(self, city: str):
        """Handle weather search"""
        # Fetch weather
        raw_data = self.api.fetch_weather(city)
        if not raw_data:
            return
        
        # Process data
        weather_data = self.processor.process_api_response(raw_data)
        
        # Save to storage
        self.storage.save_weather(raw_data)
        
        # Update display
        self.window.display_weather(weather_data)
        
        # Update features
        for feature in self.features.values():
            feature.update(weather_data)
    
    def run(self):
        """Start the application"""
        self.window.run()

if __name__ == "__main__":
    app = WeatherDashboardApp()
    app.run()