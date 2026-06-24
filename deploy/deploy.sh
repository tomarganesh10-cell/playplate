#!/usr/bin/env bash
# Build, migrate and (re)start the stack. Idempotent — safe to re-run.
# Usage: bash deploy/deploy.sh [--with-monitoring]
set -euo pipefail
cd "$(dirname "$0")/.."

WITH_MON=0
[ "${1:-}" = "--with-monitoring" ] && WITH_MON=1

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example to .env and fill in secrets." >&2
  exit 1
fi

# Refuse to deploy with placeholder secrets.
if grep -qE 'CHANGE_ME' .env; then
  echo "ERROR: .env still contains CHANGE_ME placeholders. Set real secrets first." >&2
  exit 1
fi

COMPOSE="docker compose"
[ "$WITH_MON" = "1" ] && COMPOSE="docker compose -f docker-compose.yml -f docker-compose.monitoring.yml"

echo "==> Pulling base images & building"
$COMPOSE build

echo "==> Starting database"
$COMPOSE up -d postgres
echo "==> Waiting for database health"
until docker compose exec -T postgres pg_isready >/dev/null 2>&1; do sleep 2; done

echo "==> Starting backend"
$COMPOSE up -d backend

echo "==> Applying migrations"
$COMPOSE exec -T backend alembic upgrade head

echo "==> Starting remaining services"
$COMPOSE up -d

echo "==> Deploy complete. Validating health…"
bash deploy/healthcheck.sh
