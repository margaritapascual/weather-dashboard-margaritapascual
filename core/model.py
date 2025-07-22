# core/model.py

import joblib
from pathlib import Path

class TempPredictor:
    """
    Loads a pickled regression model and exposes a simple predict API.
    """
    def __init__(self, pkl_path: str = "data/temp_model.pkl"):
        # Load the pre-trained model; no DataFrame I/O here!
        self.model = joblib.load(Path(pkl_path))

    def predict(self, day_numbers):
        """
        day_numbers: iterable of ints (days since first_day baseline).
        Returns array of predicted temperatures.
        """
        return self.model.predict([[int(d)] for d in day_numbers])
