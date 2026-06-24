"""NSE instrument-token resolution for Zerodha Kite.

Kite's historical-data API is keyed by numeric `instrument_token`, not by the
human trading symbol. This module downloads Kite's instrument dump once per
trading day and builds a {tradingsymbol -> instrument_token} map for the NSE
cash (EQ) segment, cached in memory.
"""
from __future__ import annotations

import threading
from datetime import date

from app.logging_config import get_logger

log = get_logger("broker.instruments")

_lock = threading.Lock()
_cache: dict[str, int] = {}
_cache_day: date | None = None


def load_nse_equity_tokens(kite, force: bool = False) -> dict[str, int]:
    """Return {tradingsymbol: instrument_token} for NSE equities.

    `kite` is a connected KiteConnect instance. The result is cached for the
    current day; pass force=True to refresh.
    """
    global _cache, _cache_day
    today = date.today()
    with _lock:
        if not force and _cache and _cache_day == today:
            return _cache
        try:
            instruments = kite.instruments("NSE")
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to download NSE instruments: %s", exc)
            return _cache  # fall back to whatever we had (possibly empty)

        mapping: dict[str, int] = {}
        for inst in instruments:
            # Keep only cash-segment equities (exclude indices, etc.).
            if inst.get("segment") == "NSE" and inst.get("instrument_type") == "EQ":
                mapping[inst["tradingsymbol"]] = int(inst["instrument_token"])
        if mapping:
            _cache = mapping
            _cache_day = today
            log.info("Loaded %d NSE equity instrument tokens", len(mapping))
        return _cache
