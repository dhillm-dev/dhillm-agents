from typing import Dict

def fuse(symbol: str, ta_sig: Dict, regime: Dict, corr_penalty: float = 0.0) -> Dict:
    score = ta_sig["score"] * (0.7 if regime["regime"] == "volatile" else 1.0) - corr_penalty
    action = "BUY" if score > 0.2 else "SELL" if score < -0.2 else "HOLD"
    return {"symbol": symbol, "action": action, "score": float(score)}