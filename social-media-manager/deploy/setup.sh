#!/bin/bash
# ============================================================
# Playplate AI Social Media Manager — Full VPS Deploy Script
# Tested on: Ubuntu 22.04 LTS (Hostinger VPS)
#
# Usage (as root on your VPS):
#   git clone https://github.com/tomarganesh10-cell/playplate.git /opt/playplate-smm
#   cd /opt/playplate-smm/social-media-manager
#   chmod +x deploy/setup.sh
#   ./deploy/setup.sh
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

DOMAIN="social.playplate.in"
APP_DIR="/opt/playplate-smm/social-media-manager"
ADMIN_EMAIL="admin@playplate.in"
REPO="https://github.com/tomarganesh10-cell/playplate.git"
BRANCH="claude/new-session-8kmsp6"

banner() {
  echo -e "${CYAN}${BOLD}"
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║    🦷 Playplate AI Social Media Manager — Deploy        ║"
  echo "║       Dr. Anshu Gupta · social.playplate.in             ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

step() { echo -e "\n${BLUE}${BOLD}[$1/$TOTAL_STEPS] $2${NC}"; }
ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "  ${RED}❌ $1${NC}"; exit 1; }

TOTAL_STEPS=12
banner

# ── Root check ────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && err "Run this script as root: sudo bash deploy/setup.sh"

# ── 1. System Update ──────────────────────────────────────────
step 1 "Updating system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    curl wget git unzip htop nano \
    ca-certificates gnupg lsb-release \
    ufw fail2ban \
    openssl
ok "System packages updated"

# ── 2. Install Docker ─────────────────────────────────────────
step 2 "Installing Docker & Docker Compose"
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    ok "Docker installed: $(docker --version)"
else
    ok "Docker already installed: $(docker --version)"
fi

# Docker Compose v2 (plugin)
if ! docker compose version &>/dev/null 2>&1; then
    apt-get install -y -qq docker-compose-plugin
fi
# Also install standalone for compatibility
if ! command -v docker-compose &>/dev/null; then
    COMPOSE_VER=$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest \
        | grep '"tag_name"' | sed 's/.*"v\([^"]*\)".*/\1/')
    curl -fsSL "https://github.com/docker/compose/releases/download/v${COMPOSE_VER}/docker-compose-linux-x86_64" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi
ok "Docker Compose: $(docker-compose --version)"

# ── 3. Configure Firewall ─────────────────────────────────────
step 3 "Configuring UFW firewall"
ufw --force reset >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow OpenSSH >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null
ok "Firewall: SSH(22), HTTP(80), HTTPS(443) open"

# ── 4. Configure fail2ban ─────────────────────────────────────
step 4 "Configuring fail2ban (brute-force protection)"
cat > /etc/fail2ban/jail.local << 'F2B'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
F2B
systemctl enable fail2ban >/dev/null
systemctl restart fail2ban
ok "fail2ban active"

# ── 5. Clone / Update Repository ──────────────────────────────
step 5 "Cloning repository"
REPO_ROOT="/opt/playplate-smm"
if [ -d "$REPO_ROOT/.git" ]; then
    echo "  Repository exists — pulling latest..."
    git -C "$REPO_ROOT" fetch origin
    git -C "$REPO_ROOT" checkout "$BRANCH"
    git -C "$REPO_ROOT" pull origin "$BRANCH"
    ok "Repository updated to latest"
else
    git clone --branch "$BRANCH" "$REPO" "$REPO_ROOT"
    ok "Repository cloned"
fi

# Move into the app directory
cd "$APP_DIR"
ok "Working directory: $APP_DIR"

