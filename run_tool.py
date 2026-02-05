import sys
import threading
import time
from price_tool import get_current_price, get_option_prices, get_option_price_for_strike

done = False
status_message = "Working..."

def spinner():
    symbols = ["|", "/", "-", "\\"]
    idx = 0

    while not done:
        print(f"\r{status_message} {symbols[idx % len(symbols)]}", end="")
        idx += 1
        time.sleep(0.1)

    print(f"\r{status_message} ✓ Done")


if __name__ == "__main__":

    symbol = "ASTS"
    action = None
    strike = None

    # Read arguments
    if len(sys.argv) >= 2:
        symbol = sys.argv[1].upper()

    if len(sys.argv) >= 3:
        action = sys.argv[2].lower()

    if len(sys.argv) >= 4:
        try:
            strike = float(sys.argv[3])
        except ValueError:
            print("Strike must be a number")
            sys.exit(1)

    # Set status message BEFORE spinner starts
    if action in ["buy", "sell"] and strike is not None:
        status_message = f"Fetching {symbol} {action.upper()} option for strike {strike} (loading expiry chain for this week)"
    elif action in ["buy", "sell"]:
        status_message = f"Fetching {symbol} option chain (loading weekly expiries)"
    else:
        status_message = f"Fetching latest price for {symbol}"

    # Start spinner thread
    t = threading.Thread(target=spinner)
    t.start()

    # Run actual work
    if action in ["buy", "sell"] and strike is not None:
        result = get_option_price_for_strike(symbol, strike, action)

    elif action in ["buy", "sell"]:
        result = get_option_prices(symbol, action=action)

    else:
        result = get_current_price(symbol)

    # Stop spinner
    done = True
    t.join()

    print(result)
