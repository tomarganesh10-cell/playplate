"""Multi-timeframe analysis helpers.

Aggregates a base-timeframe OHLCV frame into higher timeframes and confirms
that lower- and higher-timeframe trends agree before a signal is emitted.
"""
from __future__ import annotations

import pandas as pd

from app.engine import indicators

# pandas resample rule per timeframe label
_RESAMPLE_RULE = {
    "1m": "1min",
    "3m": "3min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "60min",
    "1d": "1D",
}


def resample(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    rule = _RESAMPLE_RULE[timeframe]
    s = df.copy()
    s["timestamp"] = pd.to_datetime(s["timestamp"])
    s = s.set_index("timestamp")
    agg = s.resample(rule, label="right", closed="right").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    return agg.dropna().reset_index()


def trend_alignment(base_df: pd.DataFrame, timeframes: list[str]) -> dict:
    """Return per-timeframe trend plus an `aligned` flag and direction."""
    trends: dict[str, str] = {}
    for tf in timeframes:
        tf_df = resample(base_df, tf)
        if len(tf_df) < 30:
            trends[tf] = "unknown"
            continue
        trends[tf] = indicators.trend_state(tf_df)
    valid = [t for t in trends.values() if t in ("up", "down")]
    aligned = len(valid) > 0 and len(set(valid)) == 1
    return {
        "trends": trends,
        "aligned": aligned,
        "direction": valid[0] if aligned else "mixed",
    }
