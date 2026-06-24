from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SignalOut(BaseModel):
    id: int
    symbol: str
    side: str
    timeframe: str
    entry: float
    stop_loss: float
    target: float
    risk_reward: float
    score: float
    confidence: float
    rank: int | None
    indicators: dict
    explanation: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderRequest(BaseModel):
    symbol: str
    side: str = Field(pattern="^(BUY|SELL)$")
    quantity: int = Field(gt=0)
    order_type: str = Field(default="MARKET", pattern="^(MARKET|LIMIT)$")
    limit_price: float | None = None
    stop_loss: float | None = None
    target: float | None = None
    signal_id: int | None = None
    # Required for live mode (see config.require_order_confirmation).
    confirm_token: str | None = Field(
        default=None,
        description="Explicit per-order confirmation required for live trading.",
    )


class OrderResult(BaseModel):
    accepted: bool
    mode: str
    broker_order_id: str | None = None
    message: str
    trade_id: int | None = None


class TradeOut(BaseModel):
    id: int
    symbol: str
    side: str
    mode: str
    quantity: int
    entry_price: float
    exit_price: float | None
    pnl: float
    fees: float
    status: str
    opened_at: datetime
    closed_at: datetime | None

    model_config = {"from_attributes": True}


class PositionOut(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    last_price: float
    unrealised_pnl: float

    model_config = {"from_attributes": True}


class PortfolioOut(BaseModel):
    capital: float
    cash: float
    invested: float
    open_positions: list[PositionOut]
    realised_pnl_today: float
    unrealised_pnl: float
    exposure: float


class PerformanceOut(BaseModel):
    total_trades: int
    win_rate: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown_pct: float
    period_start: datetime | None
    period_end: datetime | None
