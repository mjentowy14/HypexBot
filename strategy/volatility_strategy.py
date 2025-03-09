import numpy as np
from datetime import datetime
from database.db_manager import DatabaseManager

class VolatilityStrategy:
    def __init__(self, volatility_threshold=0.02, prediction_buffer=0.03):
        """
        Strategy to test Allora's prediction accuracy during high volatility periods
        - Tracks price history for volatility calculation
        - Uses 2% volatility as default threshold for "high volatility" periods
        - Added 3% buffer for prediction differences to avoid chasing bad trades
        """
        self.price_history = {}
        self.db = DatabaseManager()
        self.volatility_threshold = volatility_threshold
        self.prediction_buffer = prediction_buffer
        
    def update_price_history(self, token, price):
        if token not in self.price_history:
            self.price_history[token] = []
        self.price_history[token].append(float(price))
        # Keep last 24 hours of data (assuming 5-minute intervals)
        self.price_history[token] = self.price_history[token][-288:]
    
    def calculate_volatility(self, prices, window=24):
        """
        Calculates rolling volatility using standard deviation of log returns
        - Uses 24-period window (configurable)
        - Higher values indicate more volatile market conditions
        """
        if len(prices) < window:
            return None
        returns = np.diff(np.log(prices[-window:]))
        return np.std(returns) * np.sqrt(window)
    
    def get_market_condition(self, volatility):
        return 'HIGH_VOLATILITY' if volatility > self.volatility_threshold else 'NORMAL'
    
    def calculate_trend(self, prices, window=12):
        """
        Calculate price trend over last hour (12 5-minute periods)
        Returns: 'UP', 'DOWN', or 'SIDEWAYS'
        """
        if len(prices) < window:
            return 'SIDEWAYS'
            
        recent_prices = prices[-window:]
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        if abs(price_change) < 0.01:  # Less than 1% change
            return 'SIDEWAYS'
        return 'UP' if price_change > 0 else 'DOWN'
    
    def execute(self, token, current_price, allora_signal, allora_prediction):
        # Update price history
        self.update_price_history(token, current_price)
        
        # Calculate volatility
        volatility = self.calculate_volatility(self.price_history[token])
        if volatility is None:
            return None
            
        trend = self.calculate_trend(self.price_history[token])
        prediction_diff = ((allora_prediction - current_price) / current_price)
        
        # Only trade if prediction difference exceeds buffer
        if abs(prediction_diff) < self.prediction_buffer:
            return None
            
        market_condition = self.get_market_condition(volatility)
        
        # Log trade data with trend info (but don't filter by it)
        trade_data = {
            'token': token,
            'current_price': current_price,
            'allora_prediction': allora_prediction,
            'prediction_diff': prediction_diff * 100,
            'volatility': volatility,
            'direction': allora_signal,
            'entry_price': current_price,
            'market_condition': market_condition,
            'trend': trend  # Keep logging trend for analysis
        }
        
        self.db.log_trade(trade_data)
        
        # Only check for high volatility, remove trend filter
        if market_condition == 'HIGH_VOLATILITY':
            return allora_signal
            
        return None 