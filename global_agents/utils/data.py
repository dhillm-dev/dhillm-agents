import time
from typing import Tuple, Optional
import pandas as pd
import yfinance as yf

# Combos to try, in order (broad -> narrower -> daily fallback)
FALLBACKS: Tuple[Tuple[str,str], ...] = (
    ("60d","1h"),
    ("30d","1h"),
    ("14d","1h"),
    ("7d","1h"),
    ("1y","1d"),   # daily fallback
)

def safe_download(
    symbol: str,
    fallbacks: Tuple[Tuple[str,str], ...] = FALLBACKS,
    retries: int = 3,
    backoff: float = 0.8,
    threads: bool = False,
) -> pd.DataFrame:
    """
    Try multiple (period, interval) combos; on network/JSON issues, retry with backoff.
    Returns a non-empty OHLCV frame or raises RuntimeError with a concise reason.
    """
    last_err: Optional[Exception] = None
    for (period, interval) in fallbacks:
        for attempt in range(1, retries + 1):
            try:
                df = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    progress=False,
                    threads=threads,
                )
                # yfinance can return empty on transient/unsupported combos
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Normalize columns (Close exists for TA; ensure no all-NA)
                    df = df.dropna(how="all")
                    if not df.empty and "Close" in df.columns:
                        return df
                    # Some “meta” empties come without Close; keep trying
                raise RuntimeError(f"empty frame ({period},{interval})")
            except Exception as e:
                last_err = e
                # Exponential-ish backoff
                if attempt < retries:
                    time.sleep(backoff * attempt)
        # try next fallback combo
    raise RuntimeError(f"download failed for {symbol}: {last_err}")