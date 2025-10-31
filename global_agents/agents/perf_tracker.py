import os
import pandas as pd
from datetime import datetime

LOG_PATH = os.getenv("PERF_LOG", "perf_log.csv")


def log_trade(agent: str, pnl: float, action: str, symbol: str):
    t = datetime.utcnow().isoformat()
    rec = pd.DataFrame([[t, agent, symbol, action, pnl]], columns=["time", "agent", "symbol", "action", "pnl"])
    if os.path.exists(LOG_PATH):
        rec.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        rec.to_csv(LOG_PATH, index=False)


def get_stats(window: int = 200):
    if not os.path.exists(LOG_PATH):
        return {}
    df = pd.read_csv(LOG_PATH).tail(window)
    out = {}
    for ag, g in df.groupby("agent"):
        mean = g["pnl"].mean()
        win = (g["pnl"] > 0).mean()
        sharpe = (g["pnl"].mean() / (g["pnl"].std() + 1e-9)) * (252 ** 0.5)
        out[ag] = {"avg": float(mean), "win_rate": float(win), "sharpe": float(sharpe)}
    return out
