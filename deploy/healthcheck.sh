#!/usr/bin/env bash
# Validate deployment health. Exit non-zero if anything is unhealthy.
set -uo pipefail
cd "$(dirname "$0")/.."

DOMAIN="${DOMAIN:-trading.playplate.in}"
FAIL=0

check() {
  local name="$1" url="$2"
  if curl -fsS --max-time 10 "$url" >/dev/null 2>&1; then
    echo "  ✓ $name"
  else
    echo "  ✗ $name ($url)"
    FAIL=1
  fi
}

echo "==> Container status"
docker compose ps

echo "==> Internal liveness (via backend container)"
if docker compose exec -T backend curl -fsS http://localhost:8000/api/health/live >/dev/null 2>&1; then
  echo "  ✓ backend liveness"
else
  echo "  ✗ backend liveness"
  FAIL=1
fi

echo "==> Readiness (DB + mode)"
docker compose exec -T backend curl -fsS http://localhost:8000/api/health/ready || FAIL=1
echo

echo "==> Public endpoints"
check "HTTP redirect"  "http://localhost/"
check "HTTPS frontend" "https://${DOMAIN}/" || true   # may fail locally without TLS/DNS

if [ "$FAIL" -eq 0 ]; then
  echo "==> Health check PASSED"
else
  echo "==> Health check reported issues (see above)"
fi
exit $FAIL
