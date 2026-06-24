"""Seed demo data for a local simulation run.

Idempotent and DEMO-ONLY: creates a demo admin user, a batch of live signals
(from synthetic data), a couple of open positions and several closed trades so
every dashboard page has something to show. Safe to run only in simulation/
paper mode; it refuses to run when live trading is armed.

    python -m app.scripts.seed_demo
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.broker.paper import SimulationBroker
from app.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.trade import Trade
from app.models.user import User
from app.schemas.trading import OrderRequest
from app.services.scanner_service import run_scan
from app.services.trading import execute_order

DEMO_EMAIL = "demo@playplate.in"
DEMO_PASSWORD = "demo-password-123"

_UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC",
    "LT", "AXISBANK", "TATAMOTORS", "MARUTI", "SUNPHARMA",
]
_CLOSED = [
    ("TCS", "BUY", 5, 3500, 3580, 380), ("SBIN", "SELL", 20, 620, 610, 180),
    ("ITC", "BUY", 30, 440, 435, -160), ("LT", "BUY", 4, 3600, 3720, 460),
    ("AXISBANK", "SELL", 15, 1080, 1095, -240), ("MARUTI", "BUY", 2, 12800, 13050, 480),
    ("SUNPHARMA", "BUY", 10, 1550, 1572, 210),
]


def main() -> int:
    if settings.live_trading_armed:
        print("Refusing to seed demo data while live trading is armed.", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        if db.execute(select(User).where(User.email == DEMO_EMAIL)).scalar_one_or_none():
            print(f"Demo already seeded (user {DEMO_EMAIL} exists). Nothing to do.")
            return 0

        db.add(User(
            email=DEMO_EMAIL, full_name="Demo Admin", role="admin",
            hashed_password=hash_password(DEMO_PASSWORD), is_active=True,
        ))
        db.commit()

        broker = SimulationBroker()
        res = run_scan(db, broker, symbols=_UNIVERSE, explain_top=3)
        print(f"Seeded {res['count']} signals.")

        for sym in ("RELIANCE", "INFY"):
            q = broker.get_quote(sym).last_price
            execute_order(db, broker, OrderRequest(
                symbol=sym, side="BUY", quantity=10,
                stop_loss=round(q * 0.98, 2), target=round(q * 1.04, 2),
            ))

        now = datetime.now(UTC)
        for i, (sym, side, qty, entry, ex, pnl) in enumerate(_CLOSED):
            db.add(Trade(
                symbol=sym, side=side, mode="paper", quantity=qty, entry_price=entry,
                exit_price=ex, pnl=pnl, status="closed",
                opened_at=now - timedelta(days=i + 1, hours=2),
                closed_at=now - timedelta(days=i + 1),
            ))
        db.commit()
        print(f"Seeded {len(_CLOSED)} closed trades and 2 open positions.")
        print(f"\nLogin: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
