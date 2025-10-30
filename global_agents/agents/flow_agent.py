import pandas as pd


def compute(df: pd.DataFrame):
    last = df.iloc[-1]
    body = abs(last["Close"] - last["Open"])
    range_ = max(1e-9, last["High"] - last["Low"])
    upper = last["High"] - max(last["Close"], last["Open"])
    lower = min(last["Close"], last["Open"]) - last["Low"]
    wick_bias = (lower - upper) / range_
    score = max(-1, min(1, wick_bias))
    return {
        "wick_bias": float(wick_bias),
        "spread": float(range_),
        "score": float(score),
        "type": "flow",
    }