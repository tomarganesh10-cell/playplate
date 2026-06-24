# SSL Configuration — Let's Encrypt for `trading.playplate.in`

TLS is terminated at the Nginx edge container. Certificates are issued and
renewed by the bundled `certbot` service using the HTTP-01 challenge.

## Prerequisites

- DNS A record for `trading.playplate.in` resolves to the VPS
  (see [`DNS_CONFIGURATION.md`](DNS_CONFIGURATION.md)).
- Ports 80 and 443 are open (the VPS setup script opens them via UFW).
- `.env` has `DOMAIN=trading.playplate.in` and a valid `LETSENCRYPT_EMAIL`
  is exported (or edit the default in `deploy/init_ssl.sh`).

## Issue the initial certificate

```bash
# Optional dry run against the staging CA to avoid rate limits:
STAGING=1 LETSENCRYPT_EMAIL=admin@playplate.in bash deploy/init_ssl.sh

# Real issuance:
LETSENCRYPT_EMAIL=admin@playplate.in bash deploy/init_ssl.sh
```

What the script does:

1. Writes a temporary HTTP-only nginx vhost so the ACME challenge is reachable.
2. Temporarily disables the TLS vhost (which references not-yet-existing certs).
3. Runs `certbot certonly --webroot` for the domain.
4. Restores the TLS vhost and reloads nginx.

Certificates live in `./certbot/conf/live/trading.playplate.in/` and are mounted
read-only into the nginx container.

## Auto-renewal

Start the renewal sidecar (it runs `certbot renew` every 12h):

```bash
docker compose --profile ssl up -d certbot
```

After a renewal, reload nginx to pick up the new cert. A simple cron entry:

```cron
0 3 * * * cd /home/playplate/playplate && docker compose exec -T nginx nginx -s reload
```

## Verify

```bash
curl -I https://trading.playplate.in            # expect HTTP/2 200
openssl s_client -connect trading.playplate.in:443 -servername trading.playplate.in </dev/null \
  | openssl x509 -noout -dates -issuer
```

The vhost already enables HSTS, TLS 1.2/1.3 only, and modern ciphers. Test your
config with SSL Labs (<https://www.ssllabs.com/ssltest/>) — aim for an A grade.

## Troubleshooting

- **Challenge fails (timeout/404):** DNS not propagated, or port 80 blocked.
  Confirm `dig +short trading.playplate.in` and `ufw status`.
- **Rate limited:** you hit Let's Encrypt limits — use `STAGING=1` while testing.
- **Cert present but nginx won't start:** ensure the TLS vhost file was restored
  (not left as `.disabled`) and paths under `/etc/letsencrypt/live/...` exist.
