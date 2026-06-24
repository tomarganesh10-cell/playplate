"""Technical indicators for the NSE cash segment.

All functions operate on a pandas DataFrame with columns:
    ['timestamp', 'open', 'high', 'low', 'close', 'volume']
sorted ascending by timestamp. They return pandas Series aligned to the input
index (or scalars where noted). No look-ahead bias is introduced.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50.0)


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "histogram": histogram}
    )


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    true_range = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def vwap(df: pd.DataFrame) -> pd.Series:
    """Session VWAP. Resets per calendar day to avoid cross-session leakage."""
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    tv = typical * df["volume"]
    day = pd.to_datetime(df["timestamp"]).dt.date
    cum_tv = tv.groupby(day).cumsum()
    cum_vol = df["volume"].groupby(day).cumsum().replace(0.0, np.nan)
    return (cum_tv / cum_vol).ffill()


def relative_volume(volume: pd.Series, lookback: int = 20) -> pd.Series:
    """Current volume vs its rolling average — a measure of unusual activity."""
    avg = volume.rolling(window=lookback, min_periods=1).mean()
    return (volume / avg.replace(0.0, np.nan)).fillna(0.0)


def volume_profile(df: pd.DataFrame, bins: int = 24) -> dict:
    """Compute a simple volume-by-price profile and the Point of Control (POC)."""
    if df.empty:
        return {"poc": None, "value_area_high": None, "value_area_low": None, "bins": []}
    prices = df["close"].to_numpy()
    volumes = df["volume"].to_numpy()
    lo, hi = float(prices.min()), float(prices.max())
    if hi <= lo:
        return {"poc": lo, "value_area_high": hi, "value_area_low": lo, "bins": []}
    edges = np.linspace(lo, hi, bins + 1)
    idx = np.clip(np.digitize(prices, edges) - 1, 0, bins - 1)
    vol_per_bin = np.zeros(bins)
    for i, v in zip(idx, volumes, strict=False):
        vol_per_bin[i] += v
    centers = (edges[:-1] + edges[1:]) / 2.0
    poc_i = int(vol_per_bin.argmax())

    # Value area = 70% of volume around the POC.
    total = vol_per_bin.sum()
    order = np.argsort(vol_per_bin)[::-1]
    acc, selected = 0.0, []
    for i in order:
        acc += vol_per_bin[i]
        selected.append(i)
        if acc >= 0.7 * total:
            break
    sel_prices = centers[selected]
    return {
        "poc": float(centers[poc_i]),
        "value_area_high": float(sel_prices.max()),
        "value_area_low": float(sel_prices.min()),
        "bins": [
            {"price": float(c), "volume": float(v)} for c, v in zip(centers, vol_per_bin, strict=False)
        ],
    }


def trend_state(df: pd.DataFrame) -> str:
    """Classify trend using EMA stack alignment. Returns up|down|sideways."""
    close = df["close"]
    e20, e50, e200 = ema(close, 20), ema(close, 50), ema(close, 200)
    last20, last50, last200 = e20.iloc[-1], e50.iloc[-1], e200.iloc[-1]
    if last20 > last50 > last200:
        return "up"
    if last20 < last50 < last200:
        return "down"
    return "sideways"


def compute_all(df: pd.DataFrame) -> dict:
    """Snapshot the latest value of every indicator for a signal record."""
    if len(df) < 30:
        raise ValueError("Need at least 30 candles to compute indicators reliably.")
    df = df.sort_values("timestamp").reset_index(drop=True)
    close = df["close"]
    macd_df = macd(close)
    vp = volume_profile(df)
    return {
        "last_price": float(close.iloc[-1]),
        "ema_20": float(ema(close, 20).iloc[-1]),
        "ema_50": float(ema(close, 50).iloc[-1]),
        "ema_200": float(ema(close, 200).iloc[-1]),
        "rsi_14": float(rsi(close).iloc[-1]),
        "macd": float(macd_df["macd"].iloc[-1]),
        "macd_signal": float(macd_df["signal"].iloc[-1]),
        "macd_hist": float(macd_df["histogram"].iloc[-1]),
        "atr_14": float(atr(df).iloc[-1]),
        "vwap": float(vwap(df).iloc[-1]),
        "rel_volume": float(relative_volume(df["volume"]).iloc[-1]),
        "volume_poc": vp["poc"],
        "value_area_high": vp["value_area_high"],
        "value_area_low": vp["value_area_low"],
        "trend": trend_state(df),
    }
