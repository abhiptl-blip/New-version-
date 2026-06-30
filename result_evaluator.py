import json
import os

from datetime import datetime

LOG_FILE = "data/signals_history.json"


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

        if candle_time < expiry:
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
