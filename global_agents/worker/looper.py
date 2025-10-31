import os, time, json, requests


def resolve_api_base():
    base = os.getenv("API_BASE", "").strip()
    if base:
        return base.rstrip("/")
    host = os.getenv("API_HOST", "").strip()
    if host:
        return f"https://{host}".rstrip("/")
    ren = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if ren:
        return ren.rstrip("/")
    # local default for dev
    return "http://127.0.0.1:8000"


UNIVERSE   = [s.strip() for s in os.getenv("UNIVERSE", "EURUSD=X,BTC-USD").split(",") if s.strip()]
TF         = os.getenv("TF", "1h")
COOLDOWN   = int(os.getenv("COOLDOWN", "20"))
HTTP_TOUT  = int(os.getenv("HTTP_TIMEOUT", "20"))


def run_once(symbol: str, api_base: str):
    url = f"{api_base}/api/run_once"
    payload = {"symbol": symbol, "tf": TF}
    r = requests.post(url, json=payload, timeout=HTTP_TOUT)
    r.raise_for_status()
    return r.json()


def main():
    api_base = resolve_api_base()
    print(f"[worker] Using API base: {api_base}; UNIVERSE={UNIVERSE} TF={TF} COOLDOWN={COOLDOWN}s")
    while True:
        for sym in UNIVERSE:
            try:
                out = run_once(sym, api_base)
                print(f"[run_once] {sym}: {json.dumps(out)[:200]}")
            except Exception as e:
                print(f"[error] {sym}: {e}")
            time.sleep(2)
        time.sleep(max(5, COOLDOWN))

if __name__ == "__main__":
    main()