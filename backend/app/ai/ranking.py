"""Signal ranking and confidence scoring.

Confidence is a deterministic, explainable transform of the engine score and
corroborating factors. The AI model (Claude) is used for *natural-language*
explanation and qualitative summaries — NOT to fabricate probabilities. This
keeps the quantitative path auditable and reproducible.
"""
from __future__ import annotations

from app.engine.scanner import ScanResult


def confidence_score(result: ScanResult) -> float:
    """Map raw 0..100 engine score + R:R + volume into a 0..1 confidence."""
    base = result.score / 100.0

    # Reward favourable risk:reward up to a cap.
    rr_factor = min(result.risk_reward / 3.0, 1.0) * 0.15

    # Reward unusual volume participation.
    rel_vol = float(result.indicators.get("rel_volume", 1.0))
    vol_factor = min(max(rel_vol - 1.0, 0.0) / 2.0, 1.0) * 0.10

    # Penalise stretched RSI.
    rsi = float(result.indicators.get("rsi_14", 50.0))
    rsi_penalty = 0.10 if (rsi > 78 or rsi < 22) else 0.0

    conf = base * 0.75 + rr_factor + vol_factor - rsi_penalty
    return round(min(max(conf, 0.0), 1.0), 3)


def rank_signals(results: list[ScanResult]) -> list[tuple[int, ScanResult, float]]:
    """Return [(rank, result, confidence)] sorted by a blended score desc."""
    scored = [(r, confidence_score(r)) for r in results]
    scored.sort(key=lambda x: (x[1], x[0].score), reverse=True)
    return [(i + 1, r, c) for i, (r, c) in enumerate(scored)]
