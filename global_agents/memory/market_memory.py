import os
import pandas as pd

MEM_PATH = os.getenv("MEM_PATH", "market_memory.csv")


def remember(features: dict, pnl: float):
    f = pd.DataFrame([{**features, "pnl": pnl}])
    if os.path.exists(MEM_PATH):
        f.to_csv(MEM_PATH, mode="a", header=False, index=False)
    else:
        f.to_csv(MEM_PATH, index=False)


def recall(top: int = 50):
    if not os.path.exists(MEM_PATH):
        return []
    df = pd.read_csv(MEM_PATH)
    df = df.sort_values("pnl", ascending=False).head(top)
    return df.to_dict("records")
