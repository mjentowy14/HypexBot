from .volatility_strategy import VolatilityStrategy

# Initialize strategy globally
volatility_strategy = VolatilityStrategy()


def custom_strategy(token, price=None, allora_signal=None, allora_prediction=None):
    """
    Modified custom strategy that trades counter to Allora's predictions
    during high volatility periods
    """
    if price is None or allora_signal is None or allora_prediction is None:
        return None

    return volatility_strategy.execute(token, price, allora_signal, allora_prediction)
