import os, math
from typing import Dict
import statistics as S

from .weights_store import save_weights, load_weights
from global_agents.agents import perf_tracker

# Hyperparams (env overrides)
ALPHA = float(os.getenv("EMA_ALPHA", "0.2"))        # EMA smoothing for win_rate/Sharpe (placeholder for future EMA)
CLIP_MIN = float(os.getenv("W_MIN", "0.25"))        # lower bound pre-softmax
CLIP_MAX = float(os.getenv("W_MAX", "3.0"))         # upper bound pre-softmax
HIST_WINDOW = int(os.getenv("HIST_WINDOW", "400"))   # perf window
TAU = float(os.getenv("SOFTMAX_TAU", "0.75"))       # softmax temperature


def _z(v: float, mean: float, std: float) -> float:
    return 0.0 if std == 0 else (v - mean) / std


def retrain() -> Dict:
    stats = perf_tracker.get_stats(window=HIST_WINDOW)
    if not stats:
        # cold start → equal weights
        eq = {
            "ta": 1, "momentum": 1, "reversion": 1, "flow": 1, "seasonality": 1,
            "macro": 1, "liquidity": 1, "ml": 1
        }
        # normalize to simplex
        n = len(eq)
        eq_norm = {k: 1.0 / n for k in eq}
        save_weights(eq_norm)
        return {"weights": eq_norm, "mode": "equal"}

    wr = [v["win_rate"] for v in stats.values()]
    sh = [max(-1.0, min(1.0, v["sharpe"] / 5.0)) for v in stats.values()]  # compress Sharpe
    m_wr, s_wr = (S.mean(wr), S.pstdev(wr) or 1e-9)
    m_sh, s_sh = (S.mean(sh), S.pstdev(sh) or 1e-9)

    raw = {}
    for ag, v in stats.items():
        wr_z = _z(v["win_rate"], m_wr, s_wr)
        sh_z = _z(max(-1.0, min(1.0, v["sharpe"] / 5.0)), m_sh, s_sh)
        score = 0.7 * wr_z + 0.3 * sh_z
        raw[ag] = max(CLIP_MIN, min(CLIP_MAX, 1.0 + score))  # center at 1.0

    exps = {ag: math.exp(w / TAU) for ag, w in raw.items()}
    Z = sum(exps.values()) or 1.0
    w_norm = {ag: exps[ag] / Z for ag in exps}

    # EMA smooth with previous weights (if any), then re-normalize
    prev = load_weights() or {}
    keys = set(list(w_norm.keys()) + list(prev.keys()))
    # fallback equal for unseen keys
    eq = 1.0 / max(1, len(keys))
    smoothed = {k: ALPHA * w_norm.get(k, eq) + (1.0 - ALPHA) * prev.get(k, eq) for k in keys}
    total = sum(smoothed.values()) or 1.0
    smoothed_norm = {k: v / total for k, v in smoothed.items()}

    save_weights(smoothed_norm)
    return {"weights": smoothed_norm, "mode": "learned"}
