"""Zerodha session / token lifecycle.

Kite access tokens expire daily. The login flow:
  1. Redirect the user to the Kite login URL (frontend).
  2. Kite redirects back with a `request_token`.
  3. We exchange request_token + api_secret -> access_token (once/day).
  4. Store the access_token encrypted in the broker_sessions table.

This module also provides a factory that returns the correct broker for the
configured TRADING_MODE.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.broker.base import BrokerBase, BrokerError
from app.broker.paper import PaperBroker, SimulationBroker
from app.config import TradingMode, settings
from app.core.encryption import get_cipher
from app.logging_config import get_logger
from app.metrics import broker_session_valid
from app.models.broker_session import BrokerSession

log = get_logger("broker.session")


def exchange_request_token(request_token: str) -> dict:
    """Exchange a Kite request_token for an access_token and persist nothing yet."""
    try:
        from kiteconnect import KiteConnect
    except ImportError as exc:  # pragma: no cover
        raise BrokerError("kiteconnect not installed") from exc
    kite = KiteConnect(api_key=settings.kite_api_key)
    data = kite.generate_session(request_token, api_secret=settings.kite_api_secret)
    return {"access_token": data["access_token"], "user_id": data.get("user_id")}


def store_session(db: Session, access_token: str, user_id: str | None) -> BrokerSession:
    cipher = get_cipher()
    # Invalidate any prior sessions.
    for prior in db.execute(select(BrokerSession).where(BrokerSession.is_valid.is_(True))).scalars():
        prior.is_valid = False
    sess = BrokerSession(
        broker="zerodha",
        api_key=settings.kite_api_key,
        encrypted_access_token=cipher.encrypt(access_token),
        user_id=user_id,
        is_valid=True,
        issued_at=datetime.now(UTC),
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    broker_session_valid.set(1)
    log.info("Stored encrypted Kite session for user_id=%s", user_id)
    return sess


def load_access_token(db: Session) -> str | None:
    sess = db.execute(
        select(BrokerSession).where(BrokerSession.is_valid.is_(True)).order_by(BrokerSession.id.desc())
    ).scalars().first()
    if not sess:
        broker_session_valid.set(0)
        return None
    return get_cipher().decrypt(sess.encrypted_access_token)


def get_broker(db: Session, instrument_map: dict[str, int] | None = None) -> BrokerBase:
    """Factory: return the broker appropriate for the configured mode.

    - simulation -> SimulationBroker (synthetic data)
    - paper      -> PaperBroker backed by live Zerodha data when a session exists
    - live       -> ZerodhaBroker (only if live_trading_armed)
    """
    mode = settings.trading_mode

    if mode == TradingMode.SIMULATION:
        return SimulationBroker()

    access_token = load_access_token(db)

    if mode == TradingMode.LIVE:
        if not settings.live_trading_armed:
            raise BrokerError("Live mode requested but not armed; refusing to build live broker.")
        if not access_token:
            raise BrokerError("No valid Kite session. Complete the broker login flow first.")
        from app.broker.zerodha import ZerodhaBroker

        return ZerodhaBroker(settings.kite_api_key, access_token, instrument_map)

    # paper (default)
    data_source: BrokerBase | None = None
    if access_token:
        try:
            from app.broker.zerodha import ZerodhaBroker

            data_source = ZerodhaBroker(settings.kite_api_key, access_token, instrument_map)
        except BrokerError:
            data_source = None
    return PaperBroker(data_source=data_source)
