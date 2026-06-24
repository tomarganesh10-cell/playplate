"""Top-level API router aggregating all route modules."""
from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    backtest,
    broker,
    health,
    performance,
    portfolio,
    signals,
    trades,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(broker.router, prefix="/broker", tags=["broker"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
