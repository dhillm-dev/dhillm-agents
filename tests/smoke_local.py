from fastapi.testclient import TestClient
import pandas as pd, numpy as np

from api.healthz import app as health_app
from api.last_decision import app as last_app
from api.run_once import app as run_app
from api.correl_scan import app as corr_app


def test_healthz():
    c = TestClient(health_app)
    r = c.get("/api/healthz")
    assert r.status_code==200 and r.json().get("ok") is True


def test_last_decision_roundtrip():
    c = TestClient(last_app)
    w = c.post("/api/last_decision", json={"decision":{"symbol":"TEST","action":"HOLD"}})
    assert w.status_code==200
    r = c.get("/api/last_decision")
    assert r.status_code==200 and r.json()["last_decision"]["symbol"]=="TEST"


def test_run_once_mock(monkeypatch):
    import api.run_once as ro
    def fake_download(symbol, period="60d", interval="1h", auto_adjust=True):
        idx = pd.date_range("2025-01-01", periods=120, freq="H")
        df = pd.DataFrame({
            "Open": 100, "High": 101, "Low": 99, "Close": np.linspace(100,110,120), "Volume": 1000
        }, index=idx)
        return df
    ro.yf.download = fake_download
    c = TestClient(run_app)
    r = c.post("/api/run_once", json={"symbol":"EURUSD=X"})
    assert r.status_code==200 and r.json().get("ok") is True


def test_correl_scan_mock(monkeypatch):
    import api.correl_scan as cs
    def fake_fetch_close(tickers, period="60d", interval="1h"):
        idx = pd.date_range("2025-01-01", periods=60, freq="H")
        return pd.DataFrame({t: np.linspace(100+i,110+i,60) for i,t in enumerate(tickers)}, index=idx)
    cs.fetch_close = fake_fetch_close
    c = TestClient(corr_app)
    r = c.get("/api/correl_scan")
    assert r.status_code==200 and r.json().get("ok") is True
