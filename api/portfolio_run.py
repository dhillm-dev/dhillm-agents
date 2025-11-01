from fastapi import FastAPI
from fastapi.responses import JSONResponse
import yfinance as yf, pandas as pd, math, json
from api.screener_stocks import screener as _stock_screen

app = FastAPI()
EQUITY = 10_000.0  # paper

def _dl(sym, per="120d"):
    try:
        return yf.download(sym, period=per, interval="1d", auto_adjust=True, progress=False, threads=False)
    except Exception:
        return pd.DataFrame()

def _atr14(df: pd.DataFrame) -> float:
    return float((df["High"]-df["Low"]).abs().rolling(14).mean().iloc[-1])

@app.post("/api/portfolio/run")
def run():
    raw = _stock_screen().body
    try:
        picks = json.loads(raw).get("results", [])[:8]
    except Exception:
        picks = []
    plans = []
    for r in picks:
        t = r["ticker"]
        df = _dl(t)
        if df.empty:
            continue
        c = float(df["Close"].iloc[-1])
        atr = _atr14(df)
        hh = float(df["Close"].rolling(20).max().iloc[-1])
        entry = max(c, hh)
        stop = entry - 2*atr
        risk = 0.0075 * EQUITY
        size = max(0, math.floor(risk / max(0.01, entry - stop)))
        plans.append({
            "ticker": t, "last": round(c,4), "entry": round(entry,4), "stop": round(stop,4),
            "atr": round(atr,4), "size": int(size), "score": r["mscore"]
        })
    plans.sort(key=lambda x: x["score"], reverse=True)
    return JSONResponse({"ok": True, "plans": plans})