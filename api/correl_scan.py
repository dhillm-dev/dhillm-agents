from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from global_agents.agents.corr_matrix import compute, ASSET_UNIVERSE

app = FastAPI()

@app.get("/api/correl_scan")
def correl_scan(
    symbol: str = Query("EURUSD=X", description="Target symbol for correlation analysis"),
    category: str = Query("all", description="Asset category: fx, crypto, indices, metals, or all")
):
    """Get multi-asset rolling correlations for the specified symbol."""
    try:
        # Run correlation analysis
        result = compute(symbol)
        
        # Add asset universe info
        result["asset_universe"] = ASSET_UNIVERSE
        result["target_symbol"] = symbol
        result["category_filter"] = category
        
        # Filter by category if specified
        if category != "all" and category in ASSET_UNIVERSE:
            filtered_correlations = {}
            category_symbols = ASSET_UNIVERSE[category]
            for sym, corr in result.get("correlations", {}).items():
                if sym in category_symbols:
                    filtered_correlations[sym] = corr
            result["filtered_correlations"] = filtered_correlations
        
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "symbol": symbol,
            "category": category
        }, status_code=500)