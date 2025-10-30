import pandas as pd
import numpy as np


def compute(df: pd.DataFrame):
    r = df["Close"].pct_change()
    rv = (r.rolling(12).std().iloc[-1] or 0.0)
    trend = np.sign(df["Close"].iloc[-1] - df["Close"].iloc[-6])
    score = -min(0.5, max(0.0, rv * 10.0))
    return {"rv": float(rv), "trend": float(trend), "score": float(score), "type": "liquidity_forecast"}