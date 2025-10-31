from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from global_agents.core.fusion import fuse_v2

app = FastAPI()


def fetch(symbol: str, period="60d", interval="1h"):
    import yfinance as yf
    import pandas as pd
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise RuntimeError(f"no data for {symbol}")
    return df.dropna()


@app.get("/api/diagnostics")
def diagnostics(symbol: str = Query("EURUSD=X"), tf: str = Query("1h")):
    try:
        from global_agents.agents import ta_alpha, regime as regime_mod
        from global_agents.agents.vwap_revert import compute as vwap_compute
        from global_agents.agents.momentum_agent import compute as momentum_compute
        from global_agents.agents.flow_agent import compute as flow_compute
        from global_agents.agents.seasonal_agent import compute as seasonal_compute
        from global_agents.agents.macro_agent import compute as macro_compute
        from global_agents.agents.liquidity_agent import compute as liq_compute
        from global_agents.agents.ml_signal import compute as ml_compute
        period = "60d"
        interval = tf
        df = fetch(symbol, period=period, interval=interval)
        ta = ta_alpha.compute(df)
        reg = regime_mod.compute(df)
        mom = momentum_compute(df)
        rev = vwap_compute(df)
        flo = flow_compute(df)
        sea = seasonal_compute(df)
        mac = macro_compute(symbol)
        liq = liq_compute(df)
        features = {"momentum": mom["score"], "reversion": rev["score"], "flow": flo["score"], "seasonality": sea["score"]}
        ml = ml_compute(features)
        signals = [
            {"type": "ta", **ta},
            {"type": "momentum", **mom},
            {"type": "reversion", **rev},
            {"type": "flow", **flo},
            {"type": "seasonality", **sea},
            {"type": "macro", **mac},
            {"type": "liquidity", **liq},
            {"type": "ml", **ml},
        ]
        fused = fuse_v2(symbol, signals, reg, corr_penalty=0.0, hist_weight=1.0)
        return JSONResponse({"ok": True, "signals": signals, "fused": fused})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)