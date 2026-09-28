import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import FUNCTIONS, SCENARIOS


class ScenarioTests(unittest.TestCase):
    def call(self, slug, *args):
        return subprocess.run([sys.executable, str(ROOT / slug / "run.py"), *args],
                              capture_output=True, text=True, timeout=10)

    def test_each_scenario_launch_repeat_and_result(self):
        for slug in SCENARIOS:
            with self.subTest(scenario=slug):
                first = self.call(slug)
                again = self.call(slug)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(first.stdout, again.stdout)
                payload = json.loads(first.stdout)
                self.assertEqual(payload["mode"], "DEMO")
                self.assertEqual(payload["scenario"], slug)
                self.assertTrue(payload["result"])
                expected = json.loads((ROOT / slug / "example_output.json").read_text(encoding="utf-8"))
                self.assertEqual(payload, expected)

    def test_live_fails_closed(self):
        for slug in SCENARIOS:
            with self.subTest(scenario=slug):
                result = self.call(slug, "--mode", "live")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(result.stdout)
                self.assertIn("LIVE MODE", result.stderr)

    def test_invalid_and_missing_inputs(self):
        for slug in SCENARIOS:
            with self.subTest(scenario=slug):
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "input.json"
                    path.write_text("{}", encoding="utf-8")
                    result = self.call(slug, "--input", str(path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(result.stdout)
                    path.write_text("invalid", encoding="utf-8")
                    self.assertNotEqual(self.call(slug, "--input", str(path)).returncode, 0)
                self.assertNotEqual(self.call(slug, "--input", str(path)).returncode, 0)

    def test_expected_findings(self):
        results = {slug: FUNCTIONS[slug](json.loads((ROOT / slug / "example_input.json").read_text(encoding="utf-8")))
                   for slug in SCENARIOS}
        self.assertEqual(results["customer_360"]["review_reactivation"], 1)
        self.assertEqual(results["margin_watch"]["orders"][0]["result"], "-600.00")
        self.assertEqual(results["document_readiness"]["orders"][0]["missing"], ["act"])
        self.assertEqual(list(results["executive_brief"]["kpis"].values()), [1, 1, 1])

    def test_currency_dates_and_untrusted_values(self):
        with self.assertRaises(ValueError):
            FUNCTIONS["margin_watch"]({"orders": [{"id": 1, "name": "a", "currency": "USD", "cost_currency": "BYN", "revenue": "5", "direct_cost": "2"}]})
        with self.assertRaises(ValueError):
            FUNCTIONS["margin_watch"]({"orders": [{"id": 1, "name": "a", "currency": "BYN", "cost_currency": "BYN", "revenue": "NaN", "direct_cost": "2"}]})
        with self.assertRaises(ValueError):
            FUNCTIONS["customer_360"]({"as_of": "2020-01-01", "partners": [{"id": 1, "name": "a"}], "orders": [{"id": 1, "partner_id": 1, "order_date": "2021-01-01", "is_paid": True}]})
        with self.assertRaises(ValueError):
            FUNCTIONS["document_readiness"]({"required_types": ["cmr", "cmr"], "orders": []})
        mixed = FUNCTIONS["document_readiness"]({"required_types": ["cmr"], "orders": [
            {"id": 1, "checks": [{"document_type": "cmr", "state": "completed"},
                                  {"document_type": "cmr", "state": "blocked"}]}]})
        self.assertEqual(mixed["review_count"], 1)

    def test_launcher_list_and_dispatch(self):
        launcher = ROOT / "run_all.py"
        listing = subprocess.run([sys.executable, str(launcher), "--list"], capture_output=True, text=True)
        self.assertEqual(listing.returncode, 0)
        self.assertEqual(listing.stdout.count("DEMO"), 4)
        selected = subprocess.run([sys.executable, str(launcher), "customer_360"], capture_output=True, text=True)
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(json.loads(selected.stdout)["scenario"], "customer_360")


if __name__ == "__main__":
    unittest.main()
