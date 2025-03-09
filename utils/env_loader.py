import os
from dotenv import load_dotenv

class EnvLoader:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
    def get_config(self):
        """
        Load configuration from environment variables with validation
        """
        required_vars = [
            'HL_SECRET_KEY',
            'ALLORA_UPSHOT_KEY',
            'DEEPSEEK_API_KEY'
        ]
        
        # Check for required variables
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        # Trading parameters with defaults
        config = {
            "secret_key": os.getenv('HL_SECRET_KEY'),
            "account_address": os.getenv('HL_ACCOUNT_ADDRESS'),
            "hl_master_address": os.getenv('HL_MASTER_ADDRESS'),
            "vault": os.getenv('HL_VAULT', ''),
            "allora_upshot_key": os.getenv('ALLORA_UPSHOT_KEY'),
            "price_gap": float(os.getenv('PRICE_GAP', '0.25')),
            "allowed_amount_per_trade": float(os.getenv('ALLOWED_AMOUNT_PER_TRADE', '500')),
            "max_leverage": int(os.getenv('MAX_LEVERAGE', '5')),
            "check_for_trades": int(os.getenv('CHECK_FOR_TRADES', '300')),
            "volatility_threshold": float(os.getenv('VOLATILITY_THRESHOLD', '0.02')),
            "db_path": os.getenv('DB_PATH', 'trading_logs.db'),
            "mainnet": os.getenv('MAINNET', "False"),
            "allora_topics": {
                "BTC": int(os.getenv('BTC_TOPIC_ID', '14')),
                "ETH": int(os.getenv('ETH_TOPIC_ID', '13'))
            }
        }
        
        return config
