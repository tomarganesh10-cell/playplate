"""Live scanner: turns OHLCV data into scored, structured trade signals.

The scoring is a transparent, rules-based composite of momentum, trend,
volume and mean-reversion factors. It is intentionally explainable — every
contribution is recorded so the AI layer and the UI can justify a signal.

This is NOT a profit guarantee. Scores are relative rankings, not forecasts.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.engine import indicators
from app.engine.multi_timeframe import trend_alignment


@dataclass
class ScanResult:
    symbol: str
    side: str
    entry: float
    stop_loss: float
    target: float
    risk_reward: float
    score: float
    timeframe: str
    indicators: dict
    reasons: list[str] = field(default_factory=list)


def _score_long(ind: dict, mtf: dict) -> tuple[float, list[str]]:
    score, reasons = 0.0, []
    price = ind["last_price"]

    if ind["trend"] == "up":
        score += 25
        reasons.append("EMA stack bullish (20>50>200)")
    if price > ind["vwap"]:
        score += 15
        reasons.append("Price above session VWAP")
    if 45 <= ind["rsi_14"] <= 68:
        score += 15
        reasons.append(f"RSI constructive ({ind['rsi_14']:.0f})")
    elif ind["rsi_14"] > 75:
        score -= 10
        reasons.append("RSI overbought — reduced score")
    if ind["macd_hist"] > 0:
        score += 15
        reasons.append("MACD histogram positive")
    if ind["rel_volume"] >= 1.5:
        score += 20
        reasons.append(f"Relative volume {ind['rel_volume']:.1f}x")
    if mtf["aligned"] and mtf["direction"] == "up":
        score += 10
        reasons.append("Higher-timeframe trend aligned (up)")
    return min(score, 100.0), reasons


def _score_short(ind: dict, mtf: dict) -> tuple[float, list[str]]:
    score, reasons = 0.0, []
    price = ind["last_price"]

    if ind["trend"] == "down":
        score += 25
        reasons.append("EMA stack bearish (20<50<200)")
    if price < ind["vwap"]:
        score += 15
        reasons.append("Price below session VWAP")
    if 32 <= ind["rsi_14"] <= 55:
        score += 15
        reasons.append(f"RSI weak ({ind['rsi_14']:.0f})")
    elif ind["rsi_14"] < 25:
        score -= 10
        reasons.append("RSI oversold — reduced score")
    if ind["macd_hist"] < 0:
        score += 15
        reasons.append("MACD histogram negative")
    if ind["rel_volume"] >= 1.5:
        score += 20
        reasons.append(f"Relative volume {ind['rel_volume']:.1f}x")
    if mtf["aligned"] and mtf["direction"] == "down":
        score += 10
        reasons.append("Higher-timeframe trend aligned (down)")
    return min(score, 100.0), reasons


def scan_symbol(
    symbol: str,
    df: pd.DataFrame,
    timeframe: str = "15m",
    higher_timeframes: list[str] | None = None,
    atr_stop_mult: float = 1.5,
    rr_target: float = 2.0,
    min_score: float = 55.0,
) -> ScanResult | None:
    """Evaluate one symbol. Returns a ScanResult only if score >= min_score."""
    higher_timeframes = higher_timeframes or ["1h"]
    ind = indicators.compute_all(df)
    mtf = trend_alignment(df, higher_timeframes)

    long_score, long_reasons = _score_long(ind, mtf)
    short_score, short_reasons = _score_short(ind, mtf)

    if long_score >= short_score:
        side, score, reasons = "BUY", long_score, long_reasons
    else:
        side, score, reasons = "SELL", short_score, short_reasons

    if score < min_score:
        return None

    price = ind["last_price"]
    atr = max(ind["atr_14"], price * 0.001)  # floor to avoid zero-width stops
    if side == "BUY":
        stop = price - atr_stop_mult * atr
        target = price + atr_stop_mult * atr * rr_target
    else:
        stop = price + atr_stop_mult * atr
        target = price - atr_stop_mult * atr * rr_target

    risk = abs(price - stop)
    reward = abs(target - price)
    rr = round(reward / risk, 2) if risk else 0.0

    return ScanResult(
        symbol=symbol,
        side=side,
        entry=round(price, 2),
        stop_loss=round(stop, 2),
        target=round(target, 2),
        risk_reward=rr,
        score=round(score, 2),
        timeframe=timeframe,
        indicators=ind,
        reasons=reasons,
    )


def scan_universe(
    data: dict[str, pd.DataFrame], **kwargs
) -> list[ScanResult]:
    """Scan a dict of {symbol: ohlcv_df}; return results sorted by score desc."""
    results: list[ScanResult] = []
    for symbol, df in data.items():
        try:
            res = scan_symbol(symbol, df, **kwargs)
        except ValueError:
            continue  # insufficient data
        if res:
            results.append(res)
    results.sort(key=lambda r: r.score, reverse=True)
    return results
