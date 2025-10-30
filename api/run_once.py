from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import yfinance as yf, pandas as pd, numpy as np
from global_agents.state import set_last_decision
from global_agents.agents import ta_alpha, regime as regime_mod
from global_agents.agents.vwap_revert import compute as vwap_compute
from global_agents.agents.momentum_agent import compute as momentum_compute
from global_agents.agents.flow_agent import compute as flow_compute
from global_agents.agents.seasonal_agent import compute as seasonal_compute
from global_agents.agents.macro_agent import compute as macro_compute
from global_agents.agents.liquidity_agent import compute as liq_compute
from global_agents.agents.pair_revert import compute_pair as pair_compute
from global_agents.agents.corr_matrix import fetch_close, DEFAULT
from global_agents.core.fusion import fuse_v2
from global_agents.core.portfolio import suggest_position

app = FastAPI()

def fetch(symbol: str, period="60d", interval="1h") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise RuntimeError(f"no data for {symbol}")
    return df.dropna()

@app.post("/api/run_once")
async def run_once(req: Request):
    body = await req.json() if "application/json" in req.headers.get("content-type", "") else {}
    symbol = body.get("symbol", "EURUSD=X")
    try:
        df = fetch(symbol)
        ta_sig = ta_alpha.compute(df)
        reg = regime_mod.compute(df)
        regime_name = reg.get("regime", "normal")
        mom = momentum_compute(df)
        rev = vwap_compute(df)
        flow = flow_compute(df)
        season = seasonal_compute(df)
        macro = macro_compute(symbol)
        liq = liq_compute(df)
        universe = body.get("universe", DEFAULT)
        try:
            closes = fetch_close(universe, period="60d", interval="1h")
            if symbol in closes.columns:
                others = [c for c in closes.columns if c != symbol]
                corr_series = closes.pct_change().rolling(24).corr().iloc[-len(closes.columns):][symbol].dropna()
                max_corr = float(corr_series[others].abs().max()) if not corr_series.empty else 0.0
                corr_penalty = min(0.5, max_corr * 0.2)
                peer_df = None
                top_peer = None
                if others:
                    top_peer = max(others, key=lambda t: float(abs(corr_series.get(t, 0.0))))
                    if top_peer:
                        peer_df = fetch(top_peer)
                pair_rev = pair_compute(df, peer_df) if peer_df is not None else {"score": 0.0, "type": "pair_revert"}
            else:
                corr_penalty = 0.0
                pair_rev = {"score": 0.0, "type": "pair_revert"}
        except Exception:
            corr_penalty = 0.0
            pair_rev = {"score": 0.0, "type": "pair_revert"}

        signals = {
            "momentum": mom.get("score", 0.0),
            "reversion": rev.get("score", 0.0),
            "flow": flow.get("score", 0.0),
            "seasonality": season.get("score", 0.0),
            "macro": macro.get("score", 0.0),
            "liquidity": liq.get("score", 0.0),
        }
        fused = fuse_v2(symbol, regime_name, signals, corr_penalty)
        price = float(df["Close"].iloc[-1])
        sizing = suggest_position(symbol, price, fused["score"], fused.get("confidence", 0.0))
        decision = {**fused, "position": sizing}
        set_last_decision(decision)
        diagnostics = {
            "ta": ta_sig,
            "regime": reg,
            "momentum": mom,
            "reversion": rev,
            "flow": flow,
            "seasonality": season,
            "macro": macro,
            "liquidity": liq,
            "pair_revert": pair_rev,
            "corr_penalty": corr_penalty,
        }
        return JSONResponse({"ok": True, "decision": decision, "diagnostics": diagnostics})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)