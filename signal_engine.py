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
        high=df["high"],
        low=df["low"],
        close=close,
        window=14
    )
    df["adx"] = adx.adx()

    return df


# -----------------------------
# TREND
# -----------------------------
def detect_trend(latest):

    if latest["ema20"] > latest["ema50"] > latest["ema200"]:
        return "Bullish"

    if latest["ema20"] < latest["ema50"] < latest["ema200"]:
        return "Bearish"

    return "Neutral"


# -----------------------------
# MAIN SIGNAL ENGINE (SAFE SCORING)
# -----------------------------
def generate_signal(current_df, higher_df):

    current_df = prepare_indicators(current_df)
    higher_df = prepare_indicators(higher_df)

    latest = current_df.iloc[-1]

    score = 0
    reasons = []

    trend = detect_trend(latest)

    # -----------------------------
    # TREND SCORE
    # -----------------------------
    if trend == "Bullish":
        score += 20
        reasons.append("Bullish Trend")

    elif trend == "Bearish":
        score -= 20
        reasons.append("Bearish Trend")

    # -----------------------------
    # RSI
    # -----------------------------
    if latest["rsi"] > 55:
        score += 10
        reasons.append("RSI Bullish")

    elif latest["rsi"] < 45:
        score -= 10
        reasons.append("RSI Bearish")

    # -----------------------------
    # MACD
    # -----------------------------
    if latest["macd"] > latest["macd_signal"]:
        score += 10
        reasons.append("MACD Bullish")

    else:
        score -= 10
        reasons.append("MACD Bearish")

    # -----------------------------
    # ADX (trend strength)
    # -----------------------------
    if latest["adx"] > 20:
        score += 10
        reasons.append("Strong Trend")

    else:
        score -= 10
        reasons.append("Weak Trend")

    # -----------------------------
    # BREAKOUT
    # -----------------------------
    breakout = get_breakout_score(current_df, None, None)
    score += breakout["score"]
    reasons.extend(breakout["reasons"])

    # -----------------------------
    # MULTI TIMEFRAME
    # -----------------------------
    mtf = get_multi_timeframe_score(current_df, higher_df)
    score += mtf["score"]
    reasons.extend(mtf["reasons"])

    # -----------------------------
    # SUPPORT RESISTANCE
    # -----------------------------
    sr = get_sr_score(current_df)
    score += sr["score"]
    reasons.extend(sr["reasons"])

    # -----------------------------
    # SESSION FILTER
    # -----------------------------
    session = get_session_score()
    score += session["score"]
    reasons.extend(session["reasons"])

    # -----------------------------
    # PSYCHOLOGY
    # -----------------------------
    psy = get_psychology_score(latest.to_frame().T)
    score += psy["score"]
    reasons.extend(psy["reasons"])

    # -----------------------------
    # FINAL SIGNAL LOGIC
    # -----------------------------
    if score >= 50:
        signal = "CALL"

    elif score <= -50:
        signal = "PUT"

    else:
        signal = "AVOID"

    # -----------------------------
    # CONFIDENCE
    # -----------------------------
    confidence = min(
        CONFIDENCE_MAX,
        max(CONFIDENCE_MIN, abs(score))
    )

    # -----------------------------
    # OUTPUT
    # -----------------------------
    return {
        "signal": signal,
        "confidence": confidence,
        "trend": trend,
        "score": score,

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

        "reasons": reasons[:10]
    }
