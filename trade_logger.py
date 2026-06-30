import json
import os
from datetime import datetime, timedelta

LOG_FILE = "data/signals_history.json"


def log_signal(
    data,
    pair,
    timeframe,
    entry_price
):

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        history = json.load(f)

    history.append({

        "time": datetime.utcnow().isoformat(),

        "expiry_time": (
            datetime.utcnow() +
            timedelta(
                minutes=1 if timeframe == "1min" else 5
            )
        ).isoformat(),
        
        "pair": pair,

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
