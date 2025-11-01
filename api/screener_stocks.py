from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd, yfinance as yf
from typing import List
import math

app = FastAPI()

EU_TICKERS = [
    "ENEL.MI","ENI.MI","AIR.PA","OR.PA","DG.PA","BAS.DE","BAYN.DE","HEN3.DE",
    "SAN.MC","IBE.MC","VOD.L","RR.L","GLEN.L","AMS.AS","RAND.AS"
]

def _safe_download(ticker: str, period="30d", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False, threads=False)
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def _gbp_to_eur_fx()->float:
    df = _safe_download("GBPEUR=X", period="7d", interval="1d")
    try: return float(df["Close"].iloc[-1])
    except Exception: return 1.16

def _last_close_eur(t: str, fx: float) -> float:
    df = _safe_download(t, period="10d", interval="1d")
    if df.empty: return math.nan
    px = float(df["Close"].iloc[-1])
    if t.endswith(".L"): px = px * 0.01 * fx  # GBp -> GBP -> EUR
    return px

def _avg_turnover_eur(t: str, fx: float) -> float:
    df = _safe_download(t, period="45d", interval="1d")
    if df.empty or "Volume" not in df: return 0.0
    val = (df["Close"] * df["Volume"].astype(float)).tail(20).mean()
    return float(val * (0.01 * fx if t.endswith(".L") else 1.0))

def _mscore(df: pd.DataFrame) -> float:
    if df.empty or len(df) < 200: return 0.0
    c = df["Close"]
    ema20 = c.ewm(span=20).mean()
    sma50 = c.rolling(50).mean()
    sma200 = c.rolling(200).mean()
    cond = (ema20.iloc[-1] > sma50.iloc[-1] > sma200.iloc[-1]) and (c.iloc[-1] > sma50.iloc[-1])
    atr = (df["High"] - df["Low"]).abs().rolling(14).mean().iloc[-1]
    hh20 = c.rolling(20).max().iloc[-1]
    bo = max(0.0, (c.iloc[-1]-hh20)/max(1e-9, atr))
    comp = max(0.0, 1.0 - atr/max(1e-9, c.iloc[-1]))
    base = 0.35*float(cond) + 0.35*bo + 0.30*comp
    return float(min(1.0, max(0.0, base)))

@app.get("/api/screener/stocks")
def screener(max_price: float = 50.0, min_turnover: float = 1_000_000.0, limit: int = 30):
    fx = _gbp_to_eur_fx()
    rows = []
    for t in EU_TICKERS:
        try:
            px = _last_close_eur(t, fx)
            if (not px) or math.isnan(px) or px <= 1.0 or px > max_price:
                continue
            tov = _avg_turnover_eur(t, fx)
            if tov < min_turnover:
                continue
            df = _safe_download(t, period="400d", interval="1d")
            m = _mscore(df)
            rows.append({"ticker": t, "price_eur": round(px,4), "avg_turnover_eur": int(tov), "mscore": round(m,4)})
        except Exception:
            continue
    rows.sort(key=lambda r: r["mscore"], reverse=True)
    return JSONResponse({"ok": True, "results": rows[:limit]})