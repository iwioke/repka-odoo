#!/bin/sh
set -eu

command="${1:-}"
if [ "$command" = "odoo" ] || [ "$command" = "--" ] || [ "${command#-}" != "$command" ]; then
    secret_dir=/run/repka-secrets
    config_file="$secret_dir/odoo.conf"
    install -d -m 0700 -o odoo -g odoo "$secret_dir"
    for secret in postgresql_password odoo_admin_password; do
        install -m 0400 -o odoo -g odoo "/run/secrets/$secret" "$secret_dir/$secret"
    done
    {
        cat /etc/odoo/odoo.conf
        printf '\ndb_host = %s\ndb_port = %s\ndb_user = %s\ndb_password = %s\n' \
            "${HOST:-db}" "${PORT:-5432}" "${USER:-odoo}" "$(cat "$secret_dir/postgresql_password")"
    } > "$config_file"
    chown odoo:odoo "$config_file"
    chmod 0400 "$config_file"
    export ODOO_ADMIN_PASSWORD_FILE="$secret_dir/odoo_admin_password"
    if [ "$command" = "odoo" ] || [ "$command" = "--" ]; then
        shift
    fi
    exec setpriv --reuid=odoo --regid=odoo --init-groups -- odoo "$@" -c "$config_file"
fi

exec setpriv --reuid=odoo --regid=odoo --init-groups -- /entrypoint.sh "$@"
