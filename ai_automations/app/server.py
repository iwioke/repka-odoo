import argparse
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parent
sys.path.insert(0, str(ROOT / ".internal"))
from engine import FUNCTIONS

MAX_INPUT = 64 * 1024
MAX_OUTPUT = 1024 * 1024
SECTIONS = {
    "what": "Что это", "simplifies": "Какую проблему решает",
    "how": "Как работает", "data": "Какие данные использует",
    "processing": "Что делает AI", "output": "Результат",
    "pros": "Плюсы", "cons": "Минусы", "risks": "Риски",
    "run_instructions": "Как запустить", "architecture": "Техническая архитектура",
    "limitations": "Ограничения",
}


def rows(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\|\s*\d+\s*\|", line):
            yield [cell.strip() for cell in line.strip().strip("|").split("|")]


def sections(path):
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").split(" — ")[0]
    blocks = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    content = {blocks[i]: blocks[i + 1].strip() for i in range(1, len(blocks) - 1, 2)}
    return title, {key: content.get(label, "") for key, label in SECTIONS.items()}


def catalog():
    future = {}
    for line in (ROOT / "catalog/future/README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and not line.startswith("| Идея") and not line.startswith("|---"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 5:
                future[cells[0].casefold()] = cells
    discovered = {}
    for folder in (ROOT / "scenarios").iterdir():
        if folder.is_dir() and folder.name in FUNCTIONS and (folder / "README.md").is_file():
            name, detail = sections(folder / "README.md")
            discovered[name.casefold()] = (folder, name, detail)
    result = []
    for cells in rows(ROOT / "catalog/AI_AUTOMATIONS_CATALOG.md"):
        if len(cells) != 6:
            raise ValueError("Invalid catalogue row")
        _, title, category, _, _, status = cells
        if status == "DEMO":
            match = discovered.get(title.split(" / ")[0].casefold())
            if not match:
                raise ValueError("Missing scenario README")
            folder, name, detail = match
            slug = folder.name
            runnable = (folder / "run.py").is_file() and (folder / "example_input.json").is_file()
            if not runnable:
                raise ValueError("Unregistered demo scenario")
            example = json.loads((folder / "example_input.json").read_text(encoding="utf-8"))
            modes = ["DEMO"]
        elif status == "BLOCKED":
            name = title
            slug = "future-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            cells_future = future.get(title.casefold())
            if not cells_future:
                raise ValueError("Missing future scenario details")
            _, problem, logic, blocker, risk = cells_future
            detail = dict(what=problem.split(";")[0], simplifies=problem.split(";")[0],
                          how=logic, data=problem, processing=logic, output=logic,
                          pros="", cons=blocker, risks=risk)
            example = None
            modes = []
            runnable = False
        else:
            raise ValueError("Unknown scenario status")
        result.append(dict(slug=slug, name=name, category=category, status=status,
                           modes=modes, runnable=runnable, description=detail["what"],
                           tags=[title, slug.replace("_", " ").replace("-", " ")],
                           details=detail, example_input=example))
    return result


def execute(item, custom_input):
    command = [sys.executable, str(ROOT / "scenarios" / item["slug"] / "run.py"), "--mode", "demo"]
    if custom_input is not None:
        with tempfile.TemporaryDirectory(prefix="repka-demo-") as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(custom_input, ensure_ascii=False), encoding="utf-8")
            command.extend(["--input", str(path)])
            return invoke(command, item["slug"])
    return invoke(command, item["slug"])


def invoke(command, slug):
    try:
        completed = subprocess.run(command, capture_output=True, timeout=12, cwd=ROOT)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Automation timed out. Try a smaller input.") from exc
    except OSError as exc:
        raise ValueError("Automation could not start. Check the local installation.") from exc
    if completed.returncode:
        raise ValueError("Automation rejected the input. Check the JSON fields against the example.")
    if len(completed.stdout) > MAX_OUTPUT:
        raise ValueError("Automation output is too large to display.")
    try:
        payload = json.loads(completed.stdout)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Automation returned an invalid result.") from exc
    if not isinstance(payload, dict) or payload.get("scenario") != slug or payload.get("mode") != "DEMO":
        raise ValueError("Automation returned an unexpected result.")
    return payload


def create_server(port=8765):
    history = deque(maxlen=100)
    lock = threading.Lock()
    slots = threading.BoundedSemaphore(2)

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/automations":
                try:
                    self.respond(200, {"automations": catalog()})
                except (OSError, ValueError, json.JSONDecodeError):
                    self.respond(500, {"error": "Catalogue is unavailable."})
            elif self.path == "/api/history":
                with lock:
                    self.respond(200, {"runs": list(history)})
            else:
                assets = {"/": ("index.html", "text/html; charset=utf-8"),
                          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                          "/style.css": ("style.css", "text/css; charset=utf-8")}
                if self.path not in assets:
                    self.respond(404, {"error": "Not found"})
                    return
                filename, content_type = assets[self.path]
                body = (APP / filename).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

        def do_POST(self):
            if self.path != "/api/run":
                self.respond(404, {"error": "Not found"})
                return
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin", "")
            local_host = r"(?:127\.0\.0\.1|localhost):\d{1,5}"
            if not re.fullmatch(local_host, host) or not re.fullmatch("http://" + local_host, origin) or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self.respond(403, {"error": "Invalid request origin or content type."})
                return
            try:
                size = int(self.headers.get("Content-Length", ""))
            except ValueError:
                size = 0
            if size <= 0 or size > MAX_INPUT:
                self.respond(413, {"error": "Input must be at most 64 KB."})
                return
            try:
                request = json.loads(self.rfile.read(size))
                if not isinstance(request, dict):
                    raise ValueError("Invalid request")
            except (UnicodeError, json.JSONDecodeError, ValueError):
                self.respond(400, {"error": "Invalid JSON request."})
                return
            slug = request.get("slug")
            mode = request.get("mode")
            if not isinstance(slug, str) or mode != "DEMO":
                self.respond(400, {"error": "Only registered DEMO automations can run."})
                return
            try:
                item = next((item for item in catalog() if item["slug"] == slug), None)
            except (OSError, ValueError, json.JSONDecodeError):
                self.respond(500, {"error": "Catalogue is unavailable."})
                return
            if not item or not item["runnable"]:
                self.respond(400, {"error": "This automation is not available to run."})
                return
            custom_input = request.get("input")
            if custom_input is not None and not isinstance(custom_input, dict):
                self.respond(400, {"error": "Input must be a JSON object."})
                return
            if not slots.acquire(blocking=False):
                self.respond(429, {"error": "Other automations are running. Retry shortly."})
                return
            started = datetime.now(timezone.utc).isoformat(timespec="seconds")
            tick = time.monotonic()
            try:
                payload = execute(item, custom_input)
                status, response = 200, {"output": payload}
            except ValueError as exc:
                status, response = 400, {"error": str(exc)}
            except OSError:
                status, response = 500, {"error": "Automation could not run. Check the local installation."}
            finally:
                slots.release()
            with lock:
                history.appendleft(dict(automation=item["name"], slug=slug, status="Completed" if status == 200 else "Failed",
                                        started=started, duration_ms=round((time.monotonic() - tick) * 1000), mode="DEMO"))
            self.respond(status, response)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description="Repka AI Automation local demo")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_server(args.port)
    print(f"Repka AI Automation: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
