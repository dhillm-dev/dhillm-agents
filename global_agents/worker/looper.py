import os, time, requests, traceback, random, json


# Prefer explicit API_HOST (full base URL), default to local dev
API_HOST = os.getenv("API_HOST", "http://127.0.0.1:8000").rstrip("/")
UNIVERSE = [s.strip() for s in os.getenv("UNIVERSE", "EURUSD=X,BTC-USD").split(",") if s.strip()]
TF = os.getenv("TF", "1h")
COOLDOWN = int(os.getenv("COOLDOWN", "20"))
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))


def _post(path, payload=None):
    url = f"{API_HOST}{path}"
    try:
        r = requests.post(url, json=payload or {}, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        return {"ok": False, "status": r.status_code, "text": r.text[:200]}
    except requests.ReadTimeout as e:
        return {"ok": False, "error": f"timeout: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _get(path):
    url = f"{API_HOST}{path}"
    try:
        r = requests.get(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        return {"ok": False, "status": r.status_code, "text": r.text[:200]}
    except requests.ReadTimeout as e:
        return {"ok": False, "error": f"timeout: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def cycle_equities():
    _ = _get("/api/screener/stocks?max_price=50&limit=30")
    return _post("/api/portfolio/run", {})


def run_once(symbol: str) -> None:
    url = f"{API_HOST}/api/run_once"
    payload = {"symbol": symbol} if symbol else None
    try:
        if payload is not None:
            r = requests.post(url, json=payload, timeout=HTTP_TIMEOUT)
        else:
            # No body → avoid setting Content-Type; send minimal POST
            r = requests.post(url, timeout=HTTP_TIMEOUT)
        if r.status_code == 502:
            # Upstream data source issue; log and move on (no immediate retry)
            print(f"[run_once][data_source] {symbol} -> 502 {r.text[:160]}")
            return
        print(f"[run_once] {symbol} -> {r.status_code} {r.text[:240]}")
    except requests.ReadTimeout as e:
        # Upstream slow; log and let loop retry without crashing
        print(f"[worker] run_once timeout — likely upstream data slow. Will retry: {e}")
    except Exception as e:
        # Log concise error and keep loop healthy
        print(f"[worker] run_once error: {e}")


if __name__ == "__main__":
    print(f"[worker] API_HOST={API_HOST} UNIVERSE={UNIVERSE} TF={TF} COOLDOWN={COOLDOWN}")
    # Small warmup delay (container cold start)
    time.sleep(2)
    last_eq = 0.0
    EQUITIES_INTERVAL = int(os.getenv("EQUITIES_INTERVAL", "60"))  # seconds
    while True:
        # Core FX/crypto loop
        for s in UNIVERSE:
            run_once(s)
        # Equities cycle with interval gating
        now = time.time()
        if now - last_eq >= EQUITIES_INTERVAL:
            try:
                print("== equities cycle ==")
                print(cycle_equities())
            except Exception as e:
                print("[worker] equities cycle error:", e)
            finally:
                last_eq = now
        # small jitter to avoid sync hammering upstream providers
        time.sleep(COOLDOWN + random.uniform(0, 5))