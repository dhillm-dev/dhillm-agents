import os
import json
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL")
_r = None

if REDIS_URL:
    try:
        import redis
        _r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        _r = None

_KEY = "orchestrator:last_decision"
_last = None

def set_last_decision(obj: dict) -> None:
    global _last
    _last = obj
    if _r:
        _r.set(_KEY, json.dumps(obj))

def get_last_decision() -> Optional[dict]:
    if _r:
        raw = _r.get(_KEY)
        return json.loads(raw) if raw else None
    return _last
