# VPS Deployment Guide — Hostinger (Ubuntu 24.04)

End-to-end production deployment of Trading Playplate.

## ⚡ Fast path (one-shot bootstrap)

After provisioning Docker (step 1 below, run as root), the entire first-time
setup can be done with a single interactive command as the `playplate` user:

```bash
su - playplate
bash <(curl -fsSL https://raw.githubusercontent.com/tomarganesh10-cell/playplate/main/deploy/bootstrap.sh)
```

It clones the repo, generates the JWT/encryption secrets, prompts for your
Kite/Anthropic/Telegram keys, issues SSL (if DNS is ready), builds + migrates +
starts the stack in **paper mode**, and creates the admin user. Live trading is
left disabled — arm it explicitly later. The manual steps below explain each
stage if you prefer to run them individually.

## 0. Provision the VPS

In Hostinger, create/choose a VPS with **Ubuntu 24.04**. Note the public IPv4.
SSH in as root:

```bash
ssh root@<YOUR_VPS_IP>
```

## 1. Run the setup script

```bash
git clone <your-repo-url> /opt/playplate-bootstrap
bash /opt/playplate-bootstrap/deploy/setup_vps.sh
```

This installs Docker + Compose, configures the UFW firewall (SSH/80/443),
enables unattended security upgrades, and creates a non-root `playplate` user.

## 2. Deploy as the `playplate` user

```bash
su - playplate
git clone <your-repo-url> ~/playplate
cd ~/playplate
cp .env.example .env
```

Edit `.env` — set **all** `CHANGE_ME` values (the deploy script refuses to run
otherwise):

```bash
openssl rand -hex 32                                   # JWT_SECRET_KEY
python3 -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())"  # ENCRYPTION_KEY
# POSTGRES_PASSWORD, GRAFANA_ADMIN_PASSWORD, domain, broker/AI/telegram keys...
```

Keep `TRADING_MODE=paper` and `ALLOW_LIVE_TRADING=false` until you have
validated everything (see "Going live" below).

## 3. DNS + SSL

1. Configure DNS: [`DNS_CONFIGURATION.md`](DNS_CONFIGURATION.md).
2. Wait for propagation (`dig +short trading.playplate.in`).
3. Issue the certificate: [`SSL_CONFIGURATION.md`](SSL_CONFIGURATION.md):
   ```bash
   LETSENCRYPT_EMAIL=admin@playplate.in bash deploy/init_ssl.sh
   ```

## 4. Bring up the full stack

```bash
bash deploy/deploy.sh --with-monitoring
docker compose --profile ssl up -d certbot     # cert auto-renewal sidecar
```

The deploy script builds images, starts Postgres, applies Alembic migrations,
starts all services, and runs the health check.

## 5. Create the admin user

```bash
docker compose exec -e ADMIN_EMAIL=you@example.com -e ADMIN_PASSWORD='strong-pass' \
  backend python -m app.scripts.create_admin
```

## 6. Validate

```bash
bash deploy/healthcheck.sh
curl -s https://trading.playplate.in/api/health/ready | jq
```

Open <https://trading.playplate.in> and log in.

## 7. Continuous deployment (optional)

Add repo secrets `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (and `VPS_PORT`). The
`.github/workflows/deploy.yml` workflow then SSH-deploys on pushes to `main`:
it runs `git pull` + `deploy/deploy.sh` on the VPS.

## 8. Backups & monitoring

- Schedule DB backups (cron):
  ```cron
  0 2 * * * /home/playplate/playplate/deploy/backup_db.sh >> ~/backup.log 2>&1
  ```
- Monitoring stack: [`MONITORING.md`](MONITORING.md). Access Grafana via an SSH
  tunnel (it is not exposed publicly by default):
  ```bash
  ssh -L 3000:localhost:3000 playplate@<VPS_IP>
  # then open http://localhost:3000  (Grafana is on the internal network;
  # expose it through nginx only behind auth if you need remote access)
  ```

## Operations

- **Restart:** `make restart` or `docker compose restart`
- **Logs:** `make logs S=backend`
- **Update:** `git pull && bash deploy/deploy.sh --with-monitoring`
- **Rollback:** `git checkout <previous-tag> && bash deploy/deploy.sh`
- **Restore DB:** `gunzip -c backups/playplate_*.sql.gz | docker compose exec -T postgres psql -U playplate -d playplate`

## Going live (real orders) — checklist

> ⚠️ Read [`RISK_DISCLAIMER.md`](RISK_DISCLAIMER.md) first. No profit is guaranteed.

1. Run in paper mode for an extended period; review the Performance page and audit log.
2. Confirm risk limits in `.env` (`RISK_MAX_DAILY_LOSS`, `RISK_MAX_EXPOSURE`,
   `RISK_PER_TRADE_PCT`, `RISK_MAX_DRAWDOWN_PCT`, `ACCOUNT_CAPITAL`).
3. Ensure a valid Kite session exists (`/api/broker/status`).
4. Set `TRADING_MODE=live` and `ALLOW_LIVE_TRADING=true`; keep
   `REQUIRE_ORDER_CONFIRMATION=true`.
5. Redeploy. The backend logs a prominent **"LIVE TRADING IS ARMED"** warning.
6. Every live order still requires an explicit confirmation token returned by
   the first submit — there is no silent live execution.
