# Global Agents - Serverless FastAPI on Vercel

Serverless FastAPI on Vercel with multi-agent trading analysis.

## Endpoints

- `GET /api/healthz` - Health check
- `GET /api/last_decision` - Get last trading decision
- `POST /api/last_decision` - Update last trading decision
- `POST /api/run_once` - Compute analysis for one symbol now
- `GET /api/correl_scan` - Multi-asset rolling correlations
- `GET /api/diagnostics` - Raw agent outputs + fused result (debug)

## Usage

MT5 EA polls `/api/last_decision` for trading signals.

The system runs automated analysis every 15 minutes via Vercel cron jobs.

## Agents

- **TA Agent**: RSI + MACD technical analysis
- **Regime Agent**: ATR% volatility regime detection
- **Correlation Agent**: Multi-asset correlation analysis (FX, Crypto, Indices, Metals)
- **Momentum Agent**: EMA cross + MACD + RSI blend
- **VWAP Reversion**: Distance from rolling VWAP, z-scored reversion
- **Flow Agent**: OHLC wick bias proxy for order flow
- **Seasonality Agent**: Time-of-week bias by weekday/hour
- **Liquidity Forecast**: Volatility-driven liquidity pressure
- **Macro Agent**: Placeholder macro score (to be expanded)
- **ML Signal**: Placeholder model combining key features

## Fusion Brain v2

Adaptive fusion with confidence mapping, regime dampening, and optional correlation penalty.

- Confidence: `conf = |score|` mapped to [0,1]
- Regime dampening: volatile regimes scale weights by 0.7
- Correlation penalty: subtract `corr_penalty` when integrating multi-asset signals
- Historical weight: `hist_weight` can reduce contribution when < 1

Response shape from `/api/run_once`:

`{"ok":true,"decision":{"action":"BUY/SELL/HOLD","symbol":"...","score":...,"details":{...},"regime":{...},"sl":...,"tp":...,"size":...}}`

## Vision & Phases

- Phase 1: Add VWAP Reversion, Momentum, Flow, Seasonality, Liquidity Forecast, ML placeholder; fuse with v2.
- Phase 2: Wire correlation penalty from `/api/correl_scan`; add exposure caps & position ledger; log decisions.
- Phase 3: Add Sentiment/News and Macro data; replace ML placeholder with lightweight offline-trained model.
- Phase 4: Adaptive weights using rolling PnL per agent; promote/demote agents automatically.
- Phase 5: Full portfolio optimizer (risk parity across uncorrelated signals).

## Deployment

Deploy to Vercel with Python 3.11 runtime. Redis is optional for persistent state storage.