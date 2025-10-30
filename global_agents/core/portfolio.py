from typing import Dict


def suggest_position(symbol: str, price: float, score: float, confidence: float, exposure_cap: float = 0.02) -> Dict:
    weight = min(exposure_cap, max(0.0, abs(score) * confidence * exposure_cap))
    direction = 1 if score > 0 else -1 if score < 0 else 0
    size = weight * direction
    sl = max(0.001, 0.01 * price)
    tp = max(0.001, 0.02 * price)
    return {"symbol": symbol, "size": float(size), "sl": float(sl), "tp": float(tp), "price": float(price)}