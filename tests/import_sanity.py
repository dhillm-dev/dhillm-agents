import importlib, pytest

MODULES = [
  "api.healthz",
  "api.last_decision",
  "api.run_once",
  "api.correl_scan",
  "global_agents.state",
  "global_agents.core.fusion",
  "global_agents.agents.ta_alpha",
  "global_agents.agents.regime",
  "global_agents.agents.corr_matrix",
]

@pytest.mark.parametrize("m", MODULES+["api.retrain_now"])
def test_imports(m):
    try:
        importlib.import_module(m)
    except ModuleNotFoundError:
        if m.endswith("retrain_now"):
            pytest.skip("optional endpoint")
        raise
    except Exception as e:
        raise AssertionError(f"Import failed: {m} -> {e}") from e
