import os, time, requests, traceback


# Prefer explicit API_HOST (full base URL), default to local dev
API_HOST = os.getenv("API_HOST", "http://127.0.0.1:8000").rstrip("/")
UNIVERSE = [s.strip() for s in os.getenv("UNIVERSE", "EURUSD=X,BTC-USD").split(",") if s.strip()]
TF = os.getenv("TF", "1h")
COOLDOWN = int(os.getenv("COOLDOWN", "20"))
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "20"))


def run_once(symbol: str) -> None:
    url = f"{API_HOST}/api/run_once"
    try:
        r = requests.post(url, json={"symbol": symbol}, timeout=HTTP_TIMEOUT)
        print(f"[run_once] {symbol} -> {r.status_code} {r.text[:240]}")
    except Exception:
        print(f"[run_once][ERROR] {symbol}")
        traceback.print_exc()


if __name__ == "__main__":
    print(f"[worker] API_HOST={API_HOST} UNIVERSE={UNIVERSE} TF={TF} COOLDOWN={COOLDOWN}")
    # Small warmup delay (container cold start)
    time.sleep(2)
    while True:
        for s in UNIVERSE:
            run_once(s)
        time.sleep(COOLDOWN)