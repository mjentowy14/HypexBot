import json


def display_leverage_info(info, address, coin):
    user_state = info.user_state(address)
    for position in user_state.get("assetPositions", []):
        if position["position"]["coin"] == coin:
            print(f"Leverage info for {coin}:", json.dumps(position["position"]["leverage"], indent=2))


def round_price(price):
    return round(float(f"{price:.5g}"), 6)


def round_size(size, sz_decimals):
    return round(size, sz_decimals)


def convert_percentage_to_decimal(percentage):
    """
    Converts a percentage value to its decimal equivalent.

    :param percentage: The percentage value to convert (e.g., 0.25 for 0.25%).
    :return: The decimal equivalent of the given percentage.
    """
    if isinstance(percentage, (int, float)):
        return percentage / 100
    else:
        raise ValueError("Input must be a number (int or float).")

