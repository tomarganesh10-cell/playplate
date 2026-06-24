"""Event-driven backtesting engine.

Walks an OHLCV series bar-by-bar, runs the same scanner used live, opens one
position at a time per symbol, and exits on stop/target/timeout. No look-ahead:
signals are computed only from data up to and including the current bar, and
fills occur at the *next* bar's open.

This is a simplified single-position model for transparency, not an exhaustive
portfolio simulator. Results are illustrative and NOT a profit guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.backtest.metrics import summarise_trades
from app.engine.scanner import scan_symbol


@dataclass
class BacktestConfig:
    timeframe: str = "15m"
    warmup: int = 200          # bars needed before first signal
    max_hold_bars: int = 32    # exit if neither stop nor target hit
    fee_bps: float = 3.0       # round-trip cost in basis points
    min_score: float = 60.0


@dataclass
class BacktestResult:
    symbol: str
    trades: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    equity_curve: list[float] = field(default_factory=list)


def run_backtest(symbol: str, df: pd.DataFrame, config: BacktestConfig | None = None) -> BacktestResult:
    config = config or BacktestConfig()
    df = df.sort_values("timestamp").reset_index(drop=True)
    n = len(df)
    trades: list[dict] = []
    equity = 0.0
    equity_curve: list[float] = []

    i = config.warmup
    while i < n - 1:
        window = df.iloc[: i + 1]
        sig = scan_symbol(symbol, window, timeframe=config.timeframe, min_score=config.min_score)
        if sig is None:
            i += 1
            continue

        # Enter at next bar open (no look-ahead).
        entry_idx = i + 1
        entry_price = float(df["open"].iloc[entry_idx])
        direction = 1 if sig.side == "BUY" else -1

        exit_price, exit_idx, reason = None, None, "timeout"
        for j in range(entry_idx, min(entry_idx + config.max_hold_bars, n)):
            hi, lo = float(df["high"].iloc[j]), float(df["low"].iloc[j])
            if direction == 1:
                if lo <= sig.stop_loss:
                    exit_price, exit_idx, reason = sig.stop_loss, j, "stop"
                    break
                if hi >= sig.target:
                    exit_price, exit_idx, reason = sig.target, j, "target"
                    break
            else:
                if hi >= sig.stop_loss:
                    exit_price, exit_idx, reason = sig.stop_loss, j, "stop"
                    break
                if lo <= sig.target:
                    exit_price, exit_idx, reason = sig.target, j, "target"
                    break
        if exit_price is None:
            exit_idx = min(entry_idx + config.max_hold_bars, n - 1)
            exit_price = float(df["close"].iloc[exit_idx])

        gross = (exit_price - entry_price) * direction
        fees = (entry_price + exit_price) * (config.fee_bps / 10_000.0)
        pnl = gross - fees
        equity += pnl
        equity_curve.append(equity)
        trades.append(
            {
                "symbol": symbol,
                "side": sig.side,
                "entry": round(entry_price, 2),
                "exit": round(exit_price, 2),
                "pnl": round(pnl, 2),
                "reason": reason,
                "entered_at": str(df["timestamp"].iloc[entry_idx]),
                "exited_at": str(df["timestamp"].iloc[exit_idx]),
            }
        )
        # Resume scanning after the trade closes (flat single-position model).
        i = exit_idx + 1

    stats = summarise_trades([t["pnl"] for t in trades])
    return BacktestResult(symbol=symbol, trades=trades, stats=stats, equity_curve=equity_curve)
