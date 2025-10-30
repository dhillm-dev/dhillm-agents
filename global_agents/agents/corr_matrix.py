import pandas as pd
import yfinance as yf
import numpy as np
from typing import Dict, List

# Multi-asset universe for correlation analysis
ASSET_UNIVERSE = {
    "fx": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"],
    "crypto": ["BTC-USD", "ETH-USD", "ADA-USD"],
    "indices": ["^GSPC", "^IXIC", "^DJI", "^VIX"],
    "metals": ["GC=F", "SI=F", "PL=F"]  # Gold, Silver, Platinum
}

def fetch_correlation_data(symbols: List[str], period: str = "30d") -> pd.DataFrame:
    """Fetch price data for correlation analysis."""
    try:
        data = yf.download(symbols, period=period, interval="1d")["Close"]
        return data.dropna()
    except Exception:
        return pd.DataFrame()

def compute(target_symbol: str) -> Dict:
    """Compute multi-asset correlation analysis."""
    try:
        # Flatten all symbols
        all_symbols = []
        for category in ASSET_UNIVERSE.values():
            all_symbols.extend(category)
        
        # Add target symbol if not in universe
        if target_symbol not in all_symbols:
            all_symbols.append(target_symbol)
        
        # Fetch data
        df = fetch_correlation_data(all_symbols)
        
        if df.empty or target_symbol not in df.columns:
            return {
                "avg_correlation": 0.0,
                "max_correlation": 0.0,
                "correlations": {},
                "error": "No data available"
            }
        
        # Calculate correlations with target symbol
        correlations = {}
        target_returns = df[target_symbol].pct_change().dropna()
        
        for symbol in df.columns:
            if symbol != target_symbol:
                other_returns = df[symbol].pct_change().dropna()
                # Align the series
                aligned_target, aligned_other = target_returns.align(other_returns, join='inner')
                if len(aligned_target) > 10:  # Minimum data points
                    corr = aligned_target.corr(aligned_other)
                    if not np.isnan(corr):
                        correlations[symbol] = float(corr)
        
        if not correlations:
            return {
                "avg_correlation": 0.0,
                "max_correlation": 0.0,
                "correlations": {},
                "error": "Insufficient correlation data"
            }
        
        # Calculate statistics
        corr_values = list(correlations.values())
        avg_correlation = float(np.mean(corr_values))
        max_correlation = float(max(corr_values, key=abs))
        
        return {
            "avg_correlation": avg_correlation,
            "max_correlation": max_correlation,
            "correlations": correlations,
            "num_assets": len(correlations)
        }
        
    except Exception as e:
        return {
            "avg_correlation": 0.0,
            "max_correlation": 0.0,
            "correlations": {},
            "error": str(e)
        }