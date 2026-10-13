# Test-only environment setup — LM GROUP

**Status:** approved test-only direction. This document does not authorise a production deployment, DNS change, VPS purchase or Windows Server access.

## 1. Scope and hard boundaries

The initial environment is a disposable **test database** named `repka_test` for the existing Odoo repository.

Allowed:

- synthetic demo data and the repository's own test records;
- local/isolated development, module tests and UI exploration;
- the repository's deterministic AI demos and mock service;
- a separate public test host only after manual VPS/domain procurement and the steps below.

Forbidden:

- production Odoo data, credentials, documents or file shares;
- Windows Server connector, SMB/RDP exposure or indexing of corporate folders;
- Ollama, Mac mini worker or external AI providers;
- production deployment, automatic mail/send/sign actions;
- public PostgreSQL, Redis, Odoo internals or administrative endpoints.

## 2. Recommended topology

### Level A — isolated test sandbox (current)

Use Devin DRS sandbox for repeatable repository setup and tests. It contains no corporate secrets or documents and is not publicly exposed.

### Level B — local Mac mini test environment (later)

Use Docker Compose only after an approved Mac mini hardening plan. The development compose file binds Odoo to `127.0.0.1:8069`, so it is accessible only on the local Mac:

```text
Mac mini browser → http://127.0.0.1:8069 → Odoo repka_test + PostgreSQL
```

Do not expose the development port through router rules, port forwarding or a tunnel.

### Level C — optional public test host (later)

If browser access outside the Mac mini becomes necessary, use a separate VPS and a separately acquired test domain. Keep the host logically separate from the personal VPN VPS and from the Windows file server:

```text
Pilot browser → HTTPS → Caddy → Odoo repka_test
                                  └─ private PostgreSQL
```

The public host has no Windows connector, no Mac mini worker, no Ollama and no corporate document corpus.

## 3. VPS parameters for a public test-only host

Use one VM with the following minimum specification:

| Parameter | Recommended value | Reason |
|---|---|---|
| Operating system | Ubuntu Server 24.04 LTS or Debian 12 | Mature Docker support and a supported security-update lifecycle. |
| CPU | 4 vCPU | Odoo, PostgreSQL, asset generation and 2 Odoo workers need headroom. |
| RAM | 8 GB | Safer than the repository's 4 GB development minimum for public test use. |
| Disk | 80 GB encrypted NVMe/SSD | Images, PostgreSQL, filestore, logs and test backups. |
| Network | Public IPv4, ordinary outbound HTTPS/DNS | Required for HTTPS certificate issuance and image updates. |
| Region | A jurisdiction approved for LM GROUP test data | The environment must still contain synthetic data only. |
| Backup | Provider snapshot plus encrypted application backup | Verify restore before putting any non-synthetic data there. |
| Administration | Named owner, provider console, MFA | Do not share root credentials. |

This is sufficient for a **single test instance only**. It is not sized for production RAG, embeddings, many concurrent users, Windows indexing or local-model inference.

### Required inbound exposure

| Port | Purpose | Rule |
|---|---|---|
| 443/TCP | HTTPS through Caddy | Allowed after domain/TLS setup. |
| 80/TCP | ACME HTTP certificate validation and redirect | Allowed only if the chosen certificate method needs it. |
| 22/TCP | Administration | Do not leave generally public. Use provider console or a separately approved restricted administration method. |
| 5432/TCP | PostgreSQL | Never public. |
| 6379/TCP | Redis, if introduced later | Never public. |
| 8069/8072 | Odoo HTTP/WebSocket | Never public; Caddy proxies privately. |
| 11434/TCP | Ollama | Never public. |

## 4. Separate test domain

Use a separate domain owned by LM GROUP, not the personal VPN domain. Suggested naming pattern:

```text
test.<new-domain>
```

Before purchasing, verify that:

1. the registrar account is owned by LM GROUP, not by an individual;
2. account MFA and recovery contact are controlled by the company;
3. DNS access is available to the system owner;
4. the domain does not resemble a bank, government service or another third party;
5. there is a documented renewal owner and payment process.

After the domain is purchased manually, create one DNS `A` record from `test.<new-domain>` to the **separate test VPS** public IPv4. Do not point it at the Windows Server, Mac mini or VPN VPS.

## 5. Local test database setup on Mac mini

