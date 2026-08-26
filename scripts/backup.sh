#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
BACKUP_DIR="$ROOT_DIR/backups"

if [[ ! -f "$ENV_FILE" ]]; then
    printf '.env does not exist.\n' >&2
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ ! "${ODOO_DB_NAME:-}" =~ ^[A-Za-z0-9_]+$ ]]; then
    printf 'ODOO_DB_NAME must contain only letters, digits, and underscores.\n' >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
database_backup="$BACKUP_DIR/${ODOO_DB_NAME}_${timestamp}.dump"
filestore_backup="$BACKUP_DIR/${ODOO_DB_NAME}_${timestamp}_filestore.tar.gz"
checksum_file="$BACKUP_DIR/${ODOO_DB_NAME}_${timestamp}.sha256"
compose=(docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/compose.yaml")

cleanup_failed_backup() {
    status=$?
    rm -f "$database_backup" "$filestore_backup" "$checksum_file"
    exit "$status"
}
trap cleanup_failed_backup ERR

"${compose[@]}" exec -T db pg_dump -U odoo -d "$ODOO_DB_NAME" --format=custom --no-owner --no-privileges > "$database_backup"
"${compose[@]}" exec -T db pg_restore --list < "$database_backup" > /dev/null

if "${compose[@]}" exec -T odoo test -d "/var/lib/odoo/filestore/$ODOO_DB_NAME"; then
    "${compose[@]}" exec -T odoo tar -C /var/lib/odoo -czf - "filestore/$ODOO_DB_NAME" > "$filestore_backup"
else
    "${compose[@]}" exec -T odoo tar -czf - --files-from /dev/null > "$filestore_backup"
fi

tar -tzf "$filestore_backup" > /dev/null
chmod 600 "$database_backup" "$filestore_backup"
shasum -a 256 "$database_backup" "$filestore_backup" > "$checksum_file"
chmod 600 "$checksum_file"
trap - ERR

printf 'Database backup: %s\n' "$database_backup"
printf 'Filestore backup: %s\n' "$filestore_backup"
