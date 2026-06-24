#!/usr/bin/env bash
# One-shot first-time bootstrap for Trading Playplate on a fresh VPS.
#
# Run as the (non-root) `playplate` user AFTER deploy/setup_vps.sh has installed
# Docker. It will:
#   1. clone/update the repo,
#   2. generate JWT + encryption secrets and prompt for the few keys it needs,
#   3. (optionally) issue the Let's Encrypt certificate,
#   4. build + migrate + start the full stack (paper mode — SAFE by default),
#   5. create the first admin user.
#
# Live (real-money) trading is intentionally NOT enabled here. Validate in
# paper mode first, then arm it explicitly (see the end of this script's output
# and docs/VPS_DEPLOYMENT.md).
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/tomarganesh10-cell/playplate}"
APP_DIR="${APP_DIR:-$HOME/playplate}"
DOMAIN="${DOMAIN:-trading.playplate.in}"

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
ask()  { local p="$1" d="${2:-}"; local v; read -rp "$p${d:+ [$d]}: " v; echo "${v:-$d}"; }
asks() { local p="$1"; local v; read -rsp "$p: " v; echo >&2; echo "$v"; }

command -v docker >/dev/null || { echo "Docker not found. Run deploy/setup_vps.sh as root first." >&2; exit 1; }

bold "==> 1/5  Fetching code"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --all --prune && git -C "$APP_DIR" reset --hard origin/main
else
  git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

bold "==> 2/5  Configuring .env"
if [ -f .env ]; then
  echo ".env already exists — leaving it untouched. Edit manually if needed."
else
  cp .env.example .env
  JWT="$(openssl rand -hex 32)"
  FERNET="$(python3 -c 'from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())')"
  echo "Enter the values below (input for secrets is hidden):"
  PG_PASS="$(asks 'PostgreSQL password (choose a strong one)')"
  GRAF_PASS="$(asks 'Grafana admin password')"
  KITE_KEY="$(ask  'Zerodha Kite API key')"
  KITE_SECRET="$(asks 'Zerodha Kite API secret')"
  ANTHROPIC="$(asks 'Anthropic API key (blank to skip AI)')"
  TG_TOKEN="$(asks 'Telegram bot token (blank to skip)')"
  TG_CHAT="$(ask  'Telegram chat id (blank to skip)')"
  CAPITAL="$(ask  'Account capital (INR) for risk sizing' '200000')"

  python3 - "$JWT" "$FERNET" "$PG_PASS" "$GRAF_PASS" "$KITE_KEY" "$KITE_SECRET" \
             "$ANTHROPIC" "$TG_TOKEN" "$TG_CHAT" "$CAPITAL" <<'PY'
import sys, re, pathlib
jwt, fernet, pg, graf, kkey, ksec, anth, tgt, tgc, cap = sys.argv[1:11]
vals = {
    "JWT_SECRET_KEY": jwt, "ENCRYPTION_KEY": fernet, "POSTGRES_PASSWORD": pg,
    "GRAFANA_ADMIN_PASSWORD": graf, "KITE_API_KEY": kkey, "KITE_API_SECRET": ksec,
    "ANTHROPIC_API_KEY": anth, "TELEGRAM_BOT_TOKEN": tgt, "TELEGRAM_CHAT_ID": tgc,
    "ACCOUNT_CAPITAL": cap,
    # Stay SAFE: paper trading, live routing disabled.
    "TRADING_MODE": "paper", "ALLOW_LIVE_TRADING": "false",
    "REQUIRE_ORDER_CONFIRMATION": "true",
}
p = pathlib.Path(".env"); text = p.read_text()
for k, v in vals.items():
    if re.search(rf"(?m)^{k}=", text):
        text = re.sub(rf"(?m)^{k}=.*$", f"{k}={v}", text)
    else:
        text += f"\n{k}={v}\n"
p.write_text(text)
print("  .env written (paper mode, live disabled).")
PY
fi

bold "==> 3/5  SSL certificate"
if [ -d "certbot/conf/live/$DOMAIN" ]; then
  echo "Certificate already present — skipping issuance."
else
  ans="$(ask "Is DNS A-record for $DOMAIN pointing to this VPS and propagated? (y/N)" "N")"
  if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
    EMAIL="$(ask 'Email for Let'\''s Encrypt' 'hopecommonersfoundation@gmail.com')"
    LETSENCRYPT_EMAIL="$EMAIL" bash deploy/init_ssl.sh
  else
    echo "Skipping SSL. After DNS propagates, run: bash deploy/init_ssl.sh"
  fi
fi

bold "==> 4/5  Building and starting the stack (paper mode)"
bash deploy/deploy.sh --with-monitoring

bold "==> 5/5  Admin user"
if [ "$(ask 'Create the first admin user now? (Y/n)' 'Y')" != "n" ]; then
  AE="$(ask 'Admin email')"
  AP="$(asks 'Admin password (>=10 chars)')"
  docker compose exec -T -e ADMIN_EMAIL="$AE" -e ADMIN_PASSWORD="$AP" \
    backend python -m app.scripts.create_admin
fi

cat <<EOF

============================================================
✅ Bootstrap complete — running in PAPER mode (no real orders).

Next:
  1. Open https://$DOMAIN and log in.
  2. Connect Zerodha: GET /api/broker/login-url -> Kite login ->
     POST /api/broker/session {"request_token":"..."}  (repeat daily).
  3. Validate signals / paper trades for at least one session.

To enable CI auto-deploy: add VPS_HOST, VPS_USER, VPS_SSH_KEY GitHub secrets.

🔴 To go LIVE (real money) later, edit .env:
     TRADING_MODE=live
     ALLOW_LIVE_TRADING=true
   then: bash deploy/deploy.sh --with-monitoring
   (every live order still requires a confirmation token.)
   Risk warning: real-money trading can lose capital. No profit is guaranteed.
============================================================
EOF
