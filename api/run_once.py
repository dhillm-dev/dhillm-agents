from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from global_agents.core.fusion import run_analysis

app = FastAPI()

@app.post("/api/run_once")
@app.get("/api/run_once")  # Support both GET and POST for Vercel cron
def run_once(
    symbol: str = Query("EURUSD=X", description="Trading symbol to analyze"),
    tf: str = Query("1h", alias="timeframe", description="Timeframe for analysis")
):
    """Run analysis for a single symbol and timeframe."""
    try:
        result = run_analysis(symbol, tf)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "symbol": symbol,
            "timeframe": tf
        }, status_code=500)