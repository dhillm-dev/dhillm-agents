from typing import Dict, List
from global_agents.learn.weights_store import load_weights


def _conf(score: float) -> float:
    # map |score| → confidence in [0,1]
    return max(0.0, min(1.0, abs(score)))


def fuse_v2(symbol: str, signals: List[Dict], regime: Dict, corr_penalty: float = 0.0, hist_weight: float = 1.0) -> Dict:
    """Adaptive fusion brain v2.

    - signals: list of dicts, each with keys: {"type", "score", ...}
    - regime: dict with at least {"regime": "calm"|"normal"|"volatile"}
    - corr_penalty: optional correlation penalty [0,1]
    - hist_weight: optional historical weight [0,1]
    """
    damp = 0.7 if regime.get("regime") == "volatile" else 1.0
    num, den = 0.0, 1e-9
    details: Dict[str, Dict] = {}
    for s in signals:
        sc = float(s.get("score", 0.0))
        c = _conf(sc)
        w = c * damp
        num += w * sc
        den += w
        t = s.get("type", "unknown")
        details[t] = {"score": sc, "conf": c, "w": w}
    fused = (num / den) - max(0.0, float(corr_penalty)) - max(0.0, 1.0 - float(hist_weight)) * 0.2
    action = "BUY" if fused > 0.2 else "SELL" if fused < -0.2 else "HOLD"
    return {
        "symbol": symbol,
        "action": action,
        "score": float(fused),
        "details": details,
        "regime": regime,
        "penalty": float(corr_penalty),
    }


def adaptive_fuse(symbol: str, signals: List[Dict], regime: Dict, corr_penalty: float = 0.0) -> Dict:
    learned = load_weights()  # {agent_type: weight in [0,1], sum=1 (softmax)}
    damp = 0.7 if regime.get("regime") == "volatile" else 1.0
    total, weight_sum, details = 0.0, 1e-9, {}

    # If no learned weights → equal fallback
    if not learned:
        n = max(1, len(signals))
        learned = {s.get("type", "unknown"): 1.0 / float(n) for s in signals}

    for s in signals:
        ag = s.get("type", "unknown")
        sc = float(s.get("score", 0.0))
        conf = max(0.0, min(1.0, abs(sc)))
        lw = float(learned.get(ag, 0.0))  # learned share [0,1]
        w = (conf + 0.5) * lw * damp      # add baseline 0.5 to avoid zeroing
        total += w * sc
        weight_sum += w
        details[ag] = {"score": sc, "conf": conf, "w": w, "learned": lw}

    fused = (total / weight_sum) - max(0.0, float(corr_penalty))
    action = "BUY" if fused > 0.2 else "SELL" if fused < -0.2 else "HOLD"
    return {
        "symbol": symbol,
        "action": action,
        "score": float(fused),
        "details": details,
        "regime": regime,
        "penalty": float(corr_penalty),
    }
