from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
from global_agents.state import set_last_decision
from global_agents.agents import ta_alpha, regime as regime_mod
from global_agents.core.fusion import fuse
from global_agents.utils.safe_download import safe_download

app = FastAPI()

def fetch(symbol: str, period="60d", interval="1h") -> pd.DataFrame:
    df = safe_download(symbol, period=period, interval=interval)
    if df.empty:
        raise RuntimeError(f"no data for {symbol}")
    return df.dropna()

@app.post("/api/run_once")
async def run_once(req: Request):
    body = await req.json() if "application/json" in req.headers.get("content-type","") else {}
    symbol = body.get("symbol","EURUSD=X")
    try:
        df = fetch(symbol)
        ta_sig = ta_alpha.compute(df)
        reg    = regime_mod.compute(df)
        decision = fuse(symbol, ta_sig, reg, corr_penalty=0.0)
        set_last_decision(decision)
        return JSONResponse({"ok": True, "decision": decision})
    except Exception as e:
        # 502 -> upstream (Yahoo) likely hiccup; caller can retry
        return JSONResponse({"ok": False, "error": f"download/compute failed: {e}"}, status_code=502)