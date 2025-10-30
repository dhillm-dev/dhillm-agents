import pandas as pd
import ta


def compute(df: pd.DataFrame):
    close = df["Close"]
    rsi = ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1]
    ema_fast = ta.trend.EMAIndicator(close, 9).ema_indicator().iloc[-1]
    ema_slow = ta.trend.EMAIndicator(close, 21).ema_indicator().iloc[-1]
    macd = ta.trend.MACD(close).macd().iloc[-1]
    base = 0.0
    base += 0.7 if ema_fast > ema_slow else -0.7
    base += 0.5 if macd > 0 else -0.5
    if rsi > 55:
        base += 0.2
    if rsi < 45:
        base -= 0.2
    score = max(-1.5, min(1.5, base)) / 1.5
    return {
        "rsi": float(rsi),
        "ema_fast": float(ema_fast),
        "ema_slow": float(ema_slow),
        "macd": float(macd),
        "score": float(score),
        "type": "momentum",
    }