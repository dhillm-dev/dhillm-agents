import pandas as pd
import ta

def compute(df: pd.DataFrame) -> dict:
    """Compute ATR% regime detection."""
    try:
        # Calculate ATR
        atr = ta.volatility.AverageTrueRange(
            df["High"], df["Low"], df["Close"]
        ).average_true_range()
        
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
