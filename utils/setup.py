import eth_account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from utils.helpers import convert_percentage_to_decimal
from utils.env_loader import EnvLoader
from dotenv import load_dotenv
from utils.constants import TESTNET_API_URL, MAINNET_API_URL
import os


def setup():
    # Load configuration from environment
    env_loader = EnvLoader()
    config = env_loader.get_config()
    print(config)
    account = eth_account.Account.from_key(config["secret_key"])
    address = config["account_address"] or account.address
    vault = config["vault"]
    allora_upshot_key = config["allora_upshot_key"]
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    hl_master_address = config["hl_master_address"]
    allora_topics = config["allora_topics"]
    check_for_trades = config["check_for_trades"]
    allowed_amount_per_trade = config["allowed_amount_per_trade"]
    max_leverage = config["max_leverage"]
    mainnet = config["mainnet"]
    price_gap = convert_percentage_to_decimal(config["price_gap"])

    if vault != "":
        print(f"Running with vault: {vault}")
    else:
        print("Running with account address:", hl_master_address)

    if mainnet == "True":
        base_url = MAINNET_API_URL
    else:
        base_url = TESTNET_API_URL

    info = Info(base_url, skip_ws=True)
    if vault != "":
        exchange = Exchange(account, base_url, account_address=address, vault_address=vault)
        return (address, info, exchange, vault, allora_upshot_key, deepseek_api_key, check_for_trades,
                price_gap, allowed_amount_per_trade, max_leverage, allora_topics)
    else:
        exchange = Exchange(account, base_url, account_address=hl_master_address)
        return (hl_master_address, info, exchange, hl_master_address, allora_upshot_key, deepseek_api_key,
                check_for_trades, price_gap, allowed_amount_per_trade, max_leverage, allora_topics)


