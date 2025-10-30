def compute(features: dict):
    s = 0.0
    for k in ("momentum", "reversion", "flow", "seasonality"):
        s += features.get(k, 0.0)
    score = max(-1, min(1, s / 8.0))
    return {"score": float(score), "type": "ml_signal"}