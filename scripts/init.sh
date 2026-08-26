#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
SECRETS_DIR="$ROOT_DIR/secrets"

command -v docker >/dev/null 2>&1 || {
    printf 'Docker is required but was not found.\n' >&2
    exit 1
}

docker compose version >/dev/null

if [[ ! -f "$ENV_FILE" ]]; then
    cp "$ROOT_DIR/.env.example" "$ENV_FILE"
fi

set -a
source "$ENV_FILE"
set +a

if [[ ! "${ODOO_DB_NAME:-}" =~ ^[A-Za-z0-9_]+$ ]]; then
    printf 'ODOO_DB_NAME must contain only letters, digits, and underscores.\n' >&2
    exit 1
fi

mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

if [[ ! -s "$SECRETS_DIR/postgresql_password.txt" ]]; then
    openssl rand -base64 48 > "$SECRETS_DIR/postgresql_password.txt"
fi

if [[ ! -s "$SECRETS_DIR/odoo_admin_password.txt" ]]; then
    openssl rand -base64 32 > "$SECRETS_DIR/odoo_admin_password.txt"
fi

chmod 600 "$SECRETS_DIR"/*.txt

compose=(docker compose --project-directory "$ROOT_DIR" -f "$ROOT_DIR/compose.yaml" -f "$ROOT_DIR/compose.dev.yaml")

"${compose[@]}" up -d --wait db

database_exists="$("${compose[@]}" exec -T db psql -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$ODOO_DB_NAME'" | tr -d '[:space:]')"

if [[ "$database_exists" != "1" ]]; then
    "${compose[@]}" run --rm --no-deps odoo odoo -d "$ODOO_DB_NAME" -i repka_suite --without-demo=all --stop-after-init
    "${compose[@]}" run --rm --no-deps -T odoo odoo shell -d "$ODOO_DB_NAME" < "$ROOT_DIR/scripts/container/set_admin_password.py"
fi

"${compose[@]}" up -d --wait odoo

printf 'REPKA is available at http://127.0.0.1:%s\n' "${ODOO_HTTP_PORT:-8069}"
printf 'Login: admin\n'
printf 'The local bootstrap password is stored in secrets/odoo_admin_password.txt\n'
