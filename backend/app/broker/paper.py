"""Paper-trading and simulation brokers.

PaperBroker: uses *real* market data (delegated to a data source) but simulates
fills at the quoted price plus configurable slippage. No orders ever reach a
real exchange.

SimulationBroker: fully synthetic — generates random-walk data and instant
fills. Useful for demos and CI where no broker session exists.
"""
from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import pandas as pd

from app.broker.base import BrokerBase, OrderAck, Quote
from app.logging_config import get_logger

log = get_logger("broker.paper")


def _synthetic_ohlcv(symbol: str, interval: str, days: int) -> pd.DataFrame:
    rng = random.Random(hash(symbol) & 0xFFFFFFFF)
    periods = max(days * 25, 250)
    price = 100 + rng.random() * 900
    rows = []
    ts = datetime.now(UTC) - timedelta(minutes=15 * periods)
    for _ in range(periods):
        drift = (rng.random() - 0.5) * price * 0.01
        o = price
        c = max(price + drift, 1.0)
        h = max(o, c) * (1 + rng.random() * 0.004)
        low = min(o, c) * (1 - rng.random() * 0.004)
        v = int(50_000 + rng.random() * 200_000)
        rows.append((ts, o, h, low, c, v))
        price = c
        ts += timedelta(minutes=15)
    return pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])


class SimulationBroker(BrokerBase):
    name = "simulation"
    is_live = False

    def is_session_valid(self) -> bool:
        return True

    def get_quote(self, symbol: str) -> Quote:
        df = _synthetic_ohlcv(symbol, "15m", 1)
        return Quote(symbol, float(df["close"].iloc[-1]), datetime.now(UTC))

    def historical_ohlcv(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        return _synthetic_ohlcv(symbol, interval, days)

    def get_index_quote(self, index: str) -> Quote:
        # Synthetic index level, clearly not a real market value.
        q = self.get_quote(f"IDX-{index.upper()}")
        return Quote(index.upper(), q.last_price * 25, q.timestamp)

    def place_order(self, symbol, side, quantity, order_type="MARKET", limit_price=None) -> OrderAck:
        price = limit_price or self.get_quote(symbol).last_price
        oid = f"SIM-{int(datetime.now().timestamp())}-{random.randint(1000, 9999)}"
        log.info("Simulated fill %s %s x%s @ %.2f", side, symbol, quantity, price)
        return OrderAck(True, oid, "simulated fill", avg_price=round(price, 2))

    def positions(self) -> list[dict]:
        return []


class PaperBroker(SimulationBroker):
    """Paper trading: real data source injected, simulated fills w/ slippage."""

    name = "paper"

    def __init__(self, data_source: BrokerBase | None = None, slippage_bps: float = 2.0):
        self._data = data_source
        self._slippage = slippage_bps / 10_000.0

    def is_session_valid(self) -> bool:
        return self._data.is_session_valid() if self._data else True

    def get_quote(self, symbol: str) -> Quote:
        if self._data:
            return self._data.get_quote(symbol)
        return super().get_quote(symbol)

    def historical_ohlcv(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        if self._data:
            return self._data.historical_ohlcv(symbol, interval, days)
        return super().historical_ohlcv(symbol, interval, days)

    def get_index_quote(self, index: str) -> Quote:
        if self._data:
            return self._data.get_index_quote(index)
        return super().get_index_quote(index)

    def place_order(self, symbol, side, quantity, order_type="MARKET", limit_price=None) -> OrderAck:
        base = limit_price or self.get_quote(symbol).last_price
        # Slippage works against the trader.
        fill = base * (1 + self._slippage) if side == "BUY" else base * (1 - self._slippage)
        oid = f"PAPER-{int(datetime.now().timestamp())}-{random.randint(1000, 9999)}"
        log.info("Paper fill %s %s x%s @ %.2f (base %.2f)", side, symbol, quantity, fill, base)
        return OrderAck(True, oid, "paper fill", avg_price=round(fill, 2))
