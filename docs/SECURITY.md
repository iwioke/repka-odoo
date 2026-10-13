# Security model for LM GROUP corporate AI application

**Status:** Stage 0 security baseline. Requirements become implementation controls only after architecture and infrastructure approvals.

## 1. Security objectives

1. Corporate documents are visible only to authorised identities at document, chunk, citation, cache and log layers.
2. Public access uses HTTPS without VPN; office nodes never require public inbound access.
3. Administrative, Odoo and outbound actions stay human-approved and auditable.
4. Production secrets, data and infrastructure remain outside the repository and outside AI prompts/logs.
5. The system fails closed on unknown identity, unavailable ACL check, invalid worker identity or unavailable source.

## 2. Assets and classification

| Asset | Classification / rule |
|---|---|
| Originals, document extracts, chunks, embeddings, citations | Confidential; ACL and retention metadata are mandatory. |
| User identity, role, session and MFA state | Confidential security data; least privilege and revocation required. |
| Passwords, keys, certificates, OAuth secrets | Secret; only approved secret store/files with minimum access; never Git/log/prompt/fixture. |
| Odoo code, feature branches, test outputs | Internal; test data must be synthetic or anonymised. |
| Audit events | Confidential; immutable/append-oriented, access-controlled, secret-free and retention-managed. |
| Worker/connector credential | High-impact secret; device-specific, short lived or rotation-enabled, immediately revocable. |

## 3. Trust boundaries

1. **Browser → public app.** The browser and every request are untrusted until authenticated/authorised server-side.
2. **Untrusted document content → ingestion/RAG.** Documents and filenames are data, not instructions. Their content must not alter prompts, permissions or tools.
3. **Public app → model provider.** Only ACL-filtered, minimum necessary context may cross. External providers are disabled until data-policy and contractual approval.
4. **Public app → Mac mini/file connector.** The central service does not open office connections. Devices authenticate their outbound connections.
5. **Connector → Windows file share.** Connector identity is separately least-privileged and path-limited; backend authorization is not a substitute for source ACL.
6. **Odoo agent → workspace/Odoo.** Generated code and AI output are untrusted; code runs only in disposable constrained test environments.
7. **Admin → production controls.** Critical configuration requires MFA, separation of duties, audit and explicit approval.

## 4. Threat model and required controls

| Threat | Required mitigation |
|---|---|
| Credential stuffing, brute force, session theft | Argon2id/equivalent passwords if local auth, rate limits, secure HttpOnly/SameSite cookies or equivalent token policy, session expiry/revocation, MFA for admins, login audit. |
| Horizontal/vertical privilege escalation | Backend RBAC for every operation; server-side document ACL; role separation; test denied paths; do not trust UI hiding. |
| RAG data leakage | Filter before retrieval/model context; enforce ACL for originals/chunks/embeddings/citations/cache; no document contents in general logs; leakage regression tests. |
| Prompt injection in documents | Treat source as quoted untrusted data; fixed system/tool policy; no document-controlled tool calls; sanitise rendered content; red-team corpus. |
| Malicious uploads | Allowlist MIME/extension, size and archive limits, parser isolation, malware scanning policy, reject malformed inputs, quota and timeout. |
| XSS/CSRF/injection/SSRF | Output encoding, strict CSP suited to chosen frontend, CSRF protections for cookie sessions, parameterised DB access, URL/scheme/host allowlist for service calls, no arbitrary fetch/tool URL. |
| Worker/connector takeover | mTLS or equivalent device identity, short-lived/rotated credentials, outbound-only channel, signed typed jobs, allowlist, resource limits, revoke/disable workflow. |
| Abuse/resource exhaustion | Per-user/IP/device rate limits, quotas, max request/file/context sizes, queue bounds, timeout/cancellation, CPU/RAM/disk limits and backpressure. |
| Secrets in source/logs | `.env`, `secrets/`, `backups/`, audit exports excluded from Git; secrets scanner before publication; redacted structured logs. |
| Odoo-agent code execution | Read-only first; feature branch; disposable workspace; no production DB/credentials; filesystem/network allowlist; no auto merge/deploy. |
| Ransomware/data loss | Tested backups, encrypted/protected off-site policy after approval, restore drills, minimal connector rights, incident procedure. |

## 5. Existing controls confirmed in repka-odoo

