#!/bin/bash
# ============================================================
# Playplate AI Social Media Manager — One-Shot VPS Setup
# Run on Hostinger VPS as root:
#   curl -sS https://raw.githubusercontent.com/.../setup.sh | bash
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

DOMAIN="social.playplate.in"
APP_DIR="/opt/playplate-smm"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Playplate AI Social Media Manager — Setup       ║"
echo "║     Dr. Anshu Gupta — Chandigarh Dentist            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. System Update ──────────────────────────────────────
echo -e "${BLUE}[1/10] Updating system packages...${NC}"
apt-get update -qq && apt-get upgrade -y -qq

# ── 2. Install Dependencies ───────────────────────────────
echo -e "${BLUE}[2/10] Installing dependencies...${NC}"
apt-get install -y -qq \
    curl wget git unzip htop \
    nginx certbot python3-certbot-nginx \
    ufw fail2ban \
    ca-certificates gnupg lsb-release

# ── 3. Install Docker ─────────────────────────────────────
echo -e "${BLUE}[3/10] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# ── 4. Configure Firewall ─────────────────────────────────
echo -e "${BLUE}[4/10] Configuring firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}✅ Firewall configured${NC}"

# ── 5. Setup fail2ban ─────────────────────────────────────
echo -e "${BLUE}[5/10] Configuring fail2ban...${NC}"
systemctl enable fail2ban && systemctl start fail2ban

# ── 6. Create App Directory ───────────────────────────────
echo -e "${BLUE}[6/10] Setting up application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# ── 7. Setup Environment ──────────────────────────────────
echo -e "${BLUE}[7/10] Setting up environment...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cp .env.example .env

    # Generate secrets
    SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 20)
    REDIS_PASSWORD=$(openssl rand -hex 20)
    N8N_PASSWORD=$(openssl rand -hex 16)

    sed -i "s/CHANGE_THIS_TO_A_RANDOM_64_CHAR_STRING/$SECRET_KEY/" .env
    sed -i "s/CHANGE_THIS_STRONG_DB_PASSWORD/$POSTGRES_PASSWORD/" .env
    sed -i "s/CHANGE_THIS_STRONG_REDIS_PASSWORD/$REDIS_PASSWORD/" .env
    sed -i "s/CHANGE_THIS_N8N_PASSWORD/$N8N_PASSWORD/" .env

    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env to add your API keys!${NC}"
    echo "   nano $APP_DIR/.env"
fi

# ── 8. SSL Certificate ────────────────────────────────────
echo -e "${BLUE}[8/10] Setting up SSL certificate...${NC}"
# Initial nginx setup without SSL
cat > /etc/nginx/sites-available/playplate-temp << 'EOF'
server {
    listen 80;
    server_name social.playplate.in;
    root /var/www/html;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'Playplate SMM - Starting up...'; }
}
EOF
ln -sf /etc/nginx/sites-available/playplate-temp /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get SSL certificate
certbot certonly --webroot -w /var/www/certbot \
    --non-interactive --agree-tos \
    --email admin@playplate.in \
    -d $DOMAIN \
    || echo -e "${YELLOW}⚠️  SSL setup requires DNS to point to this server${NC}"

# ── 9. Start Services ─────────────────────────────────────
echo -e "${BLUE}[9/10] Starting services...${NC}"
cd $APP_DIR
docker-compose pull
docker-compose up -d --build

echo -e "${BLUE}[10/10] Waiting for services to be ready...${NC}"
sleep 30

# Check health
docker-compose ps

# ── 10. Setup Cron for SSL renewal ────────────────────────
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker exec nginx nginx -s reload" | crontab -

# ── Setup Cron for DB Backup ──────────────────────────────
mkdir -p /opt/backups
cat > /opt/backup-smm.sh << 'BACKUP'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec postgres pg_dump -U smm smm_db > "$BACKUP_DIR/smm_db_$DATE.sql"
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
echo "Backup completed: $DATE"
BACKUP
chmod +x /opt/backup-smm.sh
echo "0 2 * * * /opt/backup-smm.sh >> /var/log/smm-backup.log 2>&1" | crontab -

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║            🎉 Setup Complete!                       ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Dashboard:  https://social.playplate.in/client    ║"
echo "║  Admin:      https://social.playplate.in/admin     ║"
echo "║  n8n:        https://social.playplate.in/n8n       ║"
echo "║  API Docs:   https://social.playplate.in/api/docs  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Admin Login: admin@social.playplate.in            ║"
echo "║  Doctor Login: dr.anshu@chandigarhdentist.com      ║"
echo "║  Default Password: doctor123 (CHANGE IMMEDIATELY)  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  ⚠️  Next Steps:                                    ║"
echo "║  1. Edit .env with your API keys                   ║"
echo "║  2. Go to /admin → API Credentials                 ║"
echo "║  3. Add OpenAI, Claude, Meta, LinkedIn keys        ║"
echo "║  4. Trigger first website crawl from admin         ║"
echo "║  5. Content will auto-generate at 9:00 AM IST      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
