# Project Rules

- Target Odoo version: `18.0-20251222` Community Edition.
- Start the local stack with `./scripts/init.sh`; subsequent starts use `docker compose -f compose.yaml -f compose.dev.yaml up -d`.
- Validate Compose with `docker compose -f compose.yaml -f compose.dev.yaml config --quiet` and `ODOO_DOMAIN=erp.example.com docker compose -f compose.yaml -f compose.prod.yaml config --quiet`.
- Run an addon test in a dedicated database with `docker compose -f compose.yaml run --rm --no-deps odoo odoo -d repka_test -i <module> --without-demo=all --test-enable --test-tags=/<module> --stop-after-init`.
- Keep source audit exports in `audit/` or outside the repository; never commit them.
- Never commit `.env`, `secrets/`, `backups/`, credentials, filestore content, or PostgreSQL data.
- Preserve audited technical model and field names when required for future data migration, but implement proprietary UFS behavior clean-room rather than copying source code.
