import pandas as pd, yfinance as yf

# Default multi-asset universe
DEFAULT = [
    "EURUSD=X","GBPUSD=X","USDJPY=X",
    "BTC-USD","ETH-USD",
    "^GSPC","GLD","USO"
]

def fetch_close(tickers, period="60d", interval="1h"):
    d = yf.download(
        tickers,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=True,
        threads=True,
    )
    out = {}
    for t in tickers:
        try:
            out[t] = (
                d[t]["Close"]
                if isinstance(d.columns, pd.MultiIndex)
                else d["Close"]
            )
        except Exception:
            pass
    return pd.DataFrame(out).dropna(how="all")

def top_pairs(df: pd.DataFrame, window=24, k=5):
    corr = df.pct_change().rolling(window).corr()
    snap = corr.iloc[-len(df.columns):].unstack().dropna()
    snap = snap[
        snap.index.get_level_values(0) != snap.index.get_level_values(1)
    ]
    ranked = snap.abs().sort_values(ascending=False)
    # unique ordered pairs
    seen, picks = set(), []
    for (a, b), v in ranked.items():
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        picks.append((a, b, float(v)))
        if len(picks) >= k:
            break
    return picks