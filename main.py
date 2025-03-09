from utils.setup import setup
from core.orders import OrderManager
from utils.helpers import display_leverage_info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
from allora.allora_mind import AlloraMind
from analysis.performance_analyzer import PerformanceAnalyzer
import time


def main():
    (address, info, exchange, vault, allora_upshot_key, deepseek_api_key, check_for_trades, price_gap,
     allowed_amount_per_trade, max_leverage, allora_topics) = setup()

    manager = OrderManager(exchange, vault, allowed_amount_per_trade, max_leverage, info)
    res = manager.get_wallet_summary()
    print(res)
    allora_mind = AlloraMind(manager, allora_upshot_key, deepseek_api_key, threshold=price_gap)
    allora_mind.set_topic_ids(allora_topics)
    allora_mind.start_allora_trade_bot(interval=check_for_trades)

    # Add periodic analysis
    while True:
        try:
            analyze_trading_results()
            time.sleep(3600)  # Analyze every hour
        except KeyboardInterrupt:
            break


def analyze_trading_results():
    analyzer = PerformanceAnalyzer()
    results = analyzer.analyze_results()
    print("\nTrading Analysis Results:")
    print("========================")
    print("\nPerformance by Market Condition:")
    print(results['condition_analysis'])
    print(f"\nVolatility Correlation: {results['volatility_correlation']:.4f}")
    print(f"Allora Prediction Accuracy: {results['prediction_accuracy']:.4f}")


if __name__ == "__main__":
    main()
