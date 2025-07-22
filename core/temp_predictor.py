import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List

class TempPredictor:
    """
    Temperature prediction using simple linear regression
    Can be replaced with more sophisticated models later
    """
    
    def __init__(self):
        self.model = LinearRegression()
        # Sample training data (day_number, temperature)
        self.X_train = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)  # Day numbers
        self.y_train = np.array([72, 74, 76, 78, 80])  # Sample temperatures
        
        # Train the model
        self.model.fit(self.X_train, self.y_train)
    
    def predict(self, day_numbers: List[int]) -> List[float]:
        """
        Predict temperatures for given day numbers
        Args:
            day_numbers: List of days to predict (e.g., [1, 2, 3] for next 3 days)
        Returns:
            List of predicted temperatures
        """
        if not day_numbers:
            return []
            
        # Convert to numpy array and reshape for sklearn
        days_array = np.array(day_numbers).reshape(-1, 1)
        
        # Make predictions
        predictions = self.model.predict(days_array)
        
        # Round to 1 decimal place
        return [round(temp, 1) for temp in predictions]

# Example usage
if __name__ == "__main__":
    predictor = TempPredictor()
    print(predictor.predict([6, 7, 8]))  # Predict next 3 days