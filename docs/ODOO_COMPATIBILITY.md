# Odoo compatibility and deployment audit

**Status:** Stage 0 fact record. The target Odoo.sh environment is not verified by this repository.

## 1. Confirmed version for this repository

| Evidence | Value |
|---|---|
| `AGENTS.md` | Target: Odoo Community Edition `18.0-20251222`. |
| `Dockerfile` | `FROM odoo:18.0-20251222` pinned by digest. |
| `compose.yaml` | Image tag default `18.0-20251222`. |
| `.env.example` | `REPKA_IMAGE_TAG=18.0-20251222`. |
| Custom module manifests | Version convention `18.0.x.y.z`. |

**Conclusion:** `repka-odoo` is internally targeted at Odoo CE 18 build `18.0-20251222`.

## 2. Odoo.sh target: unconfirmed and blocking

The stakeholder reports that LM GROUP Odoo.sh targets Odoo Community `18.0-20251222`, which matches this repository. This report is not yet independently verified from Odoo.sh. The repository has no Odoo.sh project metadata, no Odoo.sh branch/environment configuration and no confirmed project link. Therefore the following remain **unknown**:

- exact Odoo release/build and edition (Community / Enterprise / other);
- Odoo.sh project, Git remote and branch policy;
- Development/Staging/Production environments and automated test configuration;
- installed custom modules, OCA modules, enterprise dependencies and licensing constraints;
- supported addon path/repository layout;
- data migration, backup and rollback workflow.

Do not infer the Odoo.sh target from this Docker repository or its README. No Odoo module for the target environment may be authored or deployed until the owner supplies this information.

## 3. Current module landscape

| Category | Confirmed modules / role |
|---|---|
| Meta/base | `repka_suite`, `repka_base`, `repka_standard`, `repka_oca` |
| Logistics | `repka_logistics_core`, `repka_forwarding`, `repka_invoices*`, `repka_complex_reporting`, `repka_special_lm`, `repka_excel_report` and supporting modules |
| Fleet | `repka_fleet*` family |
| Web UX | `repka_*` widgets, map, attachment and tree-view helpers |
| AI demo/queue | `repka_ai_document_check`, `repka_ai_demo_showcase` |

`repka_suite` aggregates Odoo core apps such as CRM, sales, purchase, stock, calendar and project alongside project-specific modules. This signals a broad Odoo dependency surface: any new module must list only necessary dependencies and be tested against the actual target.

## 4. Existing AI-related compatibility notes

- `repka_ai_document_check` depends on `base`, `mail` and `repka_forwarding`; it submits an HTTP payload to a configurable endpoint, then records a result in Odoo.
- The bundled `ai_document_check_mock` is a deterministic development service. It is not an OCR/LLM integration and must not be represented as one.
- `repka_ai_demo_showcase` is for the `repka_test` database and its logout behaviour is explicitly conditional on that test database. It must remain excluded from production workflows.
- `ai_automations/` is external to the Odoo addon runtime and uses synthetic data; it is not an Odoo.sh deployment artefact.

A future AI gateway integration must remain version-compatible with the verified target Odoo and have an approved security/authentication contract. Direct arbitrary HTTP endpoints and production document transfer are not acceptable.

## 5. Identity and MFA compatibility

`repka_standard` declares dependencies on `auth_signup`, `auth_totp`, `auth_totp_mail` and `auth_totp_portal`. This means the current repository includes Odoo modules that can support TOTP-related flows, but it does **not** demonstrate a configured production MFA policy or a mapping to LM GROUP roles.

The authentication implementation is a pending architecture decision:

1. corporate SSO/IdP, if verified and approved;
2. Odoo-native identity/MFA if the corporate application is hosted within a suitable Odoo boundary;
3. separate application identity service with secure password/MFA lifecycle.

Whichever is selected, it must be tested separately for account provisioning, deactivation, session revocation and administrative MFA.

## 6. OCA dependencies and licensing

`requirements-oca.txt` contains hash-locked Odoo 18 packages and the Docker image installs them with `--require-hashes --no-deps`. The repository README states that `web_timeline` and `currency_rate_update` are AGPL-3 and the remaining attached OCA modules are LGPL-3.

Before redistribution, proprietary module coupling, Odoo.sh deployment or SaaS delivery, validate the current license texts, dependency graph and obligations with the responsible legal/technical owner. This audit does not provide legal advice.

## 7. Required compatibility checks for every new Odoo change

1. Confirm exact Odoo.sh version/edition, installed dependency list and addon path.
2. Create an approved feature branch, never edit production branch directly.
3. Validate Python, XML, manifest version/dependencies, record rules/ACL and migrations.
4. Run an isolated test database without production secrets/data:

```bash
docker compose -f compose.yaml run --rm --no-deps odoo odoo \
  -d repka_test -i <module> --without-demo=all \
  --test-enable --test-tags=/<module> --stop-after-init
```

5. Run the equivalent Odoo.sh Development/Staging checks after their actual workflow is confirmed.
6. Produce a report: affected files, rationale, diff, tests, result, risk and rollback.
7. Require a human approval for PR merge, staging deployment, production deployment, schema/data/access/financial changes.

## 8. Deployment-path decision to make

The existing repository includes Docker Compose and Caddy for a self-managed Odoo/VPS path. Odoo.sh is separately named as the target development environment in the LM GROUP brief. These are not automatically the same deployment model.

Before implementation, decide and document:

- whether the existing Odoo deployment is a local/demo environment, a VPS target, or an Odoo.sh source tree;
- whether the corporate AI application is a separate service or an Odoo extension;
- how source, CI, secrets, staging and production promotion relate between these environments.

Until that decision, all Odoo.sh compatibility claims remain pending.