The current Mac mini uses a user-level Colima Docker runtime with 4 vCPU, 6 GiB RAM and 60 GiB disk. Docker Desktop is not required for this local test setup. Colima exposes a local Unix socket only; do not add router port forwarding, tunnels or public listeners.

Start the local runtime before using the following test procedure from the repository root:

```bash
colima start --cpu 4 --memory 6 --disk 60 --vm-type vz --mount-type virtiofs
```

```bash
cp .env.example .env
```

Edit the local, Git-ignored `.env` file so that at minimum it contains:

```dotenv
COMPOSE_PROJECT_NAME=lmgroup-test
ODOO_DB_NAME=repka_test
ODOO_HTTP_PORT=8069
REPKA_IMAGE_TAG=18.0-20251222
```

Then initialise the isolated database:

```bash
./scripts/init.sh
```

The script generates local secrets under `secrets/`, creates the `repka_test` database on the local Docker PostgreSQL instance, installs `repka_suite`, and starts the development stack. It does not use production credentials.

Validate and test it:

```bash
docker compose -f compose.yaml -f compose.dev.yaml config --quiet
npm --prefix apps/lm-group-pwa run lint
npm --prefix apps/lm-group-pwa run build
docker compose -f compose.yaml run --rm --no-deps odoo odoo \
  -d repka_test -i repka_suite --without-demo=all \
  --test-enable --test-tags=/repka_suite --stop-after-init
```

Open only on the Mac mini:

```text
http://127.0.0.1:8069
```

The bootstrap password is stored only in `secrets/odoo_admin_password.txt`; do not paste it into chat, tickets, commits or screenshots.

### Secret handling in the test image

The custom image entrypoint runs as root only long enough to copy the Docker bind-mounted secrets into `/run/repka-secrets` with owner `odoo` and mode `0400`. It then runs Odoo and the mock as the unprivileged `odoo` user. Odoo reads its database settings from a temporary `0400` config file, so the database password is not passed in the process command line.

Do not rotate only `secrets/postgresql_password.txt` while retaining an existing PostgreSQL volume: PostgreSQL will still hold the previous password. For a disposable test database, recreate the database/volume and secrets together. Never apply that deletion procedure to a non-test database without separately approved recovery steps.

## 6. Public test host procedure

Perform these steps only after you manually purchase the VPS and domain and after the test-host owner confirms its backup/admin process.

1. Install Docker Engine and Docker Compose v2 using the operating-system/provider approved method.
2. Clone the repository using a deploy identity with read-only access where possible.
3. Copy `.env.example` to `.env`; do not commit `.env`.
4. Set unique test-only values:

   ```dotenv
   COMPOSE_PROJECT_NAME=lmgroup-test
   ODOO_DB_NAME=repka_test
   ODOO_DOMAIN=test.<new-domain>
   ODOO_WORKERS=2
   ODOO_MAX_CRON_THREADS=1
   REPKA_IMAGE_TAG=18.0-20251222
   ```

5. Run `./scripts/init.sh` once to create local test secrets and initialise the database.
6. Stop the loopback development profile while preserving its named volumes:

   ```bash
   docker compose -f compose.yaml -f compose.dev.yaml down
   ```

7. Validate the production-style Compose configuration before starting it:

   ```bash
   docker compose -f compose.yaml -f compose.prod.yaml config --quiet
   ```

8. Start the test-only public profile:

   ```bash
   docker compose -f compose.yaml -f compose.prod.yaml up -d --wait
   ```

9. Verify from an external browser that only HTTPS Odoo is available. Confirm that PostgreSQL, Odoo 8069/8072, Redis, SSH, SMB/RDP and Ollama are not public.
10. Run the synthetic test suite and record its result. Do not load corporate documents or credentials.

For rollback, stop the public profile without deleting named volumes:

```bash
docker compose -f compose.yaml -f compose.prod.yaml down
```

Do not run `down -v`, delete volumes or remove databases without explicit separate approval.

## 7. Gates before moving beyond test-only Odoo

- verified Odoo.sh branches/modules/backup workflow;
- named identity and MFA approach for pilot users;
- approved Mac mini hardening before worker/Ollama;
- separate VPS/domain ownership and DNS/TLS procedure;
- backup retention and successful restore drill;
- approved document sources, ACL and file connector plan.

Until these gates pass, the allowed scope is the Odoo `repka_test` database and synthetic demonstrations only.
