from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from global_agents.state import set_last_decision
from global_agents.core.fusion import adaptive_fuse
from global_agents.agents import perf_tracker
from global_agents.memory import market_memory
from global_agents.portfolio.execution import size, sl_tp, exposure_cap

app = FastAPI()

def fetch(symbol: str, period="60d", interval="1h"):
    import yfinance as yf
    import pandas as pd
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise RuntimeError(f"no data for {symbol}")
    return df.dropna()

@app.post("/api/run_once")
async def run_once(req: Request):
    body = await req.json() if "application/json" in req.headers.get("content-type", "") else {}
    symbol = body.get("symbol", "EURUSD=X")
    try:
        from global_agents.agents import ta_alpha, regime as regime_mod
        from global_agents.agents.vwap_revert import compute as vwap_compute
        from global_agents.agents.momentum_agent import compute as momentum_compute
        from global_agents.agents.flow_agent import compute as flow_compute
        from global_agents.agents.seasonal_agent import compute as seasonal_compute
        from global_agents.agents.macro_agent import compute as macro_compute
        from global_agents.agents.liquidity_agent import compute as liq_compute
        from global_agents.agents.ml_signal import compute as ml_compute

        df = fetch(symbol)
        ta_sig = ta_alpha.compute(df)
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
            {"type": "ta", **ta_sig},
            {"type": "momentum", **mom},
            {"type": "reversion", **rev},
            {"type": "flow", **flo},
            {"type": "seasonality", **sea},
            {"type": "macro", **mac},
            {"type": "liquidity", **liq},
            {"type": "ml", **ml},
        ]
        corr_penalty = 0.0
        fused = adaptive_fuse(symbol, signals, reg, corr_penalty)
        price = float(df["Close"].iloc[-1])
        direction = fused["action"]
        stop_pips = float(body.get("stop_pips", 30))
        balance = float(body.get("balance", 10000))
        risk_pct = float(body.get("risk_pct", 0.01))
        vol = size(balance, risk_pct, stop_pips)
        sl, tp = sl_tp(price, direction, stop_pips)
        decision = {**fused, "sl": sl, "tp": tp, "size": vol}
        # simulate a mock pnl update after candle close
        pnl = +0.3 if decision["action"] == "BUY" else -0.1 if decision["action"] == "SELL" else 0.0
        perf_tracker.log_trade("fusion", pnl=pnl, action=decision["action"], symbol=symbol)
        if decision["action"] != "HOLD" and pnl > 0:
            market_memory.remember({"symbol": symbol, "regime": reg.get("regime")}, pnl)
        set_last_decision(decision)
        return JSONResponse({"ok": True, "decision": decision})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/run_once")
def run_once_get(
    symbol: str = Query("EURUSD=X"),
    tf: str = Query("1h"),
    stop_pips: float = Query(30),
    balance: float = Query(10000),
    risk_pct: float = Query(0.01),
):
    try:
        from global_agents.agents import ta_alpha, regime as regime_mod
        from global_agents.agents.vwap_revert import compute as vwap_compute
        from global_agents.agents.momentum_agent import compute as momentum_compute
        from global_agents.agents.flow_agent import compute as flow_compute
        from global_agents.agents.seasonal_agent import compute as seasonal_compute
        from global_agents.agents.macro_agent import compute as macro_compute
        from global_agents.agents.liquidity_agent import compute as liq_compute
        from global_agents.agents.ml_signal import compute as ml_compute

        df = fetch(symbol, period="60d", interval=tf)
        ta_sig = ta_alpha.compute(df)
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
            {"type": "ta", **ta_sig},
            {"type": "momentum", **mom},
            {"type": "reversion", **rev},
            {"type": "flow", **flo},
            {"type": "seasonality", **sea},
            {"type": "macro", **mac},
            {"type": "liquidity", **liq},
            {"type": "ml", **ml},
        ]
        fused = adaptive_fuse(symbol, signals, reg, corr_penalty=0.0)
        price = float(df["Close"].iloc[-1])
        vol = size(balance, risk_pct, float(stop_pips))
        sl, tp = sl_tp(price, fused["action"], float(stop_pips))
        decision = {**fused, "sl": sl, "tp": tp, "size": vol}
        pnl = +0.3 if decision["action"] == "BUY" else -0.1 if decision["action"] == "SELL" else 0.0
        perf_tracker.log_trade("fusion", pnl=pnl, action=decision["action"], symbol=symbol)
        if decision["action"] != "HOLD" and pnl > 0:
            market_memory.remember({"symbol": symbol, "regime": reg.get("regime")}, pnl)
        set_last_decision(decision)
        return JSONResponse({"ok": True, "decision": decision})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)