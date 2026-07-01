from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from psychology import get_psychology_score
from session_filter import get_session_score
from support_resistance import get_sr_score
from breakout import get_breakout_score
from multi_timeframe import get_multi_timeframe_score

from config import CONFIDENCE_MIN, CONFIDENCE_MAX


# -----------------------------
# INDICATORS
# -----------------------------
def prepare_indicators(df):
    close = df["close"]

    df["ema20"] = EMAIndicator(close, window=20).ema_indicator()
    df["ema50"] = EMAIndicator(close, window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close, window=200).ema_indicator()

    df["rsi"] = RSIIndicator(close, window=14).rsi()

    macd = MACD(close)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    atr = AverageTrueRange(
        df["high"], df["low"], close, window=14
    )
    df["atr"] = atr.average_true_range()

    adx = ADXIndicator(
        high=df["high"], low=df["low"], close=close, window=14
    )
    df["adx"] = adx.adx()

    return df


# -----------------------------
# TREND DETECTION
# -----------------------------
def detect_trend(latest):
    if latest["ema20"] > latest["ema50"] > latest["ema200"]:
        return "Bullish"
    elif latest["ema20"] < latest["ema50"] < latest["ema200"]:
        return "Bearish"
    return "Neutral"


# -----------------------------
# CONFIRMATION ENGINE
# -----------------------------
def get_confirmations(latest, trend, breakout, mtf, sr):

    confirmations = 0

    # Trend
    if trend == "Bullish":
        confirmations += 1
    elif trend == "Bearish":
        confirmations -= 1

    # RSI
    if latest["rsi"] > 55:
        confirmations += 1
    elif latest["rsi"] < 45:
        confirmations -= 1

    # MACD
    if latest["macd"] > latest["macd_signal"]:
        confirmations += 1
    else:
        confirmations -= 1

    # ADX filter (important)
    if latest["adx"] > 20:
        confirmations += 1
    else:
        confirmations -= 1

    # Breakout
    if breakout["score"] > 10:
        confirmations += 1
    elif breakout["score"] < -10:
        confirmations -= 1

    # Multi timeframe
    if mtf["score"] > 10:
        confirmations += 1
    elif mtf["score"] < -10:
        confirmations -= 1

    # Support/Resistance
    if sr["score"] > 0:
        confirmations += 1
    elif sr["score"] < 0:
        confirmations -= 1

    # Psychology
    psy = get_psychology_score(latest.to_frame().T)
    confirmations += 1 if psy["score"] > 0 else -1

    return confirmations


# -----------------------------
# MAIN SIGNAL ENGINE
# -----------------------------
def generate_signal(current_df, higher_df):

    current_df = prepare_indicators(current_df)
    higher_df = prepare_indicators(higher_df)

    latest = current_df.iloc[-1]

    # -----------------------------
    # COMPONENT SCORES
    # -----------------------------
    breakout = get_breakout_score(
        current_df, None, None
    )

    mtf = get_multi_timeframe_score(
        current_df, higher_df
    )

    sr = get_sr_score(current_df)

    session = get_session_score()

    # -----------------------------
    # TREND
    # -----------------------------
    trend = detect_trend(latest)

    # -----------------------------
    # CONFIRMATIONS
    # -----------------------------
    confirmations = get_confirmations(
        latest,
        trend,
        breakout,
        mtf,
        sr
    )

    confirmations += 1 if session["score"] > 0 else -1

    # -----------------------------
    # FINAL SIGNAL LOGIC
    # -----------------------------
    if confirmations >= 4:
        signal = "CALL"
    elif confirmations <= -4:
        signal = "PUT"
    else:
        signal = "AVOID"

    # -----------------------------
    # CONFIDENCE
    # -----------------------------
    confidence = min(
        CONFIDENCE_MAX,
        max(CONFIDENCE_MIN, abs(confirmations) * 20)
    )

    # -----------------------------
    # FINAL OUTPUT
    # -----------------------------
    return {
        "signal": signal,
        "confidence": confidence,
        "trend": trend,
        "confirmations": confirmations,

        "ema20": float(latest["ema20"]),
        "ema50": float(latest["ema50"]),
        "ema200": float(latest["ema200"]),

        "rsi": float(latest["rsi"]),
        "macd": float(latest["macd"]),
        "macd_signal": float(latest["macd_signal"]),
        "adx": float(latest["adx"]),
        "atr": float(latest["atr"]),

        "support": sr["support"],
        "resistance": sr["resistance"],

        "reasons": session["reasons"][:5]
    }
