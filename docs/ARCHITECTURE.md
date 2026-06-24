# Architecture

## Overview

Trading Playplate is a containerised, single-VPS deployment composed of a React
SPA, a FastAPI backend, a background worker, PostgreSQL, and an optional
Prometheus/Grafana monitoring stack — all behind an Nginx TLS reverse proxy.

```
Browser ──HTTPS──> Nginx ──/──────> frontend (React static, served by nginx)
                        └──/api───> backend (FastAPI / uvicorn)
                                        ├── engine     (indicators, scanner, MTF, market hours)
                                        ├── risk        (sizing, limits, circuit breaker)
                                        ├── ai          (ranking, confidence, NL explain, reports)
                                        ├── broker      (zerodha | paper | simulation, sessions)
                                        ├── services    (order execution chokepoint, scanner orchestration)
                                        └── notifications (Telegram)
                                                │
worker (periodic scan + reports) ───────────────┤
                                                ▼
                                          PostgreSQL  (users, signals, trades, positions, audit, broker_sessions)
Prometheus ──scrape /api/metrics──> backend
Grafana ──query──> Prometheus
```

## Components

| Component   | Tech                  | Responsibility |
|-------------|-----------------------|----------------|
| `frontend`  | React + Vite, Recharts | Dashboard SPA: auth, signals, portfolio, trades, performance |
| `backend`   | FastAPI, SQLAlchemy 2 | REST API, auth, business logic |
| `worker`    | Python loop           | Periodic scanning + daily/weekly reports (never auto-trades) |
| `postgres`  | PostgreSQL 16         | Durable storage + audit trail |
| `nginx`     | Nginx                 | TLS termination, reverse proxy, edge rate limiting |
| `prometheus`| Prometheus            | Metrics scraping + alert rules |
| `grafana`   | Grafana               | Dashboards |
| `certbot`   | Certbot               | Let's Encrypt issuance + renewal |

## Backend module map

- `app/config.py` — validated settings; the `live_trading_armed` gate.
- `app/engine/indicators.py` — VWAP, EMA 20/50/200, RSI, MACD, ATR, volume
  profile, relative volume, trend classification.
- `app/engine/scanner.py` — transparent rules-based scoring → `ScanResult`.
- `app/engine/multi_timeframe.py` — resampling + higher-timeframe trend alignment.
- `app/engine/market_hours.py` — NSE session awareness (Asia/Kolkata).
- `app/risk/manager.py` + `circuit_breaker.py` — pre-trade validation & kill-switch.
- `app/broker/` — `base` interface, `zerodha`, `paper`, `simulation`, `session`.
- `app/ai/` — `ranking` (deterministic confidence), `explain`/`reports` (Claude).
- `app/services/trading.py` — the **single** path every order flows through.
- `app/api/` — routers for auth, signals, trades, portfolio, performance,
  broker, backtest, admin, health.

## Key design decisions

1. **Safety gates are in config, not UI.** Live routing requires two env flags
   plus a per-order token; the broker layer itself refuses unarmed live orders.
2. **Quantitative path is deterministic and auditable.** The AI model only
   writes natural-language explanations/summaries; it never fabricates the
   numeric scores, sizes, or probabilities used for decisions.
3. **Single order chokepoint.** `services.trading.execute_order` enforces risk,
   safety, persistence, audit, and notification in one place.
4. **Broker abstraction.** The engine never imports a broker SDK directly, so
   paper/sim/live are interchangeable.
5. **Append-only audit log** for every security- and trade-relevant action.

## Data flow: generating and acting on a signal

1. `worker` (or `POST /api/signals/scan`) fetches OHLCV via the active broker.
2. `scanner.scan_universe` computes indicators and scores each symbol.
3. `ai.ranking.rank_signals` derives deterministic confidence and ordering.
4. Top signals get a Claude NL explanation; all are persisted to `signals`.
5. A user reviews signals in the UI and may submit an order.
6. `services.trading.execute_order` runs risk checks → safety gate → broker →
   persists `trades`/`positions`, writes an audit log, sends a Telegram alert.
