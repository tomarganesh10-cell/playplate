"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.config import settings
from app.logging_config import configure_logging, get_logger
from app.middleware import MetricsMiddleware

configure_logging()
log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "Starting Trading Playplate v%s (mode=%s, live_armed=%s)",
        __version__, settings.trading_mode.value, settings.live_trading_armed,
    )
    if settings.live_trading_armed:
        log.warning("LIVE TRADING IS ARMED. Real orders may be routed to the broker.")
    yield
    log.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Trading Playplate API",
        version=__version__,
        description=(
            "AI-assisted NSE trading platform. SAFETY-FIRST: paper trading by "
            "default; no profit is guaranteed. See /docs for endpoints."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(MetricsMiddleware)
    app.include_router(api_router)

    @app.get("/")
    def root() -> dict:
        return {
            "name": "Trading Playplate",
            "version": __version__,
            "mode": settings.trading_mode.value,
            "docs": "/docs",
            "disclaimer": "No profit is guaranteed. Trading involves risk of loss.",
        }

    return app


app = create_app()
