from flask import Flask, render_template
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# CONFIGURATION
# -----------------------------
API_KEY = "SOJTADS3VUN4QSJXLUBA279JXLUBA"
API_URL = f"https://api.metals.dev/v1/latest?api_key={API_KEY}&currency=USD&unit=toz"
DATA_FILE = "data/yesterday_data.json"

# Create folder if missing
os.makedirs("data", exist_ok=True)

# Metals to track
METALS = ["gold", "silver", "platinum", "copper", "iron"]


# -----------------------------
# FETCH METALS DATA
# -----------------------------
def fetch_latest_data():
    """Fetch latest metal prices in USD and the INR conversion rate."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        metals_data = data.get("metals", {})
        currencies = data.get("currencies", {})
        usd_to_inr = 1 / currencies.get("INR", 0.01131)  # USD → INR

        return metals_data, usd_to_inr
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None, None


# -----------------------------
# CONVERT PRICES
# -----------------------------
def convert_to_inr(metals_usd, inr_rate):
    """Convert metal prices from USD → INR."""
    metals_inr = {}
    for metal in METALS:
        value = metals_usd.get(metal)
        metals_inr[metal] = round(value * inr_rate, 2) if value else None
    return metals_inr


# -----------------------------
# READ/WRITE LOCAL DATA
# -----------------------------
def load_yesterday_data():
    """Load yesterday’s prices from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_today_data(today_data):
    """Save today’s prices to JSON for next run."""
    with open(DATA_FILE, "w") as f:
        json.dump(today_data, f, indent=4)


# -----------------------------
# CALCULATE % CHANGE
# -----------------------------
def calculate_percentage_change(today, yesterday):
    """Compute percentage change for each metal."""
    changes = {}
    for metal in METALS:
        t_val = today.get(metal)
        y_val = yesterday.get(metal)
        if t_val and y_val and y_val != 0:
            changes[metal] = round(((t_val - y_val) / y_val) * 100, 2)
        else:
            changes[metal] = None
    return changes


# -----------------------------
# FLASK ROUTES
# -----------------------------
@app.route("/")
def index():
    metals_usd, inr_rate = fetch_latest_data()
    if not metals_usd or not inr_rate:
        return "<h3>Error fetching metal prices. Please try again later.</h3>", 500

    today_data = convert_to_inr(metals_usd, inr_rate)
    yesterday_data = load_yesterday_data()
    percentage_changes = calculate_percentage_change(today_data, yesterday_data)
    save_today_data(today_data)

    table_data = []
    for metal in METALS:
        table_data.append({
            "name": metal.capitalize(),
            "today": today_data.get(metal),
            "yesterday": yesterday_data.get(metal, "—"),
            "change": percentage_changes.get(metal)
        })

    return render_template(
        "index.html",
        table_data=table_data,
        date=datetime.now().strftime("%B %d, %Y")
    )


# -----------------------------
# RUN LOCALLY
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
