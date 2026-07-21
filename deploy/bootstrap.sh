#!/usr/bin/env bash
# One-shot first-time bootstrap for Trading Playplate on a fresh VPS.
#
# Run as a user in the `docker` group AFTER deploy/setup_vps.sh has installed
# Docker. It will:
#   1. clone/update the repo,
#   2. generate JWT + encryption secrets and prompt for the few keys it needs,
#   3. build + migrate + start the full stack (paper mode — SAFE by default),
#      -> the site is immediately reachable over HTTP on the VPS IP,
#   4. create the first admin user,
#   5. optionally issue an HTTPS certificate (only once DNS is ready).
#
# Live (real-money) trading is intentionally NOT enabled here.
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
  echo "Enter the values below (input for secrets is hidden). Press Enter to skip optional ones."
  PG_PASS="$(asks 'PostgreSQL password (choose a strong one)')"
  GRAF_PASS="$(asks 'Grafana admin password')"
  KITE_KEY="$(ask  'Zerodha Kite API key (blank to add later)')"
  KITE_SECRET="$(asks 'Zerodha Kite API secret (blank to add later)')"
  ANTHROPIC="$(asks 'Anthropic API key (blank to skip AI)')"
  TG_TOKEN="$(asks 'Telegram bot token (blank to skip)')"
  TG_CHAT="$(ask  'Telegram chat id (blank to skip)')"
  CAPITAL="$(ask  'Account capital (INR) for risk sizing' '200000')"

  python3 - "$JWT" "$FERNET" "$PG_PASS" "$GRAF_PASS" "$KITE_KEY" "$KITE_SECRET" \
             "$ANTHROPIC" "$TG_TOKEN" "$TG_CHAT" "$CAPITAL" <<'PY'
import sys, re, pathlib
jwt, fernet, pg, graf, kkey, ksec, anth, tgt, tgc, cap = sys.argv[1:11]
vals = {
    "JWT_SECRET_KEY": jwt, "ENCRYPTION_KEY": fernet, "POSTGRES_PASSWORD": pg or "playplate_pg",
    "GRAFANA_ADMIN_PASSWORD": graf or "playplate_grafana", "KITE_API_KEY": kkey,
    "KITE_API_SECRET": ksec, "ANTHROPIC_API_KEY": anth, "TELEGRAM_BOT_TOKEN": tgt,
    "TELEGRAM_CHAT_ID": tgc, "ACCOUNT_CAPITAL": cap or "200000",
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

bold "==> 3/5  Building and starting the stack (paper mode, HTTP)"
bash deploy/deploy.sh --with-monitoring

bold "==> 4/5  Admin user"
if [ "$(ask 'Create the first admin user now? (Y/n)' 'Y')" != "n" ]; then
  AE="$(ask 'Admin email')"
  AP="$(asks 'Admin password (>=10 chars)')"
  docker compose exec -T -e ADMIN_EMAIL="$AE" -e ADMIN_PASSWORD="$AP" \
    backend python -m app.scripts.create_admin
fi

bold "==> 5/5  HTTPS (optional)"
if [ -d "certbot/conf/live/$DOMAIN" ]; then
  echo "Certificate already present — skipping."
else
  ans="$(ask "Is DNS A-record for $DOMAIN pointing to this VPS and propagated? (y/N)" "N")"
  if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
    EMAIL="$(ask 'Email for Let'\''s Encrypt' 'hopecommonersfoundation@gmail.com')"
    LETSENCRYPT_EMAIL="$EMAIL" bash deploy/init_ssl.sh
  else
    echo "Skipping HTTPS. Set DNS later, then run: bash deploy/init_ssl.sh"
  fi
fi

IP="$(curl -fsS -4 ifconfig.me 2>/dev/null || echo YOUR_VPS_IP)"
cat <<EOF

============================================================
✅ Bootstrap complete — PAPER mode (no real orders).

   Open now:   http://${IP}
   (After HTTPS + DNS:  https://${DOMAIN})

   Log in with the admin you just created.
   Connect Zerodha from the Broker page (or add KITE_API_KEY/SECRET to
   .env and re-run: bash deploy/deploy.sh).

🔴 Real-money LIVE later: set TRADING_MODE=live and ALLOW_LIVE_TRADING=true
   in .env, then: bash deploy/deploy.sh --with-monitoring
   Risk: real-money trading can lose capital. No profit is guaranteed.
============================================================
EOF
