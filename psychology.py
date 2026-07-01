def is_tradeable_candle(candle):

    rng = candle["high"] - candle["low"]
    if rng == 0:
        return False

    body = abs(candle["close"] - candle["open"])
    body_ratio = body / rng

    return 0.35 <= body_ratio <= 0.80

def candle_body_size(candle):

    return abs(
        candle["close"] - candle["open"]
    )


def candle_range(candle):

    return (
        candle["high"] - candle["low"]
    )


def upper_wick(candle):

    return (
        candle["high"]
        - max(
            candle["open"],
            candle["close"]
        )
    )


def lower_wick(candle):

    return (
        min(
            candle["open"],
            candle["close"]
        )
        - candle["low"]
    )


def bullish_strength(candle):

    body = candle_body_size(candle)
    rng = candle_range(candle)

    if rng == 0:
        return 0

    return (body / rng) * 100


def bearish_strength(candle):

    body = candle_body_size(candle)
    rng = candle_range(candle)

    if rng == 0:
        return 0

    return (body / rng) * 100


def is_bullish_momentum(candle):

    if candle["close"] <= candle["open"]:
        return False

    rng = candle["high"] - candle["low"]
    if rng == 0:
        return False

    body = candle["close"] - candle["open"]

    return (body / rng) >= 0.60


def is_bearish_momentum(candle):

    if candle["close"] >= candle["open"]:
        return False

    rng = candle["high"] - candle["low"]
    if rng == 0:
        return False

    body = candle["open"] - candle["close"]

    return (body / rng) >= 0.60


def is_bullish_rejection(candle):

    body = abs(candle["close"] - candle["open"])
    lower_wick = min(candle["open"], candle["close"]) - candle["low"]

    return (
        lower_wick > body * 2
        and candle["close"] > candle["open"]
    )


def is_bearish_rejection(candle):

    body = abs(candle["close"] - candle["open"])
    upper_wick = candle["high"] - max(candle["open"], candle["close"])

    return (
        upper_wick > body * 2
        and candle["close"] < candle["open"]
    )


def is_exhaustion_candle(candle):

    rng = candle["high"] - candle["low"]
    if rng == 0:
        return False

    body = abs(candle["close"] - candle["open"])

    body_ratio = body / rng

    return body_ratio < 0.25


def get_psychology_score(df):

    latest = df.iloc[-1]

    score = 0
    reasons = []

    if not is_tradeable_candle(latest):
        return {"score": 0, "reasons": ["No Trade Candle"]}

    if is_bullish_momentum(latest):
        score += 20
        reasons.append("Bullish Momentum")

    elif is_bearish_momentum(latest):
        score -= 20
        reasons.append("Bearish Momentum")

    elif is_bullish_rejection(latest):
        score += 15
        reasons.append("Bullish Rejection")

    elif is_bearish_rejection(latest):
        score -= 15
        reasons.append("Bearish Rejection")

    elif is_exhaustion_candle(latest):
        score -= 10
        reasons.append("Exhaustion Candle")

    return {
        "score": score,
        "reasons": reasons
    }
