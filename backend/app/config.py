"""Centralised, validated application settings.

All configuration is sourced from environment variables (see `.env.example`).
Defaults are chosen to be *safe*: paper trading, live routing disabled.
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TradingMode(str, Enum):
    SIMULATION = "simulation"
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # General
    environment: str = "production"
    domain: str = "trading.playplate.in"
    log_level: str = "INFO"

    # Trading safety
    trading_mode: TradingMode = TradingMode.PAPER
    allow_live_trading: bool = False
    require_order_confirmation: bool = True

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "https://trading.playplate.in,http://localhost:8080"

    # Security
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    encryption_key: str = ""
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    # Database
    postgres_user: str = "playplate"
    postgres_password: str = "playplate"
    postgres_db: str = "playplate"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str | None = None

    # Zerodha
    kite_api_key: str = ""
    kite_api_secret: str = ""
    kite_access_token: str = ""

    # AI
    anthropic_api_key: str = ""
    ai_model: str = "claude-opus-4-8"
    ai_enabled: bool = True

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    notifications_enabled: bool = True

    # Risk
    risk_max_daily_loss: float = 5000.0
    risk_max_open_positions: int = 5
    risk_max_exposure: float = 200000.0
    risk_per_trade_pct: float = 1.0
    risk_max_drawdown_pct: float = 10.0
    account_capital: float = 200000.0

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def live_trading_armed(self) -> bool:
        """True only when *all* safety gates permit live order routing."""
        return self.trading_mode == TradingMode.LIVE and self.allow_live_trading


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
