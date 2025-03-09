from hyperliquid.exchange import Exchange


class ExchangeWrapper:
    def __init__(self, account, base_url, vault_address):
        self.exchange = Exchange(account, base_url, account_address=vault_address)