# ── 6. Generate .env File ─────────────────────────────────────
step 6 "Setting up environment variables"
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"

    SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 20)
    REDIS_PASSWORD=$(openssl rand -hex 20)
    N8N_PASSWORD=$(openssl rand -hex 16)
    MINIO_SECRET=$(openssl rand -hex 20)

    sed -i "s|CHANGE_THIS_TO_A_RANDOM_64_CHAR_STRING|${SECRET_KEY}|g" .env
    sed -i "s|CHANGE_THIS_STRONG_DB_PASSWORD|${POSTGRES_PASSWORD}|g"  .env
    sed -i "s|CHANGE_THIS_STRONG_REDIS_PASSWORD|${REDIS_PASSWORD}|g"  .env
    sed -i "s|CHANGE_THIS_N8N_PASSWORD|${N8N_PASSWORD}|g"             .env
    sed -i "s|CHANGE_THIS_MINIO_SECRET|${MINIO_SECRET}|g"             .env
    sed -i "s|DOMAIN=social.playplate.in|DOMAIN=${DOMAIN}|g"          .env

    ok ".env generated with strong random secrets"
    warn "Add your API keys: nano $APP_DIR/.env"
else
    ok ".env already exists — skipping (won't overwrite)"
fi

# ── 7. SSL Certificate via Let's Encrypt ──────────────────────
step 7 "Setting up SSL certificate (Let's Encrypt)"
mkdir -p /var/www/certbot /etc/letsencrypt

# Quick temp nginx to serve ACME challenge
apt-get install -y -qq nginx
systemctl stop nginx 2>/dev/null || true

cat > /etc/nginx/sites-available/playplate-acme << ACME
server {
    listen 80;
    server_name ${DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'OK'; add_header Content-Type text/plain; }
}
ACME

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/playplate-acme /etc/nginx/sites-enabled/playplate-acme
nginx -t && systemctl start nginx

# Issue certificate
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    certbot certonly \
        --webroot \
        -w /var/www/certbot \
        --non-interactive \
        --agree-tos \
        --email "$ADMIN_EMAIL" \
        -d "$DOMAIN" \
        && ok "SSL certificate issued for $DOMAIN" \
        || warn "SSL failed — check DNS. Will use self-signed fallback."

    # Self-signed fallback if certbot fails
    if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
        mkdir -p "/etc/letsencrypt/live/${DOMAIN}"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" \
            -out    "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" \
            -subj   "/C=IN/ST=Punjab/L=Chandigarh/O=Playplate/CN=${DOMAIN}" \
            2>/dev/null
        warn "Using self-signed cert — replace with Let's Encrypt once DNS propagates"
    fi
else
    ok "SSL certificate already exists"
fi

systemctl stop nginx
systemctl disable nginx
ok "System nginx disabled (Docker nginx will handle traffic)"

# ── 8. Create directories ─────────────────────────────────────
step 8 "Creating required directories"
mkdir -p \
    "$APP_DIR/nginx/ssl" \
    "$APP_DIR/scripts" \
    /opt/backups \
    /var/log/playplate

# Copy SSL certs into nginx/ssl for volume mount fallback
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem "$APP_DIR/nginx/ssl/fullchain.pem" 2>/dev/null || true
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem   "$APP_DIR/nginx/ssl/privkey.pem"   2>/dev/null || true
ok "Directories created"

# ── 9. Build & Start Docker Services ──────────────────────────
step 9 "Building and starting Docker services"
cd "$APP_DIR"

# Pull base images first (faster build)
docker pull python:3.11-slim &
docker pull node:20-alpine &
docker pull postgres:15-alpine &
docker pull redis:7-alpine &
docker pull nginx:alpine &
docker pull n8nio/n8n:latest &
docker pull minio/minio:latest &
wait
ok "Base images pulled"

# Build and start
docker-compose build --parallel
docker-compose up -d

ok "All services started"

# ── 10. Wait for services to be healthy ───────────────────────
step 10 "Waiting for services to be healthy"
echo -n "  Waiting for PostgreSQL"
for i in $(seq 1 30); do
    if docker-compose exec -T postgres pg_isready -U smm -d smm_db >/dev/null 2>&1; then
        echo; ok "PostgreSQL ready"; break
    fi
    echo -n "."
    sleep 2
done

