from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import List
from global_agents.agents.corr_matrix import fetch_close, top_pairs, DEFAULT

app = FastAPI()

@app.get("/api/correl_scan")
def scan(universe: List[str] = Query(DEFAULT), window: int = 24, k: int = 5):
    try:
        tickers = universe if isinstance(universe, list) else DEFAULT
        df = fetch_close(tickers, period="60d", interval="1h")
        if df.empty or df.shape[1] == 0:
            return JSONResponse({"ok": False, "error": "no symbols fetched (rate-limit or empty responses)"}, status_code=502)
        return JSONResponse({"ok": True, "window": window, "top_pairs": top_pairs(df, window, k)})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)