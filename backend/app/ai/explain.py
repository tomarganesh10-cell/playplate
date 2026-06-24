"""Natural-language trade explanations and market summaries.

All AI output is framed as analysis, never as a guarantee or a directive to
trade. A standard risk caveat is appended to every explanation.
"""
from __future__ import annotations

from app.ai.client import get_ai
from app.engine.scanner import ScanResult

_SYSTEM = (
    "You are a careful trading analyst for the Indian NSE cash market. "
    "Explain technical setups objectively and concisely. "
    "Never promise profit, never give financial advice, and always note risk. "
    "Base your explanation ONLY on the indicator data provided."
)

_CAVEAT = (
    "⚠️ This is an automated technical analysis, not investment advice. "
    "Markets are uncertain; losses are possible. Trade only with risk capital."
)


def _fallback_explanation(r: ScanResult) -> str:
    reasons = "; ".join(r.reasons) if r.reasons else "composite technical score"
    return (
        f"{r.side} setup on {r.symbol} ({r.timeframe}). Drivers: {reasons}. "
        f"Entry ~{r.entry}, stop {r.stop_loss}, target {r.target} "
        f"(R:R {r.risk_reward}). {_CAVEAT}"
    )


def explain_signal(r: ScanResult) -> str:
    ai = get_ai()
    if not ai.enabled:
        return _fallback_explanation(r)
    prompt = (
        f"Symbol: {r.symbol}\nSide: {r.side}\nTimeframe: {r.timeframe}\n"
        f"Entry: {r.entry}\nStop: {r.stop_loss}\nTarget: {r.target}\n"
        f"Risk:Reward: {r.risk_reward}\nEngine score: {r.score}\n"
        f"Indicators: {r.indicators}\nRule reasons: {r.reasons}\n\n"
        "Write a 2-3 sentence plain-English explanation of this setup for a trader. "
        "State the key confirming factors and the main risk."
    )
    out = ai.complete(_SYSTEM, prompt, max_tokens=300)
    if not out:
        return _fallback_explanation(r)
    return f"{out}\n\n{_CAVEAT}"


def market_summary(top_signals: list[ScanResult], session_state: str) -> str:
    ai = get_ai()
    headline = (
        f"Market session: {session_state}. "
        f"{len(top_signals)} qualifying setups detected."
    )
    if not ai.enabled or not top_signals:
        names = ", ".join(f"{s.symbol}({s.side})" for s in top_signals[:5])
        return f"{headline} Top: {names}. {_CAVEAT}" if names else f"{headline} {_CAVEAT}"
    lines = "\n".join(
        f"- {s.symbol} {s.side} score={s.score} rr={s.risk_reward}" for s in top_signals[:10]
    )
    prompt = (
        f"{headline}\nTop setups:\n{lines}\n\n"
        "Write a concise 3-4 sentence market summary highlighting the dominant "
        "theme (breadth, momentum direction) without making predictions."
    )
    out = ai.complete(_SYSTEM, prompt, max_tokens=400)
    return f"{out}\n\n{_CAVEAT}" if out else f"{headline} {_CAVEAT}"
