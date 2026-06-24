"""Performance metrics: win rate, profit factor, Sharpe, drawdown."""
from __future__ import annotations

import math

import numpy as np


def sharpe_ratio(returns: list[float], periods_per_year: int = 252, risk_free: float = 0.0) -> float:
    """Annualised Sharpe from a series of per-trade/per-period returns."""
    if len(returns) < 2:
        return 0.0
    arr = np.asarray(returns, dtype=float)
    excess = arr - (risk_free / periods_per_year)
    std = excess.std(ddof=1)
    if std == 0:
        return 0.0
    return float((excess.mean() / std) * math.sqrt(periods_per_year))


def max_drawdown(equity_curve: list[float]) -> float:
    """Maximum peak-to-trough drawdown as a positive percentage."""
    if not equity_curve:
        return 0.0
    arr = np.asarray(equity_curve, dtype=float)
    running_max = np.maximum.accumulate(arr)
    # Avoid divide-by-zero when equity starts at 0.
    safe = np.where(running_max == 0, np.nan, running_max)
    drawdowns = (arr - running_max) / safe
    dd = np.nanmin(drawdowns)
    return float(abs(dd) * 100.0) if not math.isnan(dd) else 0.0


def summarise_trades(pnls: list[float], starting_equity: float = 0.0) -> dict:
    if not pnls:
        return {
            "total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0,
            "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0,
            "sharpe_ratio": 0.0, "max_drawdown_pct": 0.0,
        }
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    equity, curve = starting_equity, []
    for p in pnls:
        equity += p
        curve.append(equity)
    return {
        "total_trades": len(pnls),
        "win_rate": len(wins) / len(pnls),
        "total_pnl": sum(pnls),
        "avg_win": (gross_win / len(wins)) if wins else 0.0,
        "avg_loss": (-gross_loss / len(losses)) if losses else 0.0,
        "profit_factor": (gross_win / gross_loss) if gross_loss else float("inf") if gross_win else 0.0,
        "sharpe_ratio": sharpe_ratio(pnls),
        "max_drawdown_pct": max_drawdown(curve),
    }
