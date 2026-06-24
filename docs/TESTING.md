# Testing Procedures & Checklist

## Automated tests

Backend unit tests cover indicators, backtest metrics, the scanner, risk/safety
gates, encryption, and the circuit breaker.

```bash
# In Docker:
make test
# Locally:
cd backend
pip install -r requirements.txt
TRADING_MODE=simulation JWT_SECRET_KEY=test DATABASE_URL=sqlite+pysqlite:///:memory: pytest -q
```

Lint:

```bash
cd backend && ruff check app tests
```

Frontend build (type/asset check):

```bash
cd frontend && npm install && npm run build
```

CI (`.github/workflows/ci.yml`) runs all of the above plus Docker image builds
on every push/PR.

## Manual smoke test (paper mode)

1. `make build && make up && make migrate`
2. Create admin user; log in to the dashboard.
3. **Signals:** click *Run scan* → signals appear with score/confidence/explanation.
4. **Trade:** submit a 1-qty order from a signal → confirm a paper fill message.
5. **Portfolio:** open position appears; PnL fields populate.
6. **Trades:** the trade is listed as `open`; *Close* it → status `closed`, PnL set.
7. **Performance:** metrics (win rate, Sharpe, drawdown) reflect closed trades.
8. **Health:** `curl -s localhost:8080/api/health/ready | jq` → `status: ok`.

## Safety verification (must pass before going live)

- [ ] Default `.env` keeps `TRADING_MODE=paper`, `ALLOW_LIVE_TRADING=false`.
- [ ] `Settings.live_trading_armed` is `False` unless BOTH live flags set
      (covered by `tests/test_risk_and_safety.py`).
- [ ] `ZerodhaBroker.place_order` raises when not armed (manual/inspection).
- [ ] Live order requires a confirmation token (try `POST /api/trades/order`
      in live mode without `confirm_token` → returns a token, no fill).
- [ ] Risk manager rejects orders exceeding exposure / position / size limits.
- [ ] Tripping the circuit breaker (`POST /api/admin/circuit-breaker/trip`)
      blocks new orders; reset restores trading.
- [ ] Daily-loss / drawdown breach trips the breaker automatically.
- [ ] Broker access token is stored **encrypted** (inspect `broker_sessions`).
- [ ] Audit log records logins, order fills/rejections, breaker actions.

## Risk-control test (simulation)

```bash
# Backtest a symbol to sanity-check the engine end-to-end:
curl -s -X POST "localhost:8080/api/backtest/run?symbol=RELIANCE&days=120" \
  -H "Authorization: Bearer <token>" | jq '.stats'
```

Confirm the response includes the standard disclaimer and metrics
(`win_rate`, `sharpe_ratio`, `max_drawdown_pct`, `profit_factor`).

## Deployment validation

```bash
bash deploy/healthcheck.sh
curl -I https://trading.playplate.in            # HTTP/2 200, HSTS header present
```

## Security checks

- [ ] No secrets committed (`.env` is gitignored; only `.env.example` tracked).
- [ ] JWT secret and encryption key are unique, 32-byte random values.
- [ ] Rate limiting active (hammer `/api/auth/login` → eventual `429`).
- [ ] TLS A-grade on SSL Labs; only TLS 1.2/1.3 enabled.
- [ ] Admin-only endpoints reject non-admin tokens (`403`).
- [ ] Run `pip-audit` / `npm audit` periodically for dependency CVEs.

## Performance / load (optional)

```bash
# Example with hey or k6 against a non-production environment:
hey -n 2000 -c 50 https://staging.trading.playplate.in/api/health/live
```

Watch Grafana for latency p95 and error rate during the run.
