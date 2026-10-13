# Architecture Decision Record — LM GROUP

**Status legend:** `Accepted` means a Stage 0 guardrail or repository fact, not that deployment has been approved. `Pending` requires evidence and authorised approval.

## ADR-001 — Public application tier is separate from the Windows file server

- **Status:** Accepted as an MVP guardrail.
- **Context:** Windows Server is an existing critical file server with public IP; virtualization is currently unavailable. The project requires a public web app.
- **Decision:** Do not place public frontend/backend, Redis, PostgreSQL, Ollama, RDP, SSH or SMB on that server in the first version. If an existing approved public tier is unavailable, evaluate a dedicated VPS/cloud server.
- **Consequences:** Hosting/DNS/backup/administration must be confirmed before implementation. This does not authorise purchasing infrastructure.

## ADR-002 — No VPN or inbound office-node connections

- **Status:** Accepted.
- **Context:** Users work from different offices and must use ordinary HTTPS; Mac mini and file server are not to be exposed.
- **Decision:** Browser access goes to a corporate HTTPS domain. Mac mini and file connector establish outbound authenticated TLS connections to a public broker/backend. Use mTLS or equivalent device identity plus short-lived/rotatable credentials.
- **Consequences:** No WireGuard/Tailscale/ZeroTier tunnel is introduced as an architecture dependency. No public Ollama, SMB, RDP, PostgreSQL, Redis, SSH or internal API endpoint is required.

## ADR-003 — Remove the legacy AI/automation demo stack

- **Status:** Accepted and executed for the test branch.
- **Context:** The repository contained deterministic scenarios, a Python demo UI, a document-check mock and related Odoo addons that do not match the new independent application direction.
- **Decision:** Remove their executable code, Odoo integration, Compose wiring, tests and feature documentation. Preserve only the scenario catalog as reference-only Markdown and move generic Odoo automation audit tools into `tools/legacy_automation_audit/`.
- **Consequences:** `repka_suite` no longer depends on the removed addons. The new PWA does not reuse the old runtime or connect to Odoo until a later approved integration design exists.

## ADR-004 — Local Ollama is the primary candidate, but model choice is evidence-based

- **Status:** Accepted as default direction; model selection pending.
- **Context:** A 16 GB M4 Mac mini is proposed for local AI; data-policy permission for external providers is unknown.
- **Decision:** Design a provider abstraction. Keep external providers disabled by default. Evaluate candidate local models on the actual device for Russian-language quality, latency, RAM, disk, licensing and availability before naming a production model.
- **Consequences:** No model is downloaded, exposed or benchmarked against corporate documents during Stage 0. UI must communicate local-AI outage clearly.

## ADR-005 — Document ACL is enforced before retrieval and model context

- **Status:** Accepted.
- **Context:** RAG answers can leak data through chunks, embeddings, citations, cache, history or logs.
- **Decision:** Source ACL metadata is mandatory. Backend filters at document/chunk level before retrieval context is constructed, and checks access again for originals/downloads/citations.
- **Consequences:** The interface cannot rely on model instructions to hide documents. Cross-user leakage and prompt injection become mandatory acceptance tests.

## ADR-006 — Auth architecture remains pending identity audit

- **Status:** Pending.
- **Context:** Corporate directory/SSO/MDM state is unknown. The repo includes Odoo `auth_totp*` but does not prove pilot identity architecture.
- **Decision:** Do not choose Odoo-native, IdP/SSO or separate application authentication until administrator evidence is received. If built-in pilot authentication is selected, use per-user accounts, Argon2id/equivalent, rate limits, reset flow and MFA for administrators.
- **Consequences:** No pilot account or RBAC implementation starts until identity ownership and user lifecycle are known.

## ADR-007 — Odoo.sh compatibility is a separate verification gate

- **Status:** Pending.
- **Context:** This Docker repository targets Odoo CE `18.0-20251222`; target Odoo.sh version, edition and workflow are unknown.
- **Decision:** Treat repository and target Odoo.sh compatibility as independent. Work read-only until Odoo.sh details are verified. Any future Odoo change uses feature branch, isolated test data, automated validation, diff/report and human-approved PR/merge/deploy.
- **Consequences:** No claim of Odoo.sh readiness and no module deployment based solely on README/version strings.

