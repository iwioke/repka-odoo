# Architecture: Repka AI Automation app

## Confirmed facts
`ai_automations/scenarios/` contains four Python `run.py` entry points, README files and synthetic JSON examples. `.internal/engine.py` owns the explicit `FUNCTIONS` registry and rejects live mode. The Markdown catalogue includes four DEMO rows and 19 BLOCKED rows; the future README describes the latter. There is no existing standalone frontend build system in this repository.

## Decisions for the local demo
Use a loopback-only Python stdlib HTTP server and static HTML/CSS/JS. Server reads the Markdown catalogue, future table and scenario READMEs; it intersects discovered scenario directories with `engine.FUNCTIONS` and checks expected fixed entry points. POST `/api/run` accepts only a registered slug and DEMO mode, optionally a JSON object instead of the default example, then invokes the fixed run.py with `subprocess.run`, argv list, bounded time/output and no shell. Custom input is written to a temporary file removed after execution. Only a bounded generic validation error is shown on failure. JSON results come straight from the scenario stdout. Origin and JSON content type are checked for POST. History stores only slug, mode, status, timestamp and duration in a bounded in-memory list; never input or output.

## Boundaries and assumptions
No new LIVE mode or Odoo integrations. The front end renders untrusted metadata and results as text, never HTML. Future ideas cannot be run. The process binds `127.0.0.1`; remote hosting, authorization, CSRF policy behind proxies and multi-user history require separate design. Production permissions, infrastructure, monitoring, personal-data processing and retention policy are unresolved; local synthetic demos do not require them.
