import pandas as pd
import numpy as np


def compute(df: pd.DataFrame, window: int = 48):
    p = df["Close"]
    v = df.get("Volume", pd.Series(index=df.index, data=np.nan)).fillna(1.0)
    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    vwap = (
        tp.rolling(window)
        .apply(lambda x: np.dot(x, v.loc[x.index]), raw=False)
        / v.rolling(window).sum()
    ).rename("vwap")
    spread = (p - vwap).iloc[-1]
    stdev = p.rolling(20).std().iloc[-1]
    z = 0.0 if (stdev or 0) == 0 else float(spread / stdev)
    score = -max(-2, min(2, z)) / 2.0
    return {
        "vwap": float(vwap.iloc[-1]) if vwap.notna().iloc[-1] else float(p.iloc[-1]),
        "z": float(z),
        "score": float(score),
        "type": "reversion",
    }
