from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
from global_agents.state import set_last_decision
from global_agents.agents import ta_alpha, regime as regime_mod
from global_agents.core.fusion import fuse
from global_agents.utils.data import safe_download

app = FastAPI()

def fetch(symbol: str) -> pd.DataFrame:
    return safe_download(symbol)

@app.post("/api/run_once")
async def run_once(req: Request):
    try:
        body = {}
        ct = req.headers.get("content-type", "")
        if "application/json" in ct.lower():
            # guard against empty body with JSON content-type
            try:
                body = await req.json()
            except Exception:
                body = {}
        symbol = (body or {}).get("symbol", "EURUSD=X")

        df = fetch(symbol)
        ta_sig = ta_alpha.compute(df)
        reg    = regime_mod.compute(df)
        decision = fuse(symbol, ta_sig, reg, corr_penalty=0.0)
        set_last_decision(decision)
        return JSONResponse({"ok": True, "decision": decision})
    except RuntimeError as e:
        # Upstream data problem: return 502 to distinguish from app bugs
        return JSONResponse({"ok": False, "error": f"data_source: {e}"}, status_code=502)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)