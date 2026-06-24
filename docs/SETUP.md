# Local Setup Guide

This walks through running Trading Playplate on your machine in **paper mode**
(real data when a Kite session is present, simulated fills — no live orders).

## Prerequisites

- Docker + Docker Compose plugin
- (Optional) Python 3.12 and Node 20 if you want to run services outside Docker

## 1. Clone and configure

```bash
git clone <your-repo-url> playplate
cd playplate
cp .env.example .env
```

Edit `.env` and set, at minimum:

```bash
# Generate strong values:
openssl rand -hex 32                 # -> JWT_SECRET_KEY
python -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())"  # -> ENCRYPTION_KEY

POSTGRES_PASSWORD=<something-strong>
GRAFANA_ADMIN_PASSWORD=<something-strong>
```

`TRADING_MODE` defaults to `paper` and `ALLOW_LIVE_TRADING=false` — leave them
that way for local development. Broker, AI, and Telegram keys are optional; the
platform degrades gracefully without them (simulation data, fallback text, and
logged-only notifications).

## 2. Build and start

```bash
make build
make up
make migrate          # apply DB schema
```

## 3. Create the first admin user

```bash
docker compose exec -e ADMIN_EMAIL=you@example.com -e ADMIN_PASSWORD='your-strong-pass' \
  backend python -m app.scripts.create_admin
```

## 4. Open the app

- Dashboard: <http://localhost:8080>
- API docs (Swagger): <http://localhost:8080/api/docs> or <http://localhost:8000/docs>

Log in, click **Run scan** on the Signals page, and explore Portfolio / Trades /
Performance. In paper mode you can submit orders and they will be simulated.

## 5. (Optional) Connect Zerodha for real market data

Even in paper mode you can use *real* Kite data for scanning:

1. Set `KITE_API_KEY` and `KITE_API_SECRET` in `.env`, restart backend.
2. As admin: `GET /api/broker/login-url` → open the URL → log in to Kite.
3. Kite redirects back with `?request_token=...`.
4. `POST /api/broker/session { "request_token": "..." }` to store it (encrypted).

Tokens expire daily; repeat steps 2–4 each trading day (or automate via the
broker login flow on your registered redirect URL).

## 6. (Optional) Enable AI explanations

Set `ANTHROPIC_API_KEY` and keep `AI_ENABLED=true`. The default model is the
latest, most capable Claude model (`AI_MODEL=claude-opus-4-8`).

## 7. (Optional) Telegram alerts

Create a bot via @BotFather, get the token and your chat id, then set
`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## Running tests

```bash
make test         # inside the container
# or locally:
cd backend && pip install -r requirements.txt && pytest -q
```

## Common commands

```bash
make logs S=backend     # tail backend logs
make ps                 # service status
make db-shell           # psql
make down               # stop everything
```
