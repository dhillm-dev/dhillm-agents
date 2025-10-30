import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, Any
from ..agents import ta_alpha, regime, corr_matrix
from ..state import set_last_decision

def fetch_data(symbol: str, timeframe: str = "1h", period: str = "30d") -> pd.DataFrame:
    """Fetch OHLCV data for the given symbol."""
    ticker = yf.Ticker(symbol)
    
    # Map timeframe to yfinance interval
    interval_map = {
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "4h": "4h", "1d": "1d"
    }
    interval = interval_map.get(timeframe, "1h")
    
    df = ticker.history(period=period, interval=interval)
    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")
    
    return df

def fuse_signals(ta_result: Dict, regime_result: Dict, corr_result: Dict) -> Dict[str, Any]:
    """Combine signals from all agents into a single decision."""
    
    # Base score from TA agent
    base_score = ta_result.get("score", 0)
    
    # Regime adjustment
    regime_multiplier = {
        "calm": 0.5,      # Reduce signal strength in calm markets
        "normal": 1.0,    # Normal signal strength
        "volatile": 1.5   # Amplify signals in volatile markets
    }
    regime = regime_result.get("regime", "normal")
    adjusted_score = base_score * regime_multiplier.get(regime, 1.0)
    
    # Correlation adjustment (reduce risk if high correlation)
    avg_correlation = corr_result.get("avg_correlation", 0)
    if abs(avg_correlation) > 0.7:  # High correlation = higher risk
        adjusted_score *= 0.7
    
    # Final decision
    if adjusted_score > 0.5:
        decision = "BUY"
    elif adjusted_score < -0.5:
        decision = "SELL"
    else:
        decision = "HOLD"
    
    return {
        "decision": decision,
        "score": float(adjusted_score),
        "confidence": min(abs(adjusted_score), 1.0),
        "components": {
            "ta": ta_result,
            "regime": regime_result,
            "correlation": corr_result
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def run_analysis(symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
    """Run complete analysis pipeline for a symbol."""
    try:
        # Fetch data
        df = fetch_data(symbol, timeframe)
        
        # Run all agents
        ta_result = ta_alpha.compute(df)
        regime_result = regime.compute(df)
        corr_result = corr_matrix.compute(symbol)
        
        # Fuse results
        final_decision = fuse_signals(ta_result, regime_result, corr_result)
        
        # Save decision
        set_last_decision(final_decision)
        
        return final_decision
        
    except Exception as e:
        error_result = {
            "decision": "ERROR",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        set_last_decision(error_result)
        return error_result