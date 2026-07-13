"""Broker abstraction layer.

Defines a uniform interface so the trading engine never talks to a specific
broker SDK directly. Implementations:
  - PaperBroker / SimulationBroker  (no real orders)
  - ZerodhaBroker                   (live, gated behind multiple safety checks)
"""
from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class Quote:
    symbol: str
    last_price: float
    timestamp: datetime


@dataclass
class OrderAck:
    accepted: bool
    broker_order_id: str | None
    message: str
    avg_price: float | None = None


class BrokerError(Exception):
    pass


class BrokerBase(abc.ABC):
    """All brokers expose the same surface."""

    name: str = "base"
    is_live: bool = False

    # Exchange-qualified quote keys for major Indian indices.
    INDEX_MAP: dict[str, str] = {
        "NIFTY": "NSE:NIFTY 50",
        "BANKNIFTY": "NSE:NIFTY BANK",
        "SENSEX": "BSE:SENSEX",
        "FINNIFTY": "NSE:NIFTY FIN SERVICE",
    }

    @abc.abstractmethod
    def is_session_valid(self) -> bool: ...

    @abc.abstractmethod
    def get_quote(self, symbol: str) -> Quote: ...

    def get_index_quote(self, index: str) -> Quote:
        """Quote for a market index (NIFTY/SENSEX/...). Override per broker."""
        raise BrokerError(f"Index quotes not supported by broker '{self.name}'")

    @abc.abstractmethod
    def historical_ohlcv(
        self, symbol: str, interval: str, days: int
    ) -> pd.DataFrame:
        """Return OHLCV with columns timestamp,open,high,low,close,volume."""

    @abc.abstractmethod
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "MARKET",
        limit_price: float | None = None,
    ) -> OrderAck: ...

    @abc.abstractmethod
    def positions(self) -> list[dict]: ...
