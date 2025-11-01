import time
import typing as t
import pandas as pd
import yfinance as yf


def safe_download(
    ticker: str,
    period: str = "60d",
    interval: str = "1h",
    tries: int = 4,
    backoff: float = 1.7,
) -> pd.DataFrame:
    """
    Robust fetch that tolerates Yahoo hiccups (empty/HTML/rate-limit).
    Strategy:
      1) yf.download(..., threads=False, progress=False)
      2) fallback to yf.Ticker(t).history(...)
      3) small exponential backoff between tries
    Raises RuntimeError if all attempts fail.
    """
    last_exc: t.Optional[Exception] = None

    for n in range(tries):
        try:
            # Primary path
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,  # more deterministic on serverless
            )
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df.dropna()

            # Fallback path
            h = yf.Ticker(ticker).history(
                period=period, interval=interval, auto_adjust=True
            )
            if isinstance(h, pd.DataFrame) and not h.empty:
                return h.dropna()

            # If we reach here, treat as transient failure
            raise ValueError("empty response")
        except Exception as e:
            last_exc = e
            # exponential backoff (1, ~1.7, ~2.9, ~4.9s)
            time.sleep(backoff ** n)

    raise RuntimeError(f"download failed for {ticker}: {last_exc}")