## ADR-008 — Use iwiqoVPN only as UI/UX reference

- **Status:** Accepted.
- **Context:** The reference is a SwiftUI WireGuard macOS client; LM GROUP needs a web/PWA, not a VPN client.
- **Decision:** Reuse only abstract design lessons: theme token structure, status indicators, restrained motion, compact cards and progressive disclosure. Adapt colours to a professional LM GROUP identity.
- **Consequences:** Exclude VPN code, WireGuard models, `wg-quick`, sudoers, Telegram config, native entitlements and network/business logic.

## ADR-009 — Public deployment waits for infrastructure and recovery evidence

- **Status:** Pending.
- **Context:** Repository backups validate local dump/archive generation, but no live retention, off-site copy, RPO/RTO or restore drill is confirmed.
- **Decision:** No public pilot launch before approved host, TLS/DNS, backup retention and restore test are documented.
- **Consequences:** Stage 1 may progress in isolated local development; pilot rollout remains blocked until evidence is accepted.

## ADR-010 — Human approval gates all critical actions

- **Status:** Accepted.
- **Context:** Document sending/signing, production deployment, Odoo data/schema/access changes, financial operations and infrastructure changes are consequential.
- **Decision:** Generated content is draft-only; Odoo agent is proposal/PR-oriented; no automatic merge, deployment, email, signature, data deletion or infrastructure change.
- **Consequences:** Audit records must capture requester, approver, action, scope and outcome without storing secrets or unnecessary document content.

## ADR-011 — MVP document processing is local-only

- **Status:** Accepted as stakeholder direction; implementation details pending.
- **Context:** The stakeholder stated that corporate document contents, prompts and embeddings may use local AI only.
- **Decision:** External AI/model providers are disabled for the MVP. Mac mini/local-model design remains subject to device inventory, model licensing, quality and security benchmarking.
- **Consequences:** Do not configure cloud AI credentials, send corporate context to external APIs, or claim cloud-provider fallback. Local AI unavailability must be visible to users.

## ADR-012 — Do not reuse the existing personal VPN VPS

- **Status:** Accepted.
- **Context:** The available existing VPS is used for VPN, which is excluded from the LM GROUP architecture.
- **Decision:** Do not place the public LM GROUP application on that host and do not couple the application to its VPN services. A separate host may be evaluated only through an approved procurement/allocation process.
- **Consequences:** Provider, jurisdiction, size, administration, DNS/TLS, backups and recovery for any new public tier remain approval gates; no purchase or provisioning action is authorised.

## ADR-013 — Windows file connector is deferred from the early MVP

- **Status:** Accepted as an MVP scope boundary.
- **Context:** Windows Server version, firewall, folders, ACLs, backup recovery and connector service-account lifecycle are not yet established. The stakeholder asked whether early delivery can proceed without it.
- **Decision:** Stages 0–1 may deliver architecture and an approved PWA/auth skeleton without a connector or access to the Windows file server. Stage 2 may use only separately approved synthetic or manually uploaded non-sensitive test material. No corporate file-server search or RAG is available until Stage 5 gates pass.
- **Consequences:** This lowers initial infrastructure risk but does not remove the Windows audit requirement for later document discovery.

## ADR-014 — Prefer a subdomain before acquiring a separate domain

- **Status:** Pending DNS/TLS confirmation.
- **Context:** `llclmgroup.com` is a candidate corporate domain managed by an external contractor; the stakeholder believes a new domain may be required.
- **Decision:** Request `ai.llclmgroup.com` first. A separate domain is not technically necessary if the contractor can create/delegate the record and complete the approved TLS process.
- **Consequences:** Superseded by ADR-015 after the stakeholder selected a separate domain for the test host.

## ADR-015 — Separate domain for the public test host

- **Status:** Accepted as test-only direction; purchase and configuration are pending human action.
- **Context:** The stakeholder chose a separate domain because transferring a DNS request to the current contractor is not feasible.
- **Decision:** If public test access is required, use a newly acquired LM GROUP-owned domain and a `test.<new-domain>` record pointing only to a separate test VPS. Do not use the Windows Server, Mac mini or personal VPN VPS.
- **Consequences:** The domain registrar account must be company-owned with MFA, a renewal owner and controlled DNS access. This direction permits planning and instructions, not automated purchase, DNS changes or deployment.
