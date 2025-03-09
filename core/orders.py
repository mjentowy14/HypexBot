from hyperliquid.info import Info
import json
from utils.helpers import round_size, round_price


class OrderManager:
    def __init__(self, exchange, vault_address, allowed_amount_per_trade, leverage, info: Info):
        self.exchange = exchange
        self.info = info
        self.vault_address = vault_address
        self.allowed_amount_per_trade = allowed_amount_per_trade
        self.leverage = leverage
        
        # Define size decimals for each coin
        self.size_decimals = {
            'BTC': 3,  # 0.001 BTC minimum
            'ETH': 2,  # 0.01 ETH minimum
            'SOL': 1,  # 0.1 SOL minimum
            'default': 1
        }

    def round_size(self, coin: str, size: float) -> float:
        """
        Round size according to coin's decimal requirements
        """
        decimals = self.size_decimals.get(coin, self.size_decimals['default'])
        rounded_size = round(size, decimals)
        
        # Ensure minimum sizes
        min_sizes = {
            'BTC': 0.001,
            'ETH': 0.01,
            'SOL': 0.1,
            'default': 0.1
        }
        
        min_size = min_sizes.get(coin, min_sizes['default'])
        return max(rounded_size, min_size)

    def create_order(self, coin, is_buy, size, price, order_type, reduce_only=False):
        """
        Places a buy or sell order with size and price rounding.
        """
        print(f"Placing {'Buy' if is_buy else 'Sell'} order for {size} {coin} at {price}")
        return self.exchange.order(coin, is_buy, size, price, order_type, reduce_only=reduce_only)

    def cancel_order(self, coin, oid):
        print(f"Cancelling order {oid} for {coin}")
        return self.exchange.cancel(coin, oid)

    def update_leverage(self, coin, leverage, cross_margin=True):
        mode = "cross margin" if cross_margin else "isolated margin"
        print(f"Updating leverage for {coin} to {leverage}x ({mode})")
        return self.exchange.update_leverage(leverage, coin, cross_margin)

    def market_open(self, coin, is_buy, size, leverage=5, cross_margin=True):
        self.update_leverage(coin, leverage, cross_margin=cross_margin)
        print(f"Market {'Buy' if is_buy else 'Sell'} order for {size} {coin}")
        return self.exchange.market_open(coin, is_buy, size)

    def market_close(self, coin):
        print(f"Closing position for {coin}")
        return self.exchange.market_close(coin)

    def list_open_positions(self):
        """
        Returns just the coin names of open positions
        """
        positions = self.get_open_positions()
        return [pos['coin'] for pos in positions] if positions else []

    def get_open_positions(self):
        """
        Get all open positions with correct position structure
        Returns list of positions with standardized format
        """
        try:
            response = self.info.user_state(self.vault_address)
            positions = response.get('assetPositions', [])
            print(positions)
            
            formatted_positions = []
            for pos in positions:
                if 'position' in pos:
                    position_data = pos['position']
                    # Check if position size is non-zero
                    if float(position_data.get('szi', 0)) != 0:
                        formatted_positions.append({
                            'coin': position_data.get('coin'),
                            'szi': float(position_data.get('szi', 0)),
                            'entryPrice': float(position_data.get('entryPx', 0)),
                            'leverage': position_data.get('leverage', {})
                        })
            
            return formatted_positions
            
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []

    def get_wallet_summary(self, mode="cross"):
        print("Fetching wallet summary...")
        response = self.info.user_state(self.vault_address)
        summary = response.get("crossMarginSummary", {}) if mode == "cross" else response.get("marginSummary", {})
        print(f" Wallet Summary: {summary}")
        return {
            "account_value": summary.get("accountValue"),
            "total_position_value": summary.get("totalNtlPos"),
            "total_usd_balance": summary.get("totalRawUsd"),
            "margin_used": summary.get("totalMarginUsed"),
        }

    def calculate_min_order_size(self, coin, current_price):
        """
        Calculate minimum order size to meet $10 minimum requirement
        """
        min_value = 10.0  # $10 minimum
        min_size = (min_value / current_price) * 1.1  # Add 10% buffer
        
        # Round to appropriate decimals
        if coin == "BTC":
            return round(min_size, 4)  # 0.0001 BTC precision
        elif coin == "ETH":
            return round(min_size, 3)  # 0.001 ETH precision
        return round(min_size, 2)

    def create_trade_order(self, coin, is_buy, profit_target=5, loss_target=3):
        try:
            # Get current price
            current_price = self.get_current_price(coin)
            if current_price is None:
                print(f"Could not get current price for {coin}, skipping trade")
                return None
            
            # Calculate size in coin units
            size = (self.allowed_amount_per_trade / current_price) * self.leverage
            
            # Round size according to coin's requirements
            rounded_size = self.round_size(coin, size)
            
            print(f"Creating {'Buy' if is_buy else 'Sell'} order for {rounded_size} {coin}")
            
            # Update leverage before order
            self.update_leverage(coin, self.leverage)
            
            # Create market order
            order = self.exchange.market_open(
                name=coin,
                is_buy=is_buy,
                sz=rounded_size
            )
            
            print(f"Order response: {order}")
            return order
            
        except Exception as e:
            print(f"Error creating order: {str(e)}")
            return None

    def get_price(self, coin):
        coin = str(coin).upper()
        # Fetch metadata for available tokens
        meta = self.info.meta_and_asset_ctxs()

        # Parse universe and additional data
        universe_data = meta[0]["universe"]
        additional_data = meta[1] if len(meta) > 1 else []

        # Find the coin data from universe_data
        coin_index = next((index for index, asset in enumerate(universe_data) if asset["name"] == coin), None)
        if coin_index is None:
            print(f"Oops... This coin is not supported by HyperLiquid. Coin: {coin}")
            return None

        # Merge data using the same index in additional_data
        coin_data = universe_data[coin_index]
        if coin_index < len(additional_data):
            coin_data.update(additional_data[coin_index])

        if coin_data:
            return coin_data["oraclePx"]

        return None

    def get_open_orders(self):
        return self.info.open_orders(self.vault_address)

    def modify_open_order(self, name, is_buy, sz, order_type,   order_id, limit_price):
        print("OID->",order_id)
        return self.exchange.modify_order(oid=order_id,
                                          limit_px=limit_price,
                                          name=name,
                                          sz=sz,
                                          is_buy=is_buy,
                                          order_type=order_type)

    def get_current_price(self, coin):
        """
        Get the current price for a given coin
        """
        try:
            # Use info.all_mids() instead of exchange.get_all_mids()
            market_info = self.info.all_mids()
            if coin in market_info:
                return float(market_info[coin])
            raise ValueError(f"Price not found for {coin}")
        except Exception as e:
            print(f"Error getting price for {coin}: {str(e)}")
            return None

