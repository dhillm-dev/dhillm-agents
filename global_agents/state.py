import os, json, threading
from typing import Any, Dict, Optional

# ---- In-memory fallback (thread-safe) ----
_lock = threading.Lock()
_last: Optional[Dict[str, Any]] = None

def _mem_set(decision: Optional[Dict[str, Any]]) -> None:
    global _last
    with _lock:
        _last = decision

def _mem_get() -> Optional[Dict[str, Any]]:
    with _lock:
        return _last

# ---- Optional Redis backend ----
REDIS_URL = os.getenv("REDIS_URL")
_redis = None
_key = "orchestrator:last_decision"

if REDIS_URL:
    try:
        import redis
        _redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        # probe connectivity once (don’t crash if unavailable)
        try:
            _redis.ping()
        except Exception:
            _redis = None
    except Exception:
        _redis = None

def set_last_decision(decision: Optional[Dict[str, Any]]) -> None:
    """
    decision: e.g. {"symbol":"EURUSD=X","action":"BUY","score":0.42, ...}
    None clears it.
    """
    if _redis:
        try:
            if decision is None:
                _redis.delete(_key)
            else:
                _redis.set(_key, json.dumps(decision))
            return
        except Exception:
            pass  # fallback to memory
    _mem_set(decision)

def get_last_decision() -> Optional[Dict[str, Any]]:
    if _redis:
        try:
            raw = _redis.get(_key)
            return json.loads(raw) if raw else None
        except Exception:
            pass
    return _mem_get()