"""Orchestrates a scan: fetch data -> scan -> rank -> explain -> persist."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai import explain, ranking
from app.broker.base import BrokerBase
from app.config import settings
from app.engine import market_hours
from app.engine.scanner import scan_universe
from app.logging_config import get_logger
from app.metrics import signals_generated_total
from app.models.signal import Signal

log = get_logger("services.scanner")

# A small default NSE liquid universe. Extend via the watchlist API or config.
DEFAULT_UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC",
    "LT", "AXISBANK", "KOTAKBANK", "HINDUNILVR", "BHARTIARTL", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "WIPRO", "ASIANPAINT", "BAJFINANCE", "TITAN", "ADANIENT",
]


def run_scan(
    db: Session,
    broker: BrokerBase,
    symbols: list[str] | None = None,
    timeframe: str = "15m",
    explain_top: int = 5,
    persist: bool = True,
) -> dict:
    symbols = symbols or DEFAULT_UNIVERSE
    data = {}
    for sym in symbols:
        try:
            df = broker.historical_ohlcv(sym, timeframe, days=30)
            if len(df) >= 30:
                data[sym] = df
        except Exception as exc:  # noqa: BLE001
            log.warning("data fetch failed for %s: %s", sym, exc)

    results = scan_universe(data, timeframe=timeframe)
    ranked = ranking.rank_signals(results)

    persisted: list[Signal] = []
    for rank, res, conf in ranked:
        if rank <= explain_top:
            res_explanation = explain.explain_signal(res)
        else:
            res_explanation = None
        signals_generated_total.labels(symbol=res.symbol, side=res.side).inc()
        if persist:
            sig = Signal(
                symbol=res.symbol, side=res.side, timeframe=res.timeframe,
                entry=res.entry, stop_loss=res.stop_loss, target=res.target,
                risk_reward=res.risk_reward, score=res.score, confidence=conf,
                rank=rank, indicators=res.indicators, explanation=res_explanation,
                status="active",
            )
            db.add(sig)
            persisted.append(sig)
    if persist:
        db.commit()

    summary = explain.market_summary([r for _, r, _ in ranked], market_hours.session_state())
    return {
        "session": market_hours.session_state(),
        "mode": settings.trading_mode.value,
        "count": len(ranked),
        "summary": summary,
        "signals": [
            {
                "rank": rank, "symbol": r.symbol, "side": r.side, "entry": r.entry,
                "stop_loss": r.stop_loss, "target": r.target, "risk_reward": r.risk_reward,
                "score": r.score, "confidence": conf, "reasons": r.reasons,
            }
            for rank, r, conf in ranked
        ],
    }
