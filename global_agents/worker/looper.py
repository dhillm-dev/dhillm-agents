import os, time, json, requests

API_BASE   = os.getenv("API_BASE", "http://127.0.0.1:8000")
UNIVERSE   = [s.strip() for s in os.getenv("UNIVERSE", "EURUSD=X,BTC-USD").split(",") if s.strip()]
TF         = os.getenv("TF", "1h")
COOLDOWN   = int(os.getenv("COOLDOWN", "20"))
HTTP_TOUT  = int(os.getenv("HTTP_TIMEOUT", "20"))

def run_once(symbol: str):
    url = f"{API_BASE}/api/run_once"
    payload = {"symbol": symbol, "tf": TF}
    r = requests.post(url, json=payload, timeout=HTTP_TOUT)
    r.raise_for_status()
    return r.json()

def main():
    print(f"[looper] API_BASE={API_BASE} UNIVERSE={UNIVERSE} TF={TF} COOLDOWN={COOLDOWN}s")
    while True:
        for sym in UNIVERSE:
            try:
                out = run_once(sym)
                print(f"[run_once] {sym}: {json.dumps(out)[:200]}")
            except Exception as e:
                print(f"[error] {sym}: {e}")
            time.sleep(2)  # tiny gap between symbols
        time.sleep(max(5, COOLDOWN))

if __name__ == "__main__":
    main()