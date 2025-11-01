# global_agents/utils/safe_download.py
import time
import typing as t
import datetime as dt

import pandas as pd
import requests
import yfinance as yf

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

def _yf_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*", "Connection": "keep-alive"})
    s.timeout = 15
    return s

def _binance_klines(symbol: str, interval: str = "1h", limit: int = 720) -> pd.DataFrame:
    """
    Minimal, no-key fallback for crypto. Uses USDT pairs (close ~ USD).
    symbol examples: BTC-USD -> BTCUSDT, ETH-USD -> ETHUSDT
    """
    mapping = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT"}
    if symbol not in mapping:
        raise RuntimeError("binance fallback not available for symbol")
    sym = mapping[symbol]

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": sym, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
    r.raise_for_status()
    raw = r.json()
    if not raw:
        raise RuntimeError("empty binance klines")

    # Klines: [openTime, open, high, low, close, volume, closeTime, ...]
    df = pd.DataFrame(
        raw,
        columns=[
            "open_time","open","high","low","close","volume","close_time",
            "qav","num_trades","taker_base","taker_quote","ignore"
        ],
    )
    df["Date"] = pd.to_datetime(df["close_time"], unit="ms", utc=True).dt.tz_localize(None)
    df["Close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.set_index("Date")[["Close"]].dropna()
    # mimic yf.download format (index ascending)
    return df

def safe_download(
    ticker: str,
    period: str = "60d",
    interval: str = "1h",
    tries: int = 4,
    backoff: float = 1.7,
) -> pd.DataFrame:
    """
    Robust Yahoo fetch with:
      - persistent session + UA (reduces HTML block pages),
      - retries with exponential backoff,
      - fallback to Ticker.history,
      - crypto fallback via Binance for BTC-USD/ETH-USD when Yahoo blocks.

    Raises RuntimeError after all attempts fail.
    """
    last_exc: t.Optional[Exception] = None
    sess = _yf_session()

    for n in range(tries):
        try:
            # Primary path: yf.download with session
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
                session=sess,
            )
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df.dropna()

            # Secondary: Ticker.history with session
            hist = yf.Ticker(ticker, session=sess).history(
                period=period,
                interval=interval,
                auto_adjust=True,
            )
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                return hist.dropna()

            # Crypto fallback via Binance (no key), only for 1h-like use
            if ticker in ("BTC-USD", "ETH-USD"):
                bdf = _binance_klines(ticker, interval="1h", limit=720)
                if not bdf.empty:
                    return bdf

            raise ValueError("empty response from providers")
        except Exception as e:
            last_exc = e
            time.sleep(backoff ** n)

    raise RuntimeError(f"download failed for {ticker}: {last_exc}")