- Odoo/PostgreSQL Compose services use digest-pinned images; database is on an internal Docker network.
- Development Odoo port binds loopback only; production Compose exposes only Caddy 80/443.
- `no-new-privileges:true`, healthchecks and log rotation are declared in Compose.
- Caddy config sets HSTS, `X-Content-Type-Options`, Referrer-Policy, Permissions-Policy and removes `Server` response header.
- `scripts/init.sh` generates local secret files with restrictive permissions; `.gitignore` excludes `.env`, `secrets/`, `backups/` and `audit/`.
- The custom container entrypoint copies bind-mounted secrets into a per-container `/run` directory owned by `odoo` with mode `0400`, then executes Odoo and the mock as `odoo`. It supplies database settings through a temporary protected Odoo config file rather than a `--db_password` process argument.
- `backup.sh` validates a PostgreSQL dump, archives filestore and creates checksums.
- Existing demo web app binds `127.0.0.1`, keeps history in memory and runs only registered deterministic DEMO scenarios.

These controls do not provide PWA authentication, RAG ACL, mTLS, audit schema, incident response or production monitoring for the new target.

## 6. Identified security gaps and hardening requirements

1. The new React PWA is test-only and has no authentication, backend, document ingestion or model provider. It must remain synthetic/local until an approved server-side identity and RBAC design is implemented.
2. Odoo configuration has `list_db=False`, but public deployment must additionally verify master-password handling and ensure no default/shared administrative credentials remain.
3. Reported Windows Server and prospective application backups currently rely on local copies only; schedule, retention, RPO/RTO, protected/off-site storage and a restore drill are still unconfirmed. This blocks a document-bearing pilot.
4. No CI, automated dependency/security scanning, central audit log or monitoring is present in the repository.
5. The file-connector service account is permitted in principle, but a manual account lifecycle without a named owner, rotation and immediate-revocation process is not sufficient for deployment.
6. A stakeholder selected local-only AI. External model providers remain prohibited for corporate document content, prompts and embeddings until an explicit policy change is approved.
7. Local inspection found that the Mac mini intended for the worker is not enrolled in MDM, has FileVault off, built-in firewall and stealth mode disabled, and no listed system extensions. Automatic update checking is enabled. Before installing Ollama or a persistent worker, approve a hardening plan or risk acceptance covering device owner, EDR, FileVault, firewall, non-admin runtime account, egress policy, patching and physical-access controls; this audit made no configuration changes.

## 7. Identity and authorisation baseline

Required roles for the new application:

- `employee`
- `pilot_user`
- `knowledge_admin`
- `odoo_developer`
- `security_admin`
- `system_admin`

The final mapping depends on the verified IdP/Odoo design. Roles must not automatically inherit broad document access. `knowledge_admin` manages sources and ACL policy but should not automatically become `system_admin`; `security_admin` reviews audit and revokes access but should not administer business content; `odoo_developer` has no production deployment permission.

MFA is mandatory for administrative roles. Deactivation must revoke sessions and worker/connector grants associated with the user/device where relevant.

## 8. Audit, logging and monitoring requirements

Log at minimum:

- login success/failure, MFA enrolment/use, session issue/revoke;
- user/role/source/ACL changes;
- upload, ingest, index, document read/download and retrieval decision;
- model/provider/task invocation metadata, latency/status and worker availability;
- Odoo agent plan, branch, validation, PR and requested privileged action;
- administration, credential issuance/revocation and incident events.

Do not log passwords, bearer tokens, private keys, raw documents, full prompts or model output by default. Audit access must itself be audited. Metrics and health checks must distinguish unavailable AI/connector from successful completion.

## 9. Incident response and credential revocation

1. **Detect and contain:** disable affected user/device/source; revoke sessions, tokens and certificates; pause affected queues/ingest.
2. **Preserve evidence:** protect relevant audit metadata and logs; do not copy secrets or document contents into issue trackers.
3. **Assess scope:** identify users, documents, tasks and credentials affected using audit records.
4. **Eradicate and recover:** rotate credentials, patch root cause, revalidate source ACL, restore verified backup only when required.
5. **Notify and learn:** follow LM GROUP approved notification process; record timeline, decision and controls added.

No incident workflow may send email, alter production data, or delete source files automatically without authorised human approval.

## 10. Security acceptance gates

Before pilot: independent tests of authentication, MFA, session revocation, privilege escalation, CSRF/XSS/SSRF, abuse limits, secret scanning and public port exposure.

Before document rollout: cross-user RAG leakage tests including history/cache/embedding/citation/log routes, prompt injection corpus, malformed upload tests and source ACL tests.

Before production expansion: restore drill, worker/connector outage/deduplication tests, credential revocation rehearsal, vulnerability review and administrator approval.
