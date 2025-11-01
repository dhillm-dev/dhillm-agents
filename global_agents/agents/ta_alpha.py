import pandas as pd

def compute(df: pd.DataFrame) -> dict:
    """Compute RSI + MACD technical analysis signals."""
    try:
        # Lazy import ta to avoid hard dependency; fallback if unavailable
        try:
            import ta  # type: ignore
        except Exception as ie:
            raise RuntimeError(f"ta library unavailable: {ie}")
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
        
        # Calculate MACD
        macd_diff = ta.trend.MACD(df["Close"]).macd_diff().iloc[-1]
        
        # Generate score based on RSI and MACD
        rsi_score = 1 if rsi < 30 else -1 if rsi > 70 else 0
        macd_score = 0.5 if macd_diff > 0 else -0.5
        
        total_score = rsi_score + macd_score
        
        return {
            "rsi": float(rsi),
            "macd": float(macd_diff),
            "score": float(total_score),
            "rsi_signal": "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral",
            "macd_signal": "bullish" if macd_diff > 0 else "bearish"
        }
    except Exception as e:
        # Soft fallback when ta not available or computation fails
        return {
            "rsi": 50.0,
            "macd": 0.0,
            "score": 0.0,
            "error": str(e)
        }