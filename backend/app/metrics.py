"""Prometheus metrics registry and helpers."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

http_requests_total = Counter(
    "playplate_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
http_request_latency = Histogram(
    "playplate_http_request_latency_seconds",
    "HTTP request latency",
    ["method", "path"],
)
signals_generated_total = Counter(
    "playplate_signals_generated_total",
    "Trading signals generated",
    ["symbol", "side"],
)
orders_total = Counter(
    "playplate_orders_total",
    "Orders placed",
    ["mode", "side", "status"],
)
open_positions = Gauge(
    "playplate_open_positions",
    "Current number of open positions",
)
daily_pnl = Gauge(
    "playplate_daily_pnl_inr",
    "Realised + unrealised PnL for the trading day (INR)",
)
circuit_breaker_tripped = Gauge(
    "playplate_circuit_breaker_tripped",
    "1 if the trading circuit breaker is currently tripped, else 0",
)
broker_session_valid = Gauge(
    "playplate_broker_session_valid",
    "1 if the broker session/token is currently valid, else 0",
)
