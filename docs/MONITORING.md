# Monitoring & Observability

## Stack

- **Prometheus** scrapes backend metrics at `/api/metrics` and node metrics.
- **Grafana** visualises them (provisioned datasource + dashboard).
- **Alert rules** live in `infra/prometheus/alerts.yml`.
- **node-exporter** exposes host CPU/memory/disk metrics.

Start with monitoring:

```bash
make monitoring          # or: bash deploy/deploy.sh --with-monitoring
```

## Application metrics

Exposed via `prometheus_client` (see `backend/app/metrics.py`):

| Metric | Type | Meaning |
|--------|------|---------|
| `playplate_http_requests_total{method,path,status}` | counter | HTTP requests |
| `playplate_http_request_latency_seconds` | histogram | request latency |
| `playplate_signals_generated_total{symbol,side}` | counter | signals produced |
| `playplate_orders_total{mode,side,status}` | counter | orders placed/rejected |
| `playplate_open_positions` | gauge | current open positions |
| `playplate_daily_pnl_inr` | gauge | day PnL (realised + unrealised) |
| `playplate_circuit_breaker_tripped` | gauge | 1 if breaker tripped |
| `playplate_broker_session_valid` | gauge | 1 if Kite session valid |

## Health endpoints

- `GET /api/health/live` — process liveness (Docker healthcheck).
- `GET /api/health/ready` — DB reachable, mode, market session, breaker state.

## Grafana

- Default login: `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from `.env`.
- Dashboard **"Trading Playplate Overview"** is auto-provisioned
  (`infra/grafana/dashboards/trading.json`): PnL, positions, breaker, broker
  session, request rate/latency, signal & order rates.
- Grafana is **not** exposed publicly by default. Reach it via SSH tunnel:
  ```bash
  ssh -L 3000:grafana:3000 playplate@<VPS_IP>   # if grafana port published internally
  ```
  or add a protected nginx location if you need remote access.

## Alerting

`alerts.yml` defines: `BackendDown`, `CircuitBreakerTripped`,
`BrokerSessionInvalid`, `DailyLossBreached`, `HighErrorRate`.

To route alerts to Slack/email/Telegram, add **Alertmanager** and a receiver
config, then point Prometheus at it (`alerting.alertmanagers` in
`prometheus.yml`). Application-level trade alerts already go to Telegram via the
notifications module.

## Logs

All services log structured JSON to stdout (collected by Docker). Tail with:

```bash
make logs S=backend
docker compose logs -f --tail=200
```

For long-term log retention, ship stdout to Loki, the ELK stack, or your
provider's logging service.
