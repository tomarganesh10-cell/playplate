"""Zerodha Kite Connect live broker adapter.

SAFETY: `place_order` raises unless `settings.live_trading_armed` is True (i.e.
TRADING_MODE=live AND ALLOW_LIVE_TRADING=true). The session/token is loaded
from the encrypted BrokerSession row, never from plaintext env in production.

Kite docs: https://kite.trade/docs/connect/v3/
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from app.broker.base import BrokerBase, BrokerError, OrderAck, Quote
from app.config import settings
from app.logging_config import get_logger

log = get_logger("broker.zerodha")

# Map our interval labels to Kite's.
_KITE_INTERVAL = {
    "1m": "minute",
    "3m": "3minute",
    "5m": "5minute",
    "15m": "15minute",
    "30m": "30minute",
    "1h": "60minute",
    "1d": "day",
}


class ZerodhaBroker(BrokerBase):
    name = "zerodha"
    is_live = True

    def __init__(self, api_key: str, access_token: str, instrument_map: dict[str, int] | None = None):
        try:
            from kiteconnect import KiteConnect  # imported lazily
        except ImportError as exc:  # pragma: no cover
            raise BrokerError("kiteconnect is not installed") from exc
        self._kite = KiteConnect(api_key=api_key)
        self._kite.set_access_token(access_token)
        # symbol -> instrument_token, required for historical/quote calls.
        self._instruments = instrument_map or {}

    # ---- session ---------------------------------------------------------
    def is_session_valid(self) -> bool:
        try:
            self._kite.profile()
            return True
        except Exception as exc:  # noqa: BLE001
            log.warning("Kite session invalid: %s", exc)
            return False

    # Kite instrument tokens for major indices (stable, documented values).
    INDEX_TOKENS = {
        "NIFTY": 256265,       # NSE:NIFTY 50
        "BANKNIFTY": 260105,   # NSE:NIFTY BANK
        "SENSEX": 265,         # BSE:SENSEX
        "FINNIFTY": 257801,    # NSE:NIFTY FIN SERVICE
    }

    def _token(self, symbol: str) -> int:
        if symbol in self.INDEX_TOKENS:
            return self.INDEX_TOKENS[symbol]
        if symbol not in self._instruments:
            # Lazily download Kite's NSE instrument dump and cache it.
            from app.broker.instruments import load_nse_equity_tokens

            self._instruments = load_nse_equity_tokens(self._kite) or self._instruments
        if symbol not in self._instruments:
            raise BrokerError(f"No instrument token mapped for {symbol}")
        return self._instruments[symbol]

    # ---- data ------------------------------------------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8))
    def get_quote(self, symbol: str) -> Quote:
        key = f"NSE:{symbol}"
        data = self._kite.quote([key])[key]
        return Quote(symbol, float(data["last_price"]), datetime.now(UTC))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8))
    def get_index_quote(self, index: str) -> Quote:
        key = self.INDEX_MAP.get(index.upper())
        if not key:
            raise BrokerError(f"Unknown index '{index}'")
        data = self._kite.quote([key])[key]
        return Quote(index.upper(), float(data["last_price"]), datetime.now(UTC))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8))
    def historical_ohlcv(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        kite_interval = _KITE_INTERVAL[interval]
        to_dt = datetime.now()
        from_dt = to_dt - timedelta(days=days)
        candles = self._kite.historical_data(
            self._token(symbol), from_dt, to_dt, kite_interval
        )
        df = pd.DataFrame(candles)
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
        df = df.rename(columns={"date": "timestamp"})
        return df[["timestamp", "open", "high", "low", "close", "volume"]]

    # ---- orders ----------------------------------------------------------
    def place_order(self, symbol, side, quantity, order_type="MARKET", limit_price=None) -> OrderAck:
        if not settings.live_trading_armed:
            raise BrokerError(
                "Live trading is NOT armed. Refusing to route a real order. "
                "Set TRADING_MODE=live and ALLOW_LIVE_TRADING=true to enable."
            )
        try:
            order_id = self._kite.place_order(
                variety=self._kite.VARIETY_REGULAR,
                exchange=self._kite.EXCHANGE_NSE,
                tradingsymbol=symbol,
                transaction_type=(
                    self._kite.TRANSACTION_TYPE_BUY if side == "BUY"
                    else self._kite.TRANSACTION_TYPE_SELL
                ),
                quantity=quantity,
                product=self._kite.PRODUCT_MIS,
                order_type=(
                    self._kite.ORDER_TYPE_LIMIT if order_type == "LIMIT"
                    else self._kite.ORDER_TYPE_MARKET
                ),
                price=limit_price,
            )
            log.info("LIVE order placed id=%s %s %s x%s", order_id, side, symbol, quantity)
            return OrderAck(True, str(order_id), "live order accepted")
        except Exception as exc:  # noqa: BLE001
            log.error("Live order failed: %s", exc)
            return OrderAck(False, None, f"order rejected: {exc}")

    def positions(self) -> list[dict]:
        try:
            return self._kite.positions().get("net", [])
        except Exception as exc:  # noqa: BLE001
            log.warning("positions() failed: %s", exc)
            return []