echo -n "  Waiting for Backend API"
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
        echo; ok "Backend API ready"; break
    fi
    echo -n "."
    sleep 3
done

# ── 11. Initialize knowledge base ─────────────────────────────
step 11 "Seeding knowledge base"
sleep 5

# Get admin token
TOKEN=$(curl -sf -X POST http://localhost:8000/api/auth/login \
    -F "username=admin@social.playplate.in" \
    -F "password=admin123" \
    2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null || echo "")

if [ -n "$TOKEN" ]; then
    curl -sf -X POST http://localhost:8000/api/knowledge-base/seed \
        -H "Authorization: Bearer $TOKEN" >/dev/null && ok "Knowledge base seeded"
    # Import n8n workflows
    warn "Import n8n workflows manually from: $APP_DIR/n8n/workflows/"
else
    warn "Could not auto-seed — do it manually from Admin → Knowledge Base"
fi

# ── 12. Setup Cron Jobs ───────────────────────────────────────
step 12 "Setting up cron jobs"

# SSL renewal
(crontab -l 2>/dev/null | grep -v certbot; \
 echo "0 3 * * * certbot renew --quiet --deploy-hook 'docker exec \$(docker ps -qf name=nginx) nginx -s reload'") | crontab -

# Daily DB backup
cat > /opt/backup-smm.sh << 'BACKUP'
#!/bin/bash
set -euo pipefail
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'postgres' | head -1)
docker exec "$CONTAINER" pg_dump -U smm smm_db | gzip > "$BACKUP_DIR/smm_db_${DATE}.sql.gz"
# Keep 7 days only
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
echo "[$(date)] Backup OK: smm_db_${DATE}.sql.gz"
BACKUP
chmod +x /opt/backup-smm.sh

(crontab -l 2>/dev/null | grep -v backup-smm; \
 echo "0 2 * * * /opt/backup-smm.sh >> /var/log/playplate/backup.log 2>&1") | crontab -

ok "Cron jobs configured (SSL renewal + daily backup)"

# ── Final Status ──────────────────────────────────────────────
echo ""
docker-compose ps
echo ""

# Show passwords
POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d= -f2)
N8N_PASSWORD=$(grep "^N8N_PASSWORD=" .env | cut -d= -f2)

echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 🎉 DEPLOYMENT COMPLETE!                 ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  🌐 Client Dashboard:                                   ║"
echo "║     https://social.playplate.in/client                  ║"
echo "║                                                          ║"
echo "║  🔧 Admin Panel:                                         ║"
echo "║     https://social.playplate.in/admin                   ║"
echo "║                                                          ║"
echo "║  ⚙️  n8n Workflows:                                      ║"
echo "║     https://social.playplate.in/n8n                     ║"
echo "║                                                          ║"
echo "║  📖 API Docs:                                            ║"
echo "║     https://social.playplate.in/api/docs                ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  🔐 LOGIN CREDENTIALS:                                   ║"
echo "║  Admin:  admin@social.playplate.in / admin123           ║"
echo "║  Doctor: dr.anshu@chandigarhdentist.com / doctor123     ║"
echo "║  n8n:    admin / $N8N_PASSWORD"
printf  "║  %-54s ║\n" " "
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  ⚠️  NEXT STEPS (IMPORTANT):                             ║"
echo "║  1. Change default passwords immediately                 ║"
echo "║  2. Admin → API Credentials → Add your API keys:        ║"
echo "║     • OpenAI API Key (content generation)               ║"
echo "║     • Anthropic Claude API (content writing)            ║"
echo "║     • SendGrid (email notifications)                     ║"
echo "║     • Meta Access Token (Instagram + Facebook)          ║"
echo "║     • LinkedIn Access Token                              ║"
echo "║     • Kling/Runway/Pika (video generation)              ║"
echo "║  3. Admin → Knowledge Base → Seed KB                    ║"
echo "║  4. Import n8n workflows from n8n/workflows/            ║"
echo "║  5. Content auto-generates daily at 9:00 AM IST         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
