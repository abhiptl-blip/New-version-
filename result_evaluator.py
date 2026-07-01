import json
import os

from datetime import datetime

from datetime import timedelta

LOG_FILE = "data/signals_history.json"

def candle_time_match(candle_time, expiry_time, timeframe):

    candle_time = candle_time.replace(second=0, microsecond=0)
    expiry_time = expiry_time.replace(second=0, microsecond=0)

    if timeframe == "1min":
        return candle_time == expiry_time

    return (
        abs(candle_time - expiry_time)
        < timedelta(minutes=5)
    )


def get_expiry_close(current_df, expiry_time, timeframe):

    for _, row in current_df.iterrows():

        candle_time = row["time"]

        if candle_time_match(
            candle_time,
            expiry_time,
            timeframe
        ):

            return float(row["close"])

    return None

def evaluate_signals(current_df):

    if not os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, "r") as f:
        history = json.load(f)

    updated = False

    latest_candle_time = current_df.iloc[-1]["time"]

    for item in history:

        if item.get("result") != "PENDING":
            continue

        expiry = item.get("expiry_time")

        if expiry is None:
            continue

        expiry = datetime.fromisoformat(expiry)

        # Expiry candle abhi close nahi hui
        if latest_candle_time < expiry:
            continue

        expiry_close = get_expiry_close(
            current_df,
            expiry,
            item["timeframe"]
        )

        if expiry_close is None:
            continue

        signal = item["signal"]
        entry = float(item["entry_price"])

        if signal == "CALL":

            if expiry_close > entry:
                item["result"] = "WIN"
            else:
                item["result"] = "LOSS"

            item["exit_price"] = expiry_close

            updated = True

        elif signal == "PUT":

            if expiry_close < entry:
                item["result"] = "WIN"
            else:
                item["result"] = "LOSS"

            item["exit_price"] = expiry_close

            updated = True

    if updated:

        with open(LOG_FILE, "w") as f:
            json.dump(history, f, indent=2)
