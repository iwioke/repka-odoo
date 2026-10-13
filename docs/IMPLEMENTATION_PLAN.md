# План реализации LM GROUP

**Статус:** план после аудита; производство, DNS, firewall и Odoo.sh не изменяются без отдельного согласования.
**Принцип:** небольшие проверяемые шаги, отдельная feature-ветка для кода, human-in-the-loop для всех критичных действий.

## 1. Зависимости, которые блокируют реализацию

| Данные/решение | Нужны для | Ответственный |
|---|---|---|
| Версия, edition, Git workflow и environments Odoo.sh | Любые модули/тесты Odoo agent | Владелец Odoo.sh / администратор |
| VPS/облако, домен, DNS и TLS ownership | Public PWA/backend | Администратор / руководитель |
| IdP/SSO либо corporate email domain для пилота | Выбор auth и MFA flow | Администратор / HR/IT |
| Политика обработки документов и внешних LLM | RAG и provider selection | Руководитель / security / legal |
| Выбранные папки, ACL и сервисная учётная запись | File connector | Владелец файлового сервера |
| Mac mini availability и outbound policy | AI worker / Ollama benchmark | Офисный IT |
| RPO/RTO и retention | Backup/restore и мониторинг | Администратор / владелец данных |

### Статус после первого раунда вопросов

- **Подтверждённое направление:** local-only AI; проверенный Mac mini M4/16 GB на macOS 26.3 может запускать outbound-only `launchd` worker; доступно 185 GiB на root volume; Ollama ещё не установлен.
- **Не использовать:** существующий личный VPS, на котором работает VPN. Отдельный VPS может рассматриваться только через утверждённую закупку/выделение и не покупается автоматически.
- **Кандидат домена:** `ai.llclmgroup.com`; отдельный домен не нужен технически, если DNS-подрядчик подтверждает создание/делегирование поддомена и TLS-процедуру.
- **Оdoo.sh:** stakeholder сообщил Odoo Community `18.0-20251222`, совпадающую с репозиторием; требуется подтвердить проект, branches, module set, backup/rollback и test workflow в интерфейсе Odoo.sh.
- **Windows file server:** connector и индексирование файлового сервера исключены из Stage 1. Windows Server ports/ACL/test folders и service-account owner/revocation остаются обязательными gate для Stage 5.
- **Критические блокеры Stage 1:** IdP/SSO или безопасный pilot identity flow, параметры нового public host, DNS/TLS request process, RPO/RTO and restore evidence.
- **Backup риск:** сообщено только о локальных копиях. До пилота с документами необходимы утверждённые retention, off-site/защищённое хранение и restore drill.

## 2. Этап 0 — аудит

### Выполнено в репозитории

- проверены `git status` и ветка `main` до собственных изменений;
- установлен факт: текущий repository target — Odoo CE `18.0-20251222`;
- изучены Compose, Caddy, конфигурация, backup, addons, детерминированные AI demos и UI reference;
- сформированы документы архитектуры, безопасности, совместимости, инфраструктурного аудита и решений;
- подготовлен список вопросов администратору.

### Критерий завершения

Документированы факты, unknowns, риски, plan и Odoo-version mismatch. Код приложения, production и сетевые порты не менялись. Для перехода к Этапу 1 обязательны ответы хотя бы о VPS/DNS/IdP и Odoo.sh.

## 3. Этап 1 — test-only каркас до пилота

### Test-only scope decision

До решения по public pilot разрешён только `repka_test` с синтетическими данными и отдельный browser-only PWA shell в `apps/lm-group-pwa/`. Windows file connector, RAG по корпоративным документам, Ollama, Mac mini worker и production/Odoo.sh deployment не входят в этот этап. Отдельный public test host допускается только после ручной покупки отдельного VPS/домена и выполнения инструкции `docs/TEST_ENVIRONMENT_SETUP.md`.

### Scope

- создать отдельную feature branch;
- выбрать размещение public tier и identity model только после согласования;
- создать web/PWA shell, login/logout, server-side RBAC, сессии и audit events;
- завести отдельные персональные pilot accounts;
- включить MFA для administrator roles;
- развернуть approved development/staging среду через HTTPS.

### Повторно используемые элементы

- Caddy and only-80/443 deployment pattern из существующего production Compose;
- secrets-as-files and pinned-image discipline;
- Odoo `auth_totp*` как кандидат, если Odoo выбран identity shell;
- UI status/token patterns из `iwiqoVPN`, без VPN-кода.

### Criteria of Done

1. пилотные пользователи входят под индивидуальными учётными записями;
2. RBAC проверяется backend на каждом API action;
3. деактивированный пользователь не использует старую сессию;
4. MFA защищает administration;
5. аудируются auth, privilege changes и administrative actions;
6. нет общих аккаунтов, plaintext passwords, public DB/Redis/admin API;
7. проверены access-control, session expiry/revocation, CSRF/XSS и rate limiting.

### Rollback

