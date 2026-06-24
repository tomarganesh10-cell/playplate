import numpy as np
import pandas as pd

from app.engine import indicators


def _make_df(n=300, seed=7):
    rng = np.random.default_rng(seed)
    ts = pd.date_range("2026-01-01 09:15", periods=n, freq="15min")
    price = 100 + np.cumsum(rng.normal(0, 1, n))
    close = pd.Series(price).clip(lower=1)
    high = close * 1.005
    low = close * 0.995
    vol = rng.integers(50_000, 200_000, n)
    return pd.DataFrame(
        {"timestamp": ts, "open": close.shift(1).fillna(close), "high": high,
         "low": low, "close": close, "volume": vol}
    )


def test_ema_length_and_monotonic_window():
    df = _make_df()
    e = indicators.ema(df["close"], 20)
    assert len(e) == len(df)
    assert not e.isna().all()


def test_rsi_bounds():
    df = _make_df()
    r = indicators.rsi(df["close"])
    assert (r.dropna() >= 0).all() and (r.dropna() <= 100).all()


def test_macd_columns():
    df = _make_df()
    m = indicators.macd(df["close"])
    assert set(m.columns) == {"macd", "signal", "histogram"}


def test_atr_positive():
    df = _make_df()
    a = indicators.atr(df).dropna()
    assert (a >= 0).all()


def test_vwap_within_price_range():
    df = _make_df()
    v = indicators.vwap(df).dropna()
    assert v.min() >= df["low"].min() * 0.5
    assert v.max() <= df["high"].max() * 1.5


def test_compute_all_keys():
    df = _make_df()
    snap = indicators.compute_all(df)
    for key in ("ema_20", "ema_50", "ema_200", "rsi_14", "macd", "atr_14", "vwap", "trend"):
        assert key in snap
    assert snap["trend"] in ("up", "down", "sideways")


def test_compute_all_needs_min_candles():
    df = _make_df(n=10)
    try:
        indicators.compute_all(df)
        assert False, "expected ValueError"
    except ValueError:
        pass
