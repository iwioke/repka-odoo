import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import build_result


class TestMockDocumentCheck(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "request_id": "demo-request",
            "order": {
                "carrier": "ООО «Демо Транс»",
                "route": ["Минск, Беларусь", "Варшава, Польша"],
                "cargo": {"weight_kg": 8500},
            },
            "document": {"number": "DEMO-001"},
        }

    def test_recognizes_demo_document_types(self):
        expected = {
            "transport-request-demo.pdf": "transport_request",
            "cmr-demo.pdf": "cmr",
            "invoice-demo.pdf": "invoice",
            "act-demo.pdf": "act",
        }
        for filename, document_type in expected.items():
            with self.subTest(filename=filename):
                payload = dict(self.payload, document={"filename": filename, "number": "DEMO-001"})
                self.assertEqual(build_result(payload)["document_type"]["value"], document_type)

    def test_error_cmr_blocks_order_closure(self):
        payload = dict(self.payload, document={"filename": "cmr-error-demo.pdf", "number": "DEMO-001"})
        result = build_result(payload)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["extracted_fields"][-1]["value"], 9250)
        self.assertEqual({check["code"] for check in result["checks"]}, {"cargo_weight_mismatch", "consignee_stamp_missing"})
