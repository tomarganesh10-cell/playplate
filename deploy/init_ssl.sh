#!/usr/bin/env bash
# Obtain the initial Let's Encrypt certificate for trading.playplate.in.
# Prerequisite: DNS A record already points to this VPS (see docs/DNS_CONFIGURATION.md).
set -euo pipefail

DOMAIN="${DOMAIN:-trading.playplate.in}"
EMAIL="${LETSENCRYPT_EMAIL:-admin@playplate.in}"
STAGING="${STAGING:-0}"   # set STAGING=1 to test against LE staging

cd "$(dirname "$0")/.."

echo "==> Preparing certbot directories"
mkdir -p certbot/conf certbot/www

# Temporary HTTP-only nginx config so the ACME challenge can be served before
# any certificate exists.
TMP_CONF="infra/nginx/conf.d/_bootstrap.conf"
cat > "$TMP_CONF" <<EOF
server {
  listen 80;
  server_name ${DOMAIN};
  location /.well-known/acme-challenge/ { root /var/www/certbot; }
  location / { return 200 'bootstrap'; add_header Content-Type text/plain; }
}
EOF

# Move the TLS vhost out of the way until the cert exists.
if [ -f infra/nginx/conf.d/${DOMAIN}.conf ]; then
  mv infra/nginx/conf.d/${DOMAIN}.conf infra/nginx/conf.d/${DOMAIN}.conf.disabled
fi

echo "==> Starting nginx (HTTP only) for the ACME challenge"
docker compose up -d nginx
sleep 3

STAGING_FLAG=""
[ "$STAGING" = "1" ] && STAGING_FLAG="--staging"

echo "==> Requesting certificate for ${DOMAIN}"
docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  ${STAGING_FLAG} \
  -d ${DOMAIN} \
  --email ${EMAIL} --agree-tos --no-eff-email --non-interactive" certbot

echo "==> Restoring TLS vhost and removing bootstrap config"
rm -f "$TMP_CONF"
if [ -f infra/nginx/conf.d/${DOMAIN}.conf.disabled ]; then
  mv infra/nginx/conf.d/${DOMAIN}.conf.disabled infra/nginx/conf.d/${DOMAIN}.conf
fi

echo "==> Reloading nginx with TLS"
docker compose up -d nginx
docker compose exec nginx nginx -s reload || docker compose restart nginx

echo "==> Certificate installed. Auto-renewal runs via the certbot service (profile: ssl)."
echo "    Start the renewal sidecar with: docker compose --profile ssl up -d certbot"
