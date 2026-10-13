# Infrastructure audit — LM GROUP

**Date:** 2026-10-13
**Scope:** repository evidence and supplied business context only. No hosts, DNS zones, firewalls, Odoo.sh instances or production systems were accessed or changed.

## 1. Confirmed facts

| Area | Confirmed fact | Evidence / source |
|---|---|---|
| Repository | Main codebase is `repka-odoo`; UI reference is `iwiqoVPN`. | Approved project brief; repository audit. |
| Existing stack | Odoo CE `18.0-20251222`, PostgreSQL 16 and Caddy are modelled in Docker Compose. | `Dockerfile`, Compose files, `AGENTS.md`. |
| Public proxy pattern | Existing production Compose publishes Caddy ports 80/443; Odoo and DB remain in Docker networks. | `compose.prod.yaml`, `compose.yaml`. |
| Development exposure | Odoo development port binds `127.0.0.1`. | `compose.dev.yaml`. |
| AI demos | Existing AI work is deterministic/synthetic and local/mock only. | `ai_automations/README.md`, mock service. |
| Office equipment | A Windows Server with public IP is used as file server; a 16 GB M4 Mac mini is considered for local AI. | Supplied project brief. |
| Required connectivity | Employee access must be ordinary HTTPS from Belarus offices, with no VPN requirement. | Supplied project brief. |
| Office node rule | Do not rely on inbound internet access to Mac mini or the file server. | Supplied project brief. |

## 2. Stakeholder-reported information awaiting independent verification

The following information was supplied during the initial question round. It is recorded as a report, not as independently verified infrastructure state:

- an existing personal VPS is used for VPN; it is excluded from the LM GROUP public-tier design and must not be repurposed;
- a separately purchased VPS may be considered, but only after an approved specification, jurisdiction, budget, backup, administration and rollback plan; no purchase is authorised by this audit;
- `llclmgroup.com` is a candidate corporate domain; DNS is managed by an external contractor. A separate domain is not technically required if the contractor can delegate/create `ai.llclmgroup.com`; subdomain authority and the exact TLS request process remain unconfirmed;
- each employee has an individual Mac profile; a possible connection through a Windows image/server was reported, but whether this is RDP, VDI or another system — and its identity lifecycle — is unknown;
- Windows Server version, EDR/antivirus, public ports, firewall owner, pilot folders and ACLs are unknown. The Windows connector is explicitly deferred from the early MVP and is not a Stage 1 dependency;
- a separate read-only connector service account is allowed in principle, but the manual creation, rotation, immediate-revocation procedure and accountable owner are not established;
- Windows Server and the reported new-app backup posture currently rely on local copies only; no RPO, RTO, retention, off-site copy or restore-test evidence was supplied;
- local inspection confirms the current host is a Mac mini `Mac16,10` with Apple M4, 16 GB RAM, macOS 26.3 and 185 GiB available on the root volume. It is not enrolled in MDM, Ollama is not installed, FileVault is off, the built-in macOS firewall and stealth mode are disabled, and no system extensions were listed; automatic update checking is enabled. The Mac mini is allowed to run an outbound-only `launchd` worker, but an approved hardening plan, EDR verification, egress restrictions and worker ownership procedures are required before installation;
- MVP policy is local-only AI: corporate document content, prompts and embeddings must not be sent to external AI providers;
- the stakeholder reports target Odoo.sh is Odoo `18.0-20251222` Community Edition, matching the repository target. Its project, branch/environment model, module set, backup/rollback and test workflow remain to be inspected in Odoo.sh.

## 3. Explicitly unknown facts

The following must not be guessed:

- whether a separate VPS/cloud account already exists, its jurisdiction/specifications, access model and backup policy;
- corporate domain, available subdomain, DNS provider, DNS-change authority and certificate issuance constraints;
- Windows Server version/patch level, open ports, perimeter firewall rules, EDR/antivirus and backup status;
- corporate directory/IdP/SSO, Mac provisioning/deprovisioning method and pilot e-mail domain;
- approved file-server folders, their NTFS/share ACLs and permitted service-account procedure;
- Mac mini current software, Ollama state, egress policy, persistent-service approval and reliability;
- target Odoo.sh project/version/edition/branch/environment/test/backup configuration;
- legal/security permission to transfer documents to any external AI provider;
- records-retention, backup retention, RPO/RTO and incident-notification requirements.

