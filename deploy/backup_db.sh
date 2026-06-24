#!/usr/bin/env bash
# Dump the PostgreSQL database to ./backups with timestamped, gzipped files.
# Schedule via cron, e.g.:  0 2 * * * /home/playplate/playplate/deploy/backup_db.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# Load DB creds from .env without exporting everything noisily.
set -a; [ -f .env ] && . ./.env; set +a

BACKUP_DIR="backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${BACKUP_DIR}/playplate_${STAMP}.sql.gz"

echo "==> Backing up database to $OUT"
docker compose exec -T postgres pg_dump \
  -U "${POSTGRES_USER:-playplate}" \
  -d "${POSTGRES_DB:-playplate}" | gzip > "$OUT"

echo "==> Pruning backups older than ${RETENTION_DAYS} days"
find "$BACKUP_DIR" -name 'playplate_*.sql.gz' -mtime "+${RETENTION_DAYS}" -delete

echo "==> Backup complete: $(du -h "$OUT" | cut -f1)"
