from flask import Flask, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_URL = "https://api.metals.dev/v1/latest"
API_KEY = "SOJTADS3VUN4QSJXLUBA279JXLUBA"
CURRENCY = "USD"
UNIT = "toz"
INR_CONVERSION_RATE = 84.0  # Approximate; can update dynamically using forex API

METALS = ["gold", "silver", "platinum", "copper", "iron"]


def fetch_prices(date=None):
    """Fetch metal prices from Metals.dev API"""
    params = {
        "api_key": API_KEY,
        "currency": CURRENCY,
        "unit": UNIT
    }
    if date:
        params["date"] = date

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = {}
        for metal in METALS:
            if metal in data.get("metals", {}):
                usd_price = data["metals"][metal]
                inr_price = usd_price * INR_CONVERSION_RATE
                prices[metal.capitalize()] = round(inr_price, 2)
        return prices

    except Exception as e:
        print(f"❌ Error fetching API data: {e}")
        return {metal.capitalize(): 0.0 for metal in METALS}


def calculate_change(today, yesterday):
    """Return structured dict: {metal: {today, yesterday, change_percent}}"""
    structured = {}
    for metal in today.keys():
        today_price = today.get(metal, 0)
        y_price = yesterday.get(metal, 0)
        if y_price > 0:
            diff = today_price - y_price
            percent = round((diff / y_price) * 100, 2)
        else:
            percent = 0.0

        structured[metal] = {
            "today": today_price,
            "yesterday": y_price,
            "change_percent": percent
        }
    return structured


@app.route("/")
def index():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    today_prices = fetch_prices(today.isoformat())
    yesterday_prices = fetch_prices(yesterday.isoformat())

    prices = calculate_change(today_prices, yesterday_prices)

    return render_template(
        "index.html",
        today=today.strftime("%d %b %Y"),
        yesterday=yesterday.strftime("%d %b %Y"),
        prices=prices
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
