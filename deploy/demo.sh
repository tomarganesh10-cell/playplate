#!/usr/bin/env bash
# One-command LOCAL DEMO in simulation mode (no broker, no real orders).
# Brings up the stack, applies migrations, seeds demo data, and prints the URL.
#
#   make demo      (or)      bash deploy/demo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# Create a demo .env if one doesn't already exist (kept out of git).
if [ ! -f .env ]; then
  echo "==> Generating a demo .env (simulation mode)"
  cp .env.example .env
  JWT="$(openssl rand -hex 32)"
  FERNET="$(python3 -c 'from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())' 2>/dev/null || echo '')"
  python3 - "$JWT" "$FERNET" <<'PY'
import sys, re, pathlib
jwt, fernet = sys.argv[1], sys.argv[2]
vals = {
    "TRADING_MODE": "simulation", "ALLOW_LIVE_TRADING": "false",
    "JWT_SECRET_KEY": jwt or "demo-secret-change-me",
    "ENCRYPTION_KEY": fernet or "",
    "POSTGRES_PASSWORD": "demo_pg_password",
    "GRAFANA_ADMIN_PASSWORD": "demo_grafana_password",
    "AI_ENABLED": "false", "NOTIFICATIONS_ENABLED": "false",
}
p = pathlib.Path(".env"); t = p.read_text()
for k, v in vals.items():
    t = re.sub(rf"(?m)^{k}=.*$", f"{k}={v}", t) if re.search(rf"(?m)^{k}=", t) else t + f"\n{k}={v}\n"
p.write_text(t)
PY
fi

echo "==> Starting database + backend + frontend + nginx (simulation)"
docker compose up -d postgres
until docker compose exec -T postgres pg_isready >/dev/null 2>&1; do sleep 2; done
docker compose up -d backend frontend nginx

echo "==> Applying migrations"
docker compose exec -T backend alembic upgrade head

echo "==> Seeding demo data"
docker compose exec -T backend python -m app.scripts.seed_demo

cat <<EOF

============================================================
✅ Demo is up (SIMULATION mode — synthetic data, no real orders).

   URL:   http://localhost:8080
   Login: demo@playplate.in  /  demo-password-123

   Stop with:  docker compose down
   NOTE: numbers are synthetic and for illustration only.
         No profit is implied or guaranteed.
============================================================
EOF
