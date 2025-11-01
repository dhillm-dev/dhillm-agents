import pandas as pd
from global_agents.utils.safe_download import safe_download

# Default multi-asset universe
DEFAULT = [
    "EURUSD=X","GBPUSD=X","USDJPY=X",
    "BTC-USD","ETH-USD",
    "^GSPC","GLD","USO"
]

def fetch_close(tickers, period="60d", interval="1h"):
    out = {}
    for t in tickers:
        try:
            df = safe_download(t, period=period, interval=interval)
            out[t] = df["Close"]
        except Exception:
            # skip silently; correl_scan should still work with remaining assets
            pass
    return pd.DataFrame(out).dropna(how="all")

def top_pairs(df: pd.DataFrame, window=24, k=5):
    if df is None or df.empty or len(df.columns) < 2 or len(df) < window + 2:
        return []
    corr = df.pct_change().rolling(window).corr()
    try:
        snap = corr.iloc[-len(df.columns):].unstack().dropna()
        if not isinstance(snap.index, pd.MultiIndex) or snap.index.nlevels < 2:
            raise ValueError("insufficient index levels for pair extraction")
    except Exception:
        # Fallback: static correlation over recent window
        mat = df.pct_change().tail(window).corr().abs()
        seen, picks = set(), []
        for a in mat.columns:
            for b in mat.columns:
                if a == b:
                    continue
                key = tuple(sorted((a, b)))
                if key in seen:
                    continue
                seen.add(key)
                picks.append((a, b, float(mat.loc[a, b])))
        return sorted(picks, key=lambda x: x[2], reverse=True)[:k]
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