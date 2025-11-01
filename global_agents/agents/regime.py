import pandas as pd

def compute(df: pd.DataFrame) -> dict:
    """Compute ATR% regime detection."""
    try:
        # Try ta-based ATR first
        atr = None
        try:
            import ta  # type: ignore
            atr = ta.volatility.AverageTrueRange(
                df["High"], df["Low"], df["Close"]
            ).average_true_range()
        except Exception:
            # Fallback: simple TR rolling mean
            tr = (df["High"] - df["Low"]).abs()
            atr = tr.rolling(14).mean()
        
        # Calculate ATR percentage
        atrp = float(atr.iloc[-1] / df["Close"].iloc[-1])
        
        # Determine regime based on ATR%
        if atrp < 0.01:
            regime = "calm"
        elif atrp < 0.02:
            regime = "normal"
        else:
            regime = "volatile"
        
        return {
            "atrp": atrp,
            "regime": regime,
            "atr_raw": float(atr.iloc[-1]),
            "close_price": float(df["Close"].iloc[-1])
        }
    except Exception as e:
        return {
            "atrp": 0.01,
            "regime": "normal",
            "error": str(e)
        }