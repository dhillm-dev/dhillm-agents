def size(balance: float, risk_pct: float, stop_pips: float, pip_value: float = 1.0) -> float:
    risk_amt = max(0.0, balance * risk_pct)
    vol = max(0.01, min(2.0, risk_amt / max(1e-9, stop_pips * pip_value)))
    return round(vol, 2)


def sl_tp(price: float, direction: str, stop_pips: float, take_mult: float = 1.5, pip: float = 0.0001):
    if direction == "BUY":
        sl = price - stop_pips * pip
        tp = price + take_mult * stop_pips * pip
    else:
        sl = price + stop_pips * pip
        tp = price - take_mult * stop_pips * pip
    return round(sl, 5), round(tp, 5)


def exposure_cap(active_positions: int, max_pos: int = 4) -> float:
    return 1.0 if active_positions < max_pos else 0.0
