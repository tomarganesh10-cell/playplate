#!/usr/bin/env bash
# Issue the Let's Encrypt certificate for the domain and switch nginx to HTTPS.
#
# Prerequisite: the stack is already running (deploy.sh) serving HTTP on port 80,
# and DNS for $DOMAIN points to this VPS. The HTTP-first nginx config already
# serves the ACME challenge, so no bootstrap swap is needed.
set -euo pipefail

DOMAIN="${DOMAIN:-trading.playplate.in}"
EMAIL="${LETSENCRYPT_EMAIL:-admin@playplate.in}"
STAGING="${STAGING:-0}"   # set STAGING=1 to test against LE staging

cd "$(dirname "$0")/.."
mkdir -p certbot/conf certbot/www

echo "==> Ensuring nginx is up to serve the ACME challenge"
docker compose up -d nginx
sleep 2

STAGING_FLAG=""
[ "$STAGING" = "1" ] && STAGING_FLAG="--staging"

echo "==> Requesting certificate for ${DOMAIN}"
docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  ${STAGING_FLAG} \
  -d ${DOMAIN} \
  --email ${EMAIL} --agree-tos --no-eff-email --non-interactive" certbot

echo "==> Writing HTTPS vhost and switching port 80 to redirect"

# Port 80: serve ACME + redirect everything else to HTTPS.
cat > infra/nginx/conf.d/trading.playplate.in.conf <<EOF
upstream backend_upstream { server backend:8000; }
upstream frontend_upstream { server frontend:80; }

server {
  listen 80 default_server;
  server_name _;
  location /.well-known/acme-challenge/ { root /var/www/certbot; }
  location / { return 301 https://${DOMAIN}\$request_uri; }
}
EOF

# Port 443: TLS termination + proxy to the app.
cat > infra/nginx/conf.d/https.conf <<EOF
server {
  listen 443 ssl;
  http2 on;
  server_name ${DOMAIN};

  ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 1d;

  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;

  location /api/ {
    limit_req zone=api burst=40 nodelay;
    proxy_pass http://backend_upstream;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_read_timeout 60s;
  }

  location = /metrics {
    proxy_pass http://backend_upstream/api/metrics;
    allow 172.16.0.0/12;
    allow 127.0.0.1;
    deny all;
  }

  location / {
    proxy_pass http://frontend_upstream;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }
}
EOF

echo "==> Reloading nginx with TLS"
docker compose up -d nginx
docker compose exec -T nginx nginx -s reload || docker compose restart nginx

echo "==> Done. https://${DOMAIN} is now live."
echo "    Start cert auto-renewal: docker compose --profile ssl up -d certbot"
