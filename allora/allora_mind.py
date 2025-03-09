import requests
import time
from utils.helpers import round_price
from strategy.custom_strategy import custom_strategy
from utils.constants import ALLORA_API_BASE_URL
from database.db_manager import DatabaseManager
from strategy.deepseek_reviewer import DeepSeekReviewer


class AlloraMind:
    def __init__(self, manager, allora_upshot_key, deepseek_api_key, threshold=0.03):
        """
        Initializes the AlloraMind with a given OrderManager and strategy parameters.

        :param manager: Instance of OrderManager to interact with orders.
        :param threshold: The percentage threshold for generating signals.
        """
        self.manager = manager
        self.threshold = threshold
        self.allora_upshot_key = allora_upshot_key
        self.topic_ids = {}
        self.timeout = 5
        self.base_url = ALLORA_API_BASE_URL
        self.db = DatabaseManager()
        self.deepseek_reviewer = DeepSeekReviewer(deepseek_api_key)

    def set_topic_ids(self, topic_ids):
        """
        Set topic IDs for the tokens.
        :param topic_ids: Dictionary mapping tokens to topic IDs.
        """
        self.topic_ids = topic_ids

    def get_inference_ai_model(self, topic_id):
        url = f'{self.base_url}ethereum-11155111?allora_topic_id={topic_id}'
        headers = {
            'accept': 'application/json',
            'x-api-key': self.allora_upshot_key
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                network_inference_normalized = float(data['data']['inference_data']['network_inference_normalized'])
                return network_inference_normalized
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print("Max retries reached, could not fetch data.")
                    return None

    def generate_signal(self, token):
        """
        Generates a signal based on Allora predictions.
        :param token: The token symbol (e.g., 'BTC', 'ETH') to fetch the price for.
        :return: A signal string ("BUY", "SELL", or "HOLD"), the percentage difference, current price, and prediction.
        """
        topic_id = self.topic_ids.get(token)
        if topic_id is None:
            self.log_analysis(token, "SKIP", None, None, reason="No topic ID configured")
            return "HOLD", None, None, None

        prediction = self.get_inference_ai_model(topic_id)
        if prediction is None:
            self.log_analysis(token, "SKIP", None, None, reason="No prediction available")
            return "HOLD", None, None, None

        current_price = self.manager.get_price(token)
        if current_price is None:
            self.log_analysis(token, "SKIP", None, None, reason="No price available")
            return "HOLD", None, None, None

        prediction = float(prediction)
        current_price = float(current_price)
        difference = (prediction - current_price) / current_price

        if abs(difference) >= self.threshold:
            signal = "BUY" if difference > 0 else "SELL"
            self.log_analysis(token, signal, current_price, prediction, difference)
            return signal, difference, current_price, prediction
            
        self.log_analysis(token, "HOLD", current_price, prediction, difference, "Below threshold")
        return "HOLD", difference, current_price, prediction

    def open_trade(self):
        """
        Opens a trade based on Allora and optional custom strategies.
        """
        tokens = list(self.topic_ids.keys())
        for token in tokens:
            # Get open positions using the new format
            open_positions = self.manager.list_open_positions()
            
            # Check if token is already in an open position
            if token in open_positions:
                print(f"Already an open position for {token}, skipping...")
                continue

            allora_signal, allora_diff, current_price, prediction = self.generate_signal(token)

            # Pass more information to custom strategy
            custom_signal = custom_strategy(
                token, 
                current_price, 
                allora_signal, 
                prediction
            )

            # Add DeepSeek review before executing trade
            trade_data = {
                'token': token,
                'current_price': current_price,
                'allora_prediction': prediction,
                'prediction_diff': allora_diff * 100 if allora_diff else None,
                'direction': allora_signal,
                'market_condition': 'ANALYSIS'
            }
            review = self.deepseek_reviewer.review_trade(trade_data)
            
            if review and review['approval'] and review['confidence'] > 70:
                # Continue with existing trade execution logic
                if custom_signal == "BUY" and allora_signal == "BUY":
                    signal = "BUY"
                elif custom_signal == "SELL" and allora_signal == "SELL":
                    signal = "SELL"
                elif not custom_signal and allora_signal in ["BUY", "SELL"]:
                    signal = allora_signal
                else:
                    print(f"No trading opportunity for {token}, signal: HOLD")
                    continue

                # If there's no signal, skip the token
                if signal == "HOLD":
                    continue

                # Calculate profit target and stop-loss automatically
                target_profit = abs(allora_diff) * 100  # Convert to percentage based on Allora's diff
                stop_loss = target_profit * 0.5  # Stop-loss is 50% of the profit target
                print(f"Profit Target: {target_profit}% and Stop Loss: {stop_loss}%")

                # Generate the order based on the signal
                if signal == "BUY":
                    print(f"Generating BUY order for {token} with {allora_diff:.2%} difference "
                          f"and Current Price: {current_price} Predicted Price: {prediction}")
                    res = self.manager.create_trade_order(token, is_buy=True,
                                                          profit_target=target_profit,
                                                          loss_target=stop_loss)
                    print(res)
                elif signal == "SELL":
                    print(f"Generating SELL order for {token} with {allora_diff:.2%} difference"
                          f" and Current Price: {current_price} Predicted Price: {prediction}")
                    print(f" token:{token}, profit targit: {target_profit} and Loss: {stop_loss}")
                    res = self.manager.create_trade_order(token, is_buy=False,
                                                          profit_target=target_profit,
                                                          loss_target=stop_loss)
                    print(res)
            else:
                print(f"Trade rejected by DeepSeek AI:")
                print(f"Confidence: {review['confidence']}%")
                print(f"Reasoning: {review['reasoning']}")
                print(f"Risk Score: {review['risk_score']}/10")
                return

    def monitor_positions(self):
        """
        Monitors open positions and manages trades based on Allora predictions.
        Uses 1% buffer to avoid closing on small prediction movements.
        """
        open_positions = self.manager.get_open_positions()
        if not open_positions:
            print("No open positions to track.")
            return

        CLOSE_BUFFER = 0.01  # 1% buffer for closing positions

        for position in open_positions:
            token = position["coin"]
            entry_price = float(position["entryPrice"])
            side = "A" if float(position["szi"]) > 0 else "B"

            topic_id = self.topic_ids.get(token)
            if not topic_id:
                print(f"No topic ID configured for token: {token}")
                continue

            prediction = self.get_inference_ai_model(topic_id)
            current_price = self.manager.get_current_price(token)
            
            if prediction is None or current_price is None:
                print(f"Data unavailable for {token}. Skipping...")
                continue

            current_price = float(current_price)
            prediction = float(prediction)
            pnl_percent = ((current_price - entry_price) / entry_price) * 100 * (1 if side == "A" else -1)
            
            # Calculate prediction difference as percentage
            pred_diff_percent = (prediction - current_price) / current_price

            # For SHORT positions (side B), close when prediction > current_price by buffer
            # For LONG positions (side A), close when prediction < current_price by buffer
            should_close = (side == "B" and pred_diff_percent > CLOSE_BUFFER) or \
                          (side == "A" and pred_diff_percent < -CLOSE_BUFFER)

            if should_close:
                print(f"Closing {'LONG' if side == 'A' else 'SHORT'} position for {token}:")
                print(f"  Side: {side}")
                print(f"  Entry: ${entry_price:,.2f}")
                print(f"  Current: ${current_price:,.2f} ({pnl_percent:+.2f}%)")
                print(f"  Prediction: ${prediction:,.2f}")
                print(f"  Prediction Difference: {pred_diff_percent:+.2%}")
                print(f"  Reason: {'Prediction above current price by >1%' if side == 'B' else 'Prediction below current price by >1%'}")
                self.manager.market_close(token)
            else:
                print(f"Holding position for {token}:")
                print(f"  Side: {side}")
                print(f"  Entry: ${entry_price:,.2f}")
                print(f"  Current: ${current_price:,.2f} ({pnl_percent:+.2f}%)")
                print(f"  Prediction: ${prediction:,.2f}")
                print(f"  Prediction Difference: {pred_diff_percent:+.2%}")

    def start_allora_trade_bot(self, interval=180):
        """
        Starts the trading and monitoring process at regular intervals.
        :param interval: Time in seconds between checks (default: 180 seconds).
        :param profit_target: Profit target percentage for trades.
        :param loss_target: Loss target percentage for trades.
        """
        while True:
            print("Running trading and position monitoring...")
            self.open_trade()
            self.monitor_positions()
            print(f"Sleeping for {interval} seconds...")
            time.sleep(interval)

    def log_analysis(self, token, signal_type, current_price, prediction, difference=None, reason=None):
        """Silent logging to database without affecting console output"""
        try:
            trade_data = {
                'token': token,
                'current_price': current_price,
                'allora_prediction': prediction,
                'prediction_diff': difference * 100 if difference else None,
                'volatility': self.manager.get_volatility(token) if hasattr(self.manager, 'get_volatility') else None,
                'direction': signal_type,
                'entry_price': current_price,
                'market_condition': 'ANALYSIS',
                'reason': reason
            }
            self.db.log_trade(trade_data)
        except Exception as e:
            print(f"Database logging error: {str(e)}")  # Only error gets printed
