from fastapi import FastAPI

# Import sub-apps
from api.healthz import app as healthz_app
from api.run_once import app as run_once_app
from api.retrain_now import app as retrain_now_app
from api.correl_scan import app as correl_scan_app
from api.diagnostics import app as diagnostics_app
from api.learn_state import app as learn_state_app
from api.screener_stocks import app as screener_stocks_app
from api.screener_commodities import app as screener_comms_app
from api.portfolio_run import app as portfolio_run_app

# Import router for last decision
from api.last_decision import router as decision_router

app = FastAPI()

# Properly include routers from sub-apps
app.include_router(healthz_app.router)
app.include_router(decision_router)
app.include_router(run_once_app.router)
app.include_router(retrain_now_app.router)
app.include_router(correl_scan_app.router)
app.include_router(diagnostics_app.router)
app.include_router(learn_state_app.router)
app.include_router(screener_stocks_app.router)
app.include_router(screener_comms_app.router)
app.include_router(portfolio_run_app.router)