from playwright.sync_api import sync_playwright

URL = "https://www.optionsprofitcalculator.com/calculator/long-call.html"

def accept_cookies(page):
    page.wait_for_timeout(3000)
    for frame in page.frames:
        try:
            btn = frame.locator("#accept-btn")
            if btn.is_visible():
                btn.click()
                break
        except:
            continue

def get_current_price(symbol: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        accept_cookies(page)

        # Wait for calculator field
        page.wait_for_selector("input[name='underlying-symbol']", timeout=20000)
        page.fill("input[name='underlying-symbol']", symbol)

        # Click correct Get price button
        get_price_buttons = page.locator("a.button", has_text="Get price")
        for i in range(get_price_buttons.count()):
            btn = get_price_buttons.nth(i)
            onclick = btn.get_attribute("onclick")
            if onclick and "t1e0_input_underlying" in onclick:
                btn.click()
                break

        page.wait_for_timeout(3000)
        price_value = page.locator("input[name='underlying-price']").input_value()

        browser.close()
        return {"symbol": symbol.upper(), "current_price": price_value}

def get_option_prices(symbol: str, action: str = "Buy"):
    action_value = "buy" if action.lower() == "buy" else "sell"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        accept_cookies(page)

        # Wait for calculator
        page.wait_for_selector("input[name='underlying-symbol']", timeout=20000)

        # Enter ticker
        page.fill("input[name='underlying-symbol']", symbol)

        # Click correct Get price button
        get_price_buttons = page.locator("a.button", has_text="Get price")
        for i in range(get_price_buttons.count()):
            btn = get_price_buttons.nth(i)
            onclick = btn.get_attribute("onclick")
            if onclick and "t1e0_input_underlying" in onclick:
                btn.click()
                break

        page.wait_for_timeout(3000)

        # ✅ Set Buy or Write via dropdown
        page.select_option("select[name='option-act']", value=action_value)

        # Click Select option
        page.locator("a.button", has_text="Select option").click()

        # Wait for option table
        page.wait_for_selector("table", timeout=15000)

        rows = page.locator("table tr").all()
        options = []

        for row in rows[1:]:
            cols = row.locator("td").all_inner_texts()
            if len(cols) >= 4:
                options.append({
                    "bid": cols[0],
                    "mid": cols[1],
                    "ask": cols[2],
                    "strike": cols[3]
                })

        browser.close()

        return {
            "symbol": symbol.upper(),
            "action": action.lower(),
            "options": options[:30]
        }

def get_option_price_for_strike(symbol: str, strike: float, action: str = "Buy"):
    action_value = "buy" if action.lower() == "buy" else "sell"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        accept_cookies(page)

        # Wait for calculator
        page.wait_for_selector("input[name='underlying-symbol']", timeout=20000)

        # Enter ticker
        page.fill("input[name='underlying-symbol']", symbol)

        # Click correct Get price
        get_price_buttons = page.locator("a.button", has_text="Get price")
        for i in range(get_price_buttons.count()):
            btn = get_price_buttons.nth(i)
            onclick = btn.get_attribute("onclick")
            if onclick and "t1e0_input_underlying" in onclick:
                btn.click()
                break

        page.wait_for_timeout(3000)

        # Set Buy/Write
        page.select_option("select[name='option-act']", value=action_value)

        # Open option selector
        page.locator("a.button", has_text="Select option").click()

        # Wait for option table
        page.wait_for_selector("table", timeout=15000)

        # Wait for option table
        strike_str = f"{strike:.2f}"
        row = page.locator(f"table tbody tr[name='{strike_str}']")
        # rows = page.locator("table tr").all()

        if row.count() == 0:
            browser.close()
            return {"error": f"Strike {strike_str} not found"}

        cols = row.locator("td").all_inner_texts()

        if action == "buy":
            bid = cols[0].strip()
            mid = cols[1].strip()
            ask = cols[2].strip()
        else:  # write / sell
            bid = cols[4].strip()
            mid = cols[5].strip()
            ask = cols[6].strip()
            print(f"Write/sell - bid: {bid}, mid: {mid}, ask: {ask}")

        browser.close()

        return {
            "symbol": symbol.upper(),
            "strike": strike_str,
            "action": action,
            "bid": bid,
            "mid": mid,
            "ask": ask
        }
