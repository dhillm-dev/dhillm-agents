import pandas as pd


def compute(df: pd.DataFrame):
    idx = df.index[-1]
    wd = idx.weekday()
    hr = getattr(idx, "hour", 0)
    bias = 0.0
    if wd in (1, 2) and 8 <= hr <= 12:
        bias += 0.1
    if wd == 4 and hr >= 15:
        bias -= 0.1
    return {"weekday": wd, "hour": hr, "score": float(bias), "type": "seasonality"}
