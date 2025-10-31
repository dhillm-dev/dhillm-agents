import os, json
from typing import Dict

PATH = os.getenv("WEIGHTS_PATH", "weights.json")
REDIS_URL = os.getenv("REDIS_URL")
_r = None
if REDIS_URL:
    try:
        import redis
        _r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        _r = None

KEY = "fusion:weights"


def save_weights(w: Dict[str, float]) -> None:
    if _r:
        _r.set(KEY, json.dumps(w))
        return
    with open(PATH, "w") as f:
        json.dump(w, f)


def load_weights() -> Dict[str, float]:
    if _r:
        raw = _r.get(KEY)
        if raw:
            return json.loads(raw)
    try:
        with open(PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}
