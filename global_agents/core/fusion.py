from typing import Dict


def fuse(symbol: str, ta_sig: Dict, regime: Dict, corr_penalty: float = 0.0) -> Dict:
    score = ta_sig["score"] * (0.7 if regime.get("regime") == "volatile" else 1.0) - corr_penalty
    action = "BUY" if score > 0.2 else "SELL" if score < -0.2 else "HOLD"
    return {"symbol": symbol, "action": action, "score": float(score)}


def fuse_v2(symbol: str, regime: str, signals: Dict, corr_penalty: float) -> Dict:
    w = {"momentum": 0.3, "reversion": 0.3, "flow": 0.15, "seasonality": 0.1, "macro": 0.05, "liquidity": 0.1}
    if regime == "trend":
        w["momentum"] += 0.15
        w["reversion"] -= 0.1
    elif regime == "mean":
        w["reversion"] += 0.15
        w["momentum"] -= 0.1
    s_mom = float(signals.get("momentum", 0.0))
    s_rev = float(signals.get("reversion", 0.0))
    s_flow = float(signals.get("flow", 0.0))
    s_season = float(signals.get("seasonality", 0.0))
    s_macro = float(signals.get("macro", 0.0))
    s_liq = float(signals.get("liquidity", 0.0))
    raw = (
        w["momentum"] * s_mom
        + w["reversion"] * s_rev
        + w["flow"] * s_flow
        + w["seasonality"] * s_season
        + w["macro"] * s_macro
        + w["liquidity"] * s_liq
    )
    penalty = min(0.5, max(0.0, float(corr_penalty)))
    score = raw * (1.0 - penalty)
    confidence = min(1.0, max(0.0, abs(score)))
    decision = "BUY" if score > 0.2 else "SELL" if score < -0.2 else "HOLD"
    return {
        "symbol": symbol,
        "score": float(score),
        "decision": decision,
        "confidence": float(confidence),
        "regime": regime,
    }