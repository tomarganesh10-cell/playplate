"""NSE market-hours awareness (Asia/Kolkata).

Regular session: 09:15–15:30 IST, Monday–Friday, excluding NSE holidays.
The holiday list should be refreshed yearly (see NSE trading-holiday circulars).
"""
from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)
PRE_OPEN_START = time(9, 0)

# Maintain per-year. Sourced from NSE trading holiday circular.
NSE_HOLIDAYS_2026: set[date] = {
    date(2026, 1, 26),   # Republic Day
    date(2026, 3, 4),    # Holi (illustrative)
    date(2026, 8, 15),   # Independence Day
    date(2026, 10, 2),   # Gandhi Jayanti
    date(2026, 12, 25),  # Christmas
}


def now_ist() -> datetime:
    return datetime.now(IST)


def is_trading_holiday(d: date) -> bool:
    return d.weekday() >= 5 or d in NSE_HOLIDAYS_2026


def is_market_open(at: datetime | None = None) -> bool:
    at = at.astimezone(IST) if at else now_ist()
    if is_trading_holiday(at.date()):
        return False
    return MARKET_OPEN <= at.time() <= MARKET_CLOSE


def is_pre_open(at: datetime | None = None) -> bool:
    at = at.astimezone(IST) if at else now_ist()
    if is_trading_holiday(at.date()):
        return False
    return PRE_OPEN_START <= at.time() < MARKET_OPEN


def session_state(at: datetime | None = None) -> str:
    """Returns one of: closed | pre_open | open."""
    if is_market_open(at):
        return "open"
    if is_pre_open(at):
        return "pre_open"
    return "closed"
