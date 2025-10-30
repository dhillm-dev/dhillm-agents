import pandas as pd
import numpy as np


def compute_pair(df_a: pd.DataFrame, df_b: pd.DataFrame):
    ra = df_a["Close"].pct_change().tail(50)
    rb = df_b["Close"].pct_change().tail(50)
    if len(ra.dropna()) < 20 or len(rb.dropna()) < 20:
        return {"score": 0.0, "pair": None, "type": "pair_revert"}
    spread = (ra - rb).dropna()
    z = (spread.iloc[-1] - spread.mean()) / (spread.std() or 1e-9)
    score = -max(-2, min(2, float(z))) / 2.0
    return {"z": float(z), "score": float(score), "type": "pair_revert"}