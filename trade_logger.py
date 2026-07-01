import json
import os
from datetime import datetime, timedelta
from datetime import timedelta

LOG_FILE = "data/signals_history.json"


def log_signal(result, pair, timeframe, entry_price, current_df):

    if data.get("signal") == "AVOID":
        return

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        history = json.load(f)

    history.append({

        "time": datetime.utcnow().isoformat(),


    last_candle = current_df.iloc[-1]["time"]

    if timeframe == "1min":
        expiry_time = last_candle + timedelta(minutes=1)
    else:
        expiry_time = last_candle + timedelta(minutes=5)

    expiry_time = expiry_time.replace(second=0, microsecond=0)

        ).isoformat(),

        "expiry_interval": timeframe,
        
        "pair": pair,

        "symbol": pair,

        "timeframe": timeframe,

        "signal": data.get("signal"),

        "entry_price": entry_price,

        "confidence": data.get("confidence"),

        "trend": data.get("trend"),

        "score": data.get("score"),

        "ema20": data.get("ema20"),
        "ema50": data.get("ema50"),
        "ema200": data.get("ema200"),

        "rsi": data.get("rsi"),

        "macd": data.get("macd"),
        "macd_signal": data.get("macd_signal"),

        "adx": data.get("adx"),

        "atr": data.get("atr"),

        "support": data.get("support"),

        "resistance": data.get("resistance"),

        "reasons": data.get("reasons"),

        "result": "PENDING"
    })
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)
