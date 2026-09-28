# Repka AI Automation

Local catalogue and launcher for the existing `ai_automations/` scenarios. The dashboard shows all catalogue entries and runs only registered DEMO scenarios against synthetic JSON. No ML/LLM, OCR, live Odoo connection or production actions are provided.

## Requirements and start

Python 3.9+; no pip, Node or Docker required. From the repository root:

```sh
python3 ai_automations/app/server.py
```

Open `http://127.0.0.1:8765/` on the same machine. Optional port: `python3 ai_automations/app/server.py --port 8766`. The server binds only to 127.0.0.1 and has no authentication: do not expose it through a proxy or public network. Stop with Ctrl+C.

## Architecture and integration

`server.py` reads `catalog/AI_AUTOMATIONS_CATALOG.md` and `catalog/future/README.md`; runnable scenario details are read from each scenario's `README.md`. It discovers folders under `scenarios/`, but only folders present in `.internal/engine.py`'s `FUNCTIONS` registry with `run.py` and `example_input.json` can run. The dashboard uses `/api/automations`, `/api/run`, `/api/history`. The backend passes fixed arguments to the registered `run.py` without a shell; default input is the checked-in synthetic example. An optional custom JSON object is written to a temporary file and deleted immediately after execution. Input is limited to 64 KB, runtime to 12 seconds and output to 1 MB. Inputs and results are not kept in history; only the last 100 run metadata records are held in server memory and disappear on restart. No credentials are sent to the browser.

## Adding an automation

Add a folder in `ai_automations/scenarios/` with `README.md` using the same `##` section headings as existing demos, `run.py`, `example_input.json` and tests. Register its slug in `.internal/engine.py`'s `FUNCTIONS` (and CLI dispatcher), and add a `DEMO` row to the catalogue with a name matching the README heading (before the optional ` / ` suffix). The app discovers it on the next request without frontend edits. Future ideas require a `BLOCKED` catalogue row and a matching row in `catalog/future/README.md`; they are shown but cannot be launched. Only add real modes and describe real outputs.

## DEMO / LIVE and troubleshooting

DEMO uses deterministic rules and synthetic input. LIVE is not implemented and the API rejects it; there is no Odoo write path. Custom JSON must match the shape of the scenario's displayed example. For input errors compare fields with `example_input.json`; the UI deliberately does not show raw stderr or secrets. If the catalogue is unavailable, check README/catalogue rows and the Python server console. If a port is in use, choose another `--port`. To verify the API, UI assets and all four runners:

```sh
python3 -m unittest discover -s ai_automations/app/tests -v
python3 -m unittest discover -s ai_automations/.internal/tests -v
```
