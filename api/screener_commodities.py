from fastapi import FastAPI
from fastapi.responses import JSONResponse
import yfinance as yf, pandas as pd

app = FastAPI()
COMMS = ["GLD","SLV","USO","DBA","DBC","BNO","PALL","PPLT"]

def _dl(sym, period="400d"):
    try:
        return yf.download(sym, period=period, interval="1d", auto_adjust=True, progress=False, threads=False)
    except Exception:
        return pd.DataFrame()

def _mscore(sym: str) -> float:
    df = _dl(sym)
    if df.empty or len(df) < 200: return 0.0
    c = df["Close"]
    ema20 = c.ewm(span=20).mean()
    sma50 = c.rolling(50).mean()
    sma200 = c.rolling(200).mean()
    return float(1.0 if (ema20.iloc[-1] > sma50.iloc[-1] > sma200.iloc[-1] and c.iloc[-1] > sma50.iloc[-1]) else 0.0)

@app.get("/api/screener/commodities")
def comms(limit: int = 10):
    rows = [{"symbol": s, "mscore": _mscore(s)} for s in COMMS]
    rows.sort(key=lambda r: r["mscore"], reverse=True)
    return JSONResponse({"ok": True, "results": rows[:limit]})