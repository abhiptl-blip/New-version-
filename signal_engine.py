from ta.trend import (
    EMAIndicator,
    MACD,
    ADXIndicator
)
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from psychology import get_psychology_score
from session_filter import get_session_score
from support_resistance import get_sr_score
from breakout import get_breakout_score
from multi_timeframe import get_multi_timeframe_score

from config import (
    CONFIDENCE_MIN,
    CONFIDENCE_MAX
)


def detect_bullish_engulfing(df):

    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] < prev["open"]
        and curr["close"] > curr["open"]
        and curr["close"] > prev["open"]
    )


def detect_bearish_engulfing(df):

    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] > prev["open"]
        and curr["close"] < curr["open"]
        and curr["close"] < prev["open"]
    )


def prepare_indicators(df):

    close = df["close"]

    df["ema20"] = EMAIndicator(
        close,
        window=20
    ).ema_indicator()

    df["ema50"] = EMAIndicator(
        close,
        window=50
    ).ema_indicator()

    df["ema200"] = EMAIndicator(
        close,
        window=200
    ).ema_indicator()

    df["rsi"] = RSIIndicator(
        close,
        window=14
    ).rsi()

    macd = MACD(close)

    df["macd"] = macd.macd()

    df["macd_signal"] = (
        macd.macd_signal()
    )

    atr = AverageTrueRange(
        df["high"],
        df["low"],
        close,
        window=14
    )

    df["atr"] = (
        atr.average_true_range()
    )

    adx = ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=close,
        window=14
    )

    df["adx"] = adx.adx()

    return df


def generate_signal(
    current_df,
    higher_df
):

    current_df = prepare_indicators(
        current_df
    )

    latest = current_df.iloc[-1]

    adx = latest["adx"]

    score = 0

    reasons = []

    trend = "Neutral"

    # EMA Trend

    ema20 = latest["ema20"]
    ema50 = latest["ema50"]
    ema200 = latest["ema200"]

    if ema20 > ema50 > ema200:

        gap = ema20 - ema50

        if gap > latest["atr"] * 0.30:

            score += 30

            reasons.append(
                "Strong Uptrend"
            )

        else:

            score += 20

            reasons.append(
                "Weak Uptrend"
            )

        trend = "Bullish"

    elif ema20 < ema50 < ema200:

        gap = ema50 - ema20

        if gap > latest["atr"] * 0.30:

            score -= 30

            reasons.append(
                "Strong Downtrend"
            )

        else:

            score -= 20

            reasons.append(
                "Weak Downtrend"
            )

        trend = "Bearish"

    # RSI

    if latest["rsi"] >= 70:

        score += 20

        reasons.append(
            "Strong RSI Bullish"
        )

    elif latest["rsi"] >= 60:

        score += 10

        reasons.append(
            "RSI Bullish"
        )

    elif latest["rsi"] <= 30:

        score -= 20

        reasons.append(
            "Strong RSI Bearish"
        )

    elif latest["rsi"] <= 40:

        score -= 10

        reasons.append(
            "RSI Bearish"
        )

    # MACD

    macd_diff = latest["macd"] - latest["macd_signal"]

    if macd_diff > 0.00005:

        score += 15
        reasons.append("Strong MACD Bullish")

    elif macd_diff > 0:

        score += 8
        reasons.append("Weak MACD Bullish")

    elif macd_diff < -0.00005:

        score -= 15
        reasons.append("Strong MACD Bearish")

    else:

        score -= 8
        reasons.append("Weak MACD Bearish")

    # Candlestick Patterns

    if detect_bullish_engulfing(current_df):

        if trend == "Bullish":

            score += 20

            reasons.append(
                "Bullish Engulfing"
            )

        else:

            score += 8

            reasons.append(
                "Weak Bullish Engulfing"
            )

    if detect_bearish_engulfing(current_df):

        if trend == "Bearish":

            score -= 20

            reasons.append(
                "Bearish Engulfing"
            )

        else:

            score -= 8

            reasons.append(
                "Weak Bearish Engulfing"
            )
    # Psychology

    psychology = (
        get_psychology_score(
            current_df
        )
    )

    score += psychology["score"]

    reasons.extend(
        psychology["reasons"]
    )

    # Candle Exhaustion Filter

    last6 = current_df.tail(6)

    bullish_count = 0
    bearish_count = 0

    for _, row in last6.iterrows():

        if row["close"] > row["open"]:
            bullish_count += 1

        elif row["close"] < row["open"]:
            bearish_count += 1

    if bullish_count >= 5:

        score -= 15

        reasons.append(
            "Bullish Exhaustion"
        )

    if bearish_count >= 5:

        score += 15

        reasons.append(
            "Bearish Exhaustion"
        )

    # Session Filter

    session = get_session_score()

    score += session["score"]

    reasons.extend(
        session["reasons"]
    )

    # Support Resistance

    sr = get_sr_score(
        current_df
    )

    score += sr["score"]

    reasons.extend(
        sr["reasons"]
    )

    price = latest["close"]

    distance_to_resistance = abs(
        sr["resistance"] - price
    )

    distance_to_support = abs(
        price - sr["support"]
    )

    if (
        trend == "Bullish"
        and distance_to_resistance < latest["atr"] * 0.5
    ):
        score -= 15
        reasons.append(
            "Near Resistance Rejection"
        )

    if (
        trend == "Bearish"
        and distance_to_support < latest["atr"] * 0.5
    ):
        score += 15
        reasons.append(
            "Near Support Rejection"
        )

    # Breakout

    breakout = (
        get_breakout_score(
            current_df,
            sr["support"],
            sr["resistance"]
        )
    )

    score += breakout["score"]

    reasons.extend(
        breakout["reasons"]
    )

    # Multi Timeframe

    mtf = (
        get_multi_timeframe_score(
            current_df,
            higher_df
        )
    )

    score += mtf["score"]

    reasons.extend(
        mtf["reasons"]
    )

    higher_df = prepare_indicators(higher_df)

    higher_latest = higher_df.iloc[-1]

    trend_higher = "Neutral"

    if (
        higher_latest["ema20"]
        > higher_latest["ema50"]
        > higher_latest["ema200"]
    ):
        trend_higher = "Bullish"

    elif (
        higher_latest["ema20"]
        < higher_latest["ema50"]
        < higher_latest["ema200"]
    ):
        trend_higher = "Bearish"

    # ADX Trend Strength Filter

    if adx < 20:

        score -= 20

        reasons.append(
            "Weak Trend (Low ADX)"
        )

    # Volatility Filter

    recent_atr = (
        current_df["atr"]
        .tail(20)
        .mean()
    )

    if latest["atr"] < recent_atr * 0.70:

        score -= 15

        reasons.append(
            "Low Volatility Market"
        )

    # Final Signal

    mtf_block = False

    CALL_THRESHOLD = 60
    PUT_THRESHOLD = -60

    mtf_block = False

    if score >= CALL_THRESHOLD and trend_higher != "Bullish":
        mtf_block = True

    if score <= PUT_THRESHOLD and trend_higher != "Bearish":
        mtf_block = True

    if mtf_block:

        signal = "AVOID"

    elif score >= CALL_THRESHOLD:

        signal = "CALL"

    elif score <= PUT_THRESHOLD:

        signal = "PUT"

    else:

        signal = "AVOID"

    confidence = min(
        CONFIDENCE_MAX,
        max(
            CONFIDENCE_MIN,
            abs(score)
        )
    )

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