Отключить feature route/feature flag, деактивировать pilot accounts, отозвать sessions/credentials. Не менять Odoo production modules или network rules в рамках rollback.

## 4. Этап 2 — документы и ACL-aware RAG

### Scope

- утвердить маленький набор тестовых документов и data-owner;
- определить допустимые MIME types, size limits, antivirus/inspection behavior и retention;
- внедрить ingestion, metadata ACL, citation/provenance, retrieval filtering and audit;
- подготовить corpus для prompt injection и cross-user leakage;
- определить approved embedding/model provider after license/privacy review.

### Criteria of Done

1. unprivileged user не получает originals, chunks, embeddings, cache entries, citations или logs чужого документа;
2. ACL фильтрация происходит до model context;
3. ответы содержат проверяемые citation; при недостатке источника модель не выдумывает данные;
4. injection в DOCX/PDF/TXT/filename не меняет system instructions и не запускает tool;
5. oversized/corrupt/unsupported uploads safely reject;
6. все операции ingest/read/download отображаются в audit.

### Rollback

Остановить ingestion jobs, отозвать source connector credential, удалить только согласованные derived index data по retention procedure. Исходные документы и production shares не удаляются автоматически.

## 5. Этап 3 — генерация черновиков документов

### Scope

- versioned approved templates;
- structured approved inputs and missing-data markers;
- draft generation only; optional DOCX/PDF export after format requirements are confirmed;
- human confirmation before send/sign.

### Criteria of Done

- UI явно маркирует результат как «Черновик — требуется проверка человеком»;
- обязательные поля, источники и пропуски видны пользователю;
- нет auto-send, e-sign или публикации;
- templates and generated drafts obey ACL/retention;
- audit records template version, input provenance and approver.

## 6. Этап 4 — Mac mini AI worker

### Scope

- benchmark an approved model class on actual 16 GB Mac mini (Russian quality, latency, RAM, license);
- install outbound-only worker with supervised restart;
- implement typed job allowlist, device identity, mTLS/rotating credentials, heartbeat and bounded queue;
- integrate availability status in UI.

### Criteria of Done

- no inbound public port to Mac mini or Ollama;
- worker refuses unknown job types, arbitrary URLs, shell commands and model pull requests;
- duplicate job delivery is idempotent;
- UI accurately shows offline/timeout/degraded status;
- test: internet interrupted, worker restarted, queue retried and credential revoked.
- before installation: approved Mac mini hardening plan or explicit risk acceptance. Current audit finds no MDM enrollment, FileVault off, built-in firewall disabled and no listed system extensions; this is a Stage 4 gate, not a configuration change authorised by this document.

## 7. Этап 5 — file-server connector

### Scope

- start only with 2–3 administrator-approved folders;
- create a minimal-privilege read-only service account;
- implement outgoing connector, file/path allowlist, source-side ACL mapping and audit.

### Criteria of Done

- no SMB/RDP/SSH exposure to internet;
- connector cannot enumerate arbitrary shares or read outside approved paths;
- denied user cannot receive metadata, chunk, citation or content;
- connector handles duplicate events, file replacement and disconnection safely;
- administrator signs off firewall, account, antivirus/EDR and backup impact.

## 8. Этап 6 — Odoo Development Agent

### Scope

- verify Odoo.sh target version/edition and test process;
- begin read-only: change proposal, affected files, risk and test list;
- create feature branch only after human approval;
- run manifest/Python/XML/dependency checks and disposable DB tests;
- create PR only after checks pass.

### Criteria of Done

- no production credentials/database access;
- code execution is isolated with resource, filesystem and network limits;
- report includes diff, rationale, tests, result, risks and rollback;
- merge/deploy remains a human-approved action;
- schema, access, financial or destructive change requires separate approval.

## 9. Этап 7 — пилот и расширение

### Scope

- approved pilot participants and office networks;
- security, availability, restore, load and usability tests;
- incident-response rehearsal and support procedure;
- gradual wave-based rollout.

### Criteria of Done

- critical audit/security findings resolved or accepted in writing;
- backup restore drill passes against approved RPO/RTO;
- support team has runbook for user deactivation, connector/worker outage and credential revocation;
- usage/load measurements justify any scale-out;
- new user cohorts are approved individually; no automatic company-wide enablement.

## 10. Verification baseline

The repository specifies these checks for a later Docker-capable development environment:

```bash
# Compose syntax
 docker compose -f compose.yaml -f compose.dev.yaml config --quiet
 ODOO_DOMAIN=erp.example.com docker compose -f compose.yaml -f compose.prod.yaml config --quiet

# New PWA checks (after the shell is added)
 npm run lint
 npm run build

# Isolated Odoo module test
 docker compose -f compose.yaml run --rm --no-deps odoo odoo \
   -d repka_test -i <module> --without-demo=all \
   --test-enable --test-tags=/<module> --stop-after-init
```

Run them only with no production data or secrets. Docker is not installed in the environment used for the initial audit; Compose validation and Odoo tests remain pending there.
