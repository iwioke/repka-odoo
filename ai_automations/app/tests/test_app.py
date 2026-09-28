import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parent
sys.path.insert(0, str(APP))
from server import catalog, create_server


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, payload=None, origin=None):
        headers = {}
        if payload is not None:
            headers = {"Content-Type": "application/json", "Origin": origin or self.origin}
        request = Request(self.origin + path, data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        try:
            with urlopen(request, timeout=15) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_catalogue_and_static_assets(self):
        status, data = self.request("/api/automations")
        self.assertEqual(status, 200)
        items = data["automations"]
        self.assertEqual(len(items), 23)
        self.assertEqual(len([item for item in items if item["runnable"]]), 4)
        self.assertEqual(len([item for item in items if item["status"] == "BLOCKED"]), 19)
        self.assertEqual([item["slug"] for item in items[:4]], ["customer_360", "margin_watch", "document_readiness", "executive_brief"])
        self.assertTrue(all(item["details"]["what"] and item["description"] and item["category"] for item in items))
        for path, content_type in (("/", "text/html"), ("/app.js", "text/javascript"), ("/style.css", "text/css")):
            with self.subTest(path=path), urlopen(self.origin + path) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(content_type, response.headers["Content-Type"])
                self.assertTrue(response.read())
        self.assertEqual(self.request("/../../.env")[0], 404)

    def test_all_demos_run_and_repeat_with_real_outputs(self):
        for item in catalog():
            if not item["runnable"]:
                continue
            with self.subTest(slug=item["slug"]):
                first_status, first = self.request("/api/run", {"slug": item["slug"], "mode": "DEMO"})
                again_status, again = self.request("/api/run", {"slug": item["slug"], "mode": "DEMO"})
                expected = json.loads((ROOT / "scenarios" / item["slug"] / "example_output.json").read_text(encoding="utf-8"))
                self.assertEqual((first_status, again_status), (200, 200))
                self.assertEqual(first["output"], expected)
                self.assertEqual(again, first)
        status, data = self.request("/api/history")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(data["runs"]), 8)
        self.assertTrue(all(set(run) == {"automation", "slug", "status", "started", "duration_ms", "mode"} for run in data["runs"]))

    def test_custom_input_failure_and_retry(self):
        item = catalog()[0]
        status, result = self.request("/api/run", {"slug": item["slug"], "mode": "DEMO", "input": item["example_input"]})
        self.assertEqual(status, 200)
        self.assertEqual(result["output"]["scenario"], item["slug"])
        status, failure = self.request("/api/run", {"slug": item["slug"], "mode": "DEMO", "input": {}})
        self.assertEqual(status, 400)
        self.assertIn("rejected", failure["error"])
        self.assertNotIn("Traceback", failure["error"])
        status, retry = self.request("/api/run", {"slug": item["slug"], "mode": "DEMO"})
        self.assertEqual(status, 200)
        self.assertEqual(retry["output"], result["output"])
        self.assertEqual(self.request("/api/history")[1]["runs"][1]["status"], "Failed")

    def test_live_blocked_origin_blocked_and_no_arbitrary_execution(self):
        for payload in ({"slug": "customer_360", "mode": "LIVE"},
                        {"slug": "future-lead-scoring-qualification", "mode": "DEMO"},
                        {"slug": "../../server", "mode": "DEMO"}):
            with self.subTest(payload=payload):
                self.assertEqual(self.request("/api/run", payload)[0], 400)
        self.assertEqual(self.request("/api/run", {"slug": "customer_360", "mode": "DEMO"}, origin="http://evil.example")[0], 403)
        self.assertEqual(self.request("/api/run", {"slug": "customer_360", "mode": "DEMO", "input": []})[0], 400)


if __name__ == "__main__":
    unittest.main()
