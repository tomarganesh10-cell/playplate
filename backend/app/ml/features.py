"""Feature engineering: turn an OHLCV frame into a model-ready matrix.

All features are causal (computed only from data up to each bar) and price-
scale-invariant so a model can generalise across symbols/index levels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.engine import indicators

FEATURE_NAMES = [
    "ret_1",          # 1-bar return
    "ret_5",          # 5-bar return
    "dist_ema20",     # price/EMA20 - 1
    "dist_ema50",     # price/EMA50 - 1
    "dist_ema200",    # price/EMA200 - 1
    "rsi",            # RSI/100
    "macd_hist_n",    # MACD histogram / price
    "atr_n",          # ATR / price
    "dist_vwap",      # price/VWAP - 1
    "rel_volume",     # volume vs 20-bar average (clipped)
]


def build_dataset(df: pd.DataFrame, horizon: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """Return (X, y): features per bar and label = 1 if forward return > 0.

    The last `horizon` rows are dropped (no label available) and warm-up rows
    with NaNs are dropped. Labels use close[t+horizon]/close[t]-1, which is
    only used for training — never leaked into features.
    """
    df = df.sort_values("timestamp").reset_index(drop=True)
    close = df["close"].astype(float)

    macd_df = indicators.macd(close)
    feat = pd.DataFrame({
        "ret_1": close.pct_change(1),
        "ret_5": close.pct_change(5),
        "dist_ema20": close / indicators.ema(close, 20) - 1,
        "dist_ema50": close / indicators.ema(close, 50) - 1,
        "dist_ema200": close / indicators.ema(close, 200) - 1,
        "rsi": indicators.rsi(close) / 100.0,
        "macd_hist_n": macd_df["histogram"] / close,
        "atr_n": indicators.atr(df) / close,
        "dist_vwap": close / indicators.vwap(df) - 1,
        "rel_volume": indicators.relative_volume(df["volume"]).clip(0, 5),
    })

    fwd_ret = close.shift(-horizon) / close - 1
    label = (fwd_ret > 0).astype(float)

    mask = feat.notna().all(axis=1) & fwd_ret.notna()
    X = feat.loc[mask, FEATURE_NAMES].to_numpy(dtype=float)
    y = label.loc[mask].to_numpy(dtype=float)
    return X, y


def latest_features(df: pd.DataFrame) -> np.ndarray:
    """Feature vector for the most recent bar (for prediction)."""
    df = df.sort_values("timestamp").reset_index(drop=True)
    close = df["close"].astype(float)
    macd_df = indicators.macd(close)
    row = [
        float(close.pct_change(1).iloc[-1]),
        float(close.pct_change(5).iloc[-1]),
        float(close.iloc[-1] / indicators.ema(close, 20).iloc[-1] - 1),
        float(close.iloc[-1] / indicators.ema(close, 50).iloc[-1] - 1),
        float(close.iloc[-1] / indicators.ema(close, 200).iloc[-1] - 1),
        float(indicators.rsi(close).iloc[-1] / 100.0),
        float(macd_df["histogram"].iloc[-1] / close.iloc[-1]),
        float(indicators.atr(df).iloc[-1] / close.iloc[-1]),
        float(close.iloc[-1] / indicators.vwap(df).iloc[-1] - 1),
        float(min(max(indicators.relative_volume(df["volume"]).iloc[-1], 0.0), 5.0)),
    ]
    return np.asarray(row, dtype=float)