## 3. Questions for the responsible administrator

Do not send passwords, API tokens, private keys, production exports or real documents in chat or Git. A factual response or secure out-of-band access process is sufficient.

### Public hosting, domain and DNS

1. Is there an existing VPS/cloud server suitable for a separate public application tier? Provide provider, country/region, operating system, available CPU/RAM/disk, backup coverage and administration owner.
2. If not, is an approved VPS procurement process available? No purchase should be made by this project without approval.
3. What corporate domain and candidate subdomain may the pilot use? Who owns DNS changes?
4. Can inbound 80/443 be assigned to a new public host, and is Caddy/ACME HTTP certificate issuance permitted? If not, what approved certificate method must be used?

### Identity and pilot users

5. How are employee Mac accounts provisioned/deprovisioned today: Active Directory, Entra ID, Google Workspace, Apple Business Manager, another IdP, or local accounts?
6. Is SSO/OIDC/SAML available for a pilot? If not, what is the verified corporate email domain and approved password-reset/MFA process?
7. Who approves the pilot group and which role owners administer knowledge, security and system settings?

### Windows file server and offices

8. What Windows Server release/patch level and EDR/antivirus are in use? Who approves changes?
9. What inbound ports are currently exposed on its public IP, and which firewall owner can confirm them? Do not change rules as part of this request.
10. Which two or three test folders are approved for the pilot, who owns them, and what NTFS/share ACLs apply?
11. May a separate minimal-privilege read-only service account be created for an outbound connector? What procedure governs account expiry/revocation?
12. What backup product, schedule, retention and last successful restore test protect the file server?

### Mac mini and local AI

13. Is the Mac mini permitted to run a persistent `launchd` worker that only makes outbound TLS connections?
14. Is Ollama installed already? What local model, storage capacity, MDM/EDR and outbound network restrictions exist?
15. Is there an approved maintenance/restart owner and expected availability window for this node?

### Odoo.sh and data policy

16. What are exact Odoo.sh version, edition, project Git repository, Development/Staging/Production branches and test/deployment workflow?
17. Which custom/OCA modules are installed in the target Odoo.sh environment, and are migrations/backups verified?
18. May corporate document contents, embeddings or prompts leave company-controlled infrastructure? If yes, which jurisdictions/providers/contracts are approved? If no, confirm local-only model policy.
19. What RPO/RTO, retention and deletion rules apply to the new application, document derivatives, audit events and backups?

## 4. Preliminary hosting recommendation (not approved procurement)

If no approved public tier exists, use a dedicated VPS/cloud instance for the PWA/backend/broker rather than reusing the Windows file server. Initial pilot sizing is a proposal only:

- 2–4 vCPU;
- 8 GB RAM;
- 80 GB encrypted SSD, with growth monitored;
- supported Linux LTS, automatic security updates through an approved process;
- EU/other approved jurisdiction after company data-policy review;
- only 443/TCP and, if approved for ACME, 80/TCP exposed;
- restricted administration path, monitored backups and documented restore procedure.

This is intentionally not a purchase instruction and does not require a second Mac mini or cluster before pilot measurements show a need.

## 5. Required network stance

| System | Allowed connectivity | Explicitly disallowed in the target pilot |
|---|---|---|
| Employee browser | HTTPS to approved corporate domain | VPN as prerequisite, direct access to office nodes. |
| Public application host | HTTPS public ingress; private service networks | Direct public DB/Redis/Ollama/internal API exposure. |
| Mac mini | Outbound TLS/mTLS to approved backend/broker | Public inbound Ollama 11434, SSH/API exposure, arbitrary remote shell. |
| Windows file server / connector | Outbound TLS/mTLS from connector; local access to approved folders | Public SMB 445, RDP 3389, file share or connector inbound API. |
| Odoo/Odoo.sh | Approved HTTPS/API only after workflow confirmation | Production database access, arbitrary SQL or automated deploy. |

## 6. Audit conclusion

Repository-level infrastructure controls are promising for local Odoo development, but they do not reveal LM GROUP's live network, identity, file-server, VPS or Odoo.sh state. The administrator responses above are the gate for selecting a safe deployment topology and for moving beyond architecture/audit documents.
