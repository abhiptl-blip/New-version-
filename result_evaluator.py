import json
import os
import requests

from datetime import datetime

from config import API_KEY

LOG_FILE = "data/signals_history.json"

BASE_URL = "https://api.twelvedata.com/time_series"


def get_latest_close(pair, timeframe):

    interval = "1min" if timeframe == "1min" else "5min"

    response = requests.get(
        BASE_URL,
        params={
            "symbol": pair,
            "interval": interval,
            "outputsize": 2,
            "apikey": API_KEY,
            "format": "JSON"
        },
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if "values" not in data:
        return None

    values = list(reversed(data["values"]))

    return float(values[-1]["close"])


def evaluate_signals(current_df):

    if not os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, "r") as f:
        history = json.load(f)

    updated = False

    latest_candle = current_df.iloc[-1]

    candle_time = latest_candle["time"].to_pydatetime()

    latest_close = float(latest_candle["close"])

    for item in history:

        if item.get("result") != "PENDING":
            continue

        expiry = item.get("expiry_time")

        if expiry is None:
            continue

        expiry = datetime.fromisoformat(expiry)

        if now < expiry:
            continue

        pair = item.get("pair")
        timeframe = item.get("timeframe")

        latest_close = get_latest_close(
            pair,
            timeframe
        )

        if latest_close is None:
            continue

        signal = item.get("signal")
        entry = item.get("entry_price")

        if signal == "CALL":

            item["result"] = (
                "WIN"
                if latest_close > entry
                else "LOSS"
            )

            updated = True

        elif signal == "PUT":

            item["result"] = (
                "WIN"
                if latest_close < entry
                else "LOSS"
            )

            updated = True

    if updated:

        with open(LOG_FILE, "w") as f:
            json.dump(history, f, indent=2)
