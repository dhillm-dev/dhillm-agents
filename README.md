# Global Agents - Serverless FastAPI on Vercel

Serverless FastAPI on Vercel with multi-agent trading analysis.

## Endpoints

- `GET /api/healthz` - Health check
- `GET /api/last_decision` - Get last trading decision
- `POST /api/last_decision` - Update last trading decision
- `POST /api/run_once` - Compute analysis for one symbol now
- `GET /api/correl_scan` - Multi-asset rolling correlations

## Usage

MT5 EA polls `/api/last_decision` for trading signals.

The system runs automated analysis every 15 minutes via Vercel cron jobs.

## Agents

- **TA Agent**: RSI + MACD technical analysis
- **Regime Agent**: ATR% volatility regime detection
- **Correlation Agent**: Multi-asset correlation analysis (FX, Crypto, Indices, Metals)

## Deployment

Deploy to Vercel with Python 3.11 runtime. Redis is optional for persistent state storage.