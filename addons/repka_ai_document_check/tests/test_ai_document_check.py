import base64

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAiDocumentCheck(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "AI Check Customer"})
        self.base_order = self.env["ufs.base.order"].create({
            "name": "AI-CHECK-001",
            "company_id": self.env.company.id,
            "partner_id": self.partner.id,
        })
        self.forwarder_order = self.env["ufs.forwarder.order"].create({"base_order_id": self.base_order.id})
        self.env["ufs.cargo_line"].create({
            "forwarder_order_id": self.forwarder_order.id,
            "name": "Demo Cargo",
            "weight": 8500,
            "units_count": 18,
        })
        self.document = self.env["ufs.transport.document"].with_context(skip_ai_document_check=True).create({
            "name": "CMR-AI-CHECK-001",
            "attached_scan": base64.b64encode(b"demo cmr").decode(),
            "attached_scan_fname": "cmr-error-demo.pdf",
            "forwarder_order_ids": [(4, self.forwarder_order.id)],
        })

    def _blocked_result(self):
        return {
            "status": "blocked",
            "document_type": {"value": "cmr", "confidence": 0.99},
            "summary": "CMR requires correction.",
            "extracted_fields": [{"name": "weight_kg", "value": 9250, "confidence": 0.98}],
            "checks": [
                {
                    "code": "cargo_weight_mismatch",
                    "severity": "warning",
                    "document_value": 9250,
                    "crm_value": 8500,
                    "message": "Weight differs from CRM.",
                },
                {
                    "code": "consignee_stamp_missing",
                    "severity": "critical",
                    "message": "Consignee stamp is missing.",
                },
            ],
        }

    def test_document_upload_queues_check(self):
        self.env["ir.config_parameter"].sudo().set_param("repka_ai_document_check.endpoint", "http://127.0.0.1:8080/check")
        document = self.env["ufs.transport.document"].create({
            "name": "Invoice-AI-CHECK-001",
            "attached_scan": base64.b64encode(b"demo invoice").decode(),
            "attached_scan_fname": "invoice-demo.pdf",
            "forwarder_order_ids": [(4, self.forwarder_order.id)],
        })
        check = self.env["ufs.ai.document.check"].search([("source_document_id", "=", document.id)])
        self.assertEqual(len(check), 1)
        self.assertEqual(check.state, "queued")
        self.assertEqual(check.forwarder_order_id, self.forwarder_order)

    def test_payload_uses_forwarder_cargo_lines(self):
        check = self.env["ufs.ai.document.check"].create({
            "name": "AI: CMR-AI-CHECK-001",
            "source_document_id": self.document.id,
            "forwarder_order_id": self.forwarder_order.id,
            "base_order_id": self.base_order.id,
            "source_checksum": "demo-payload",
        })
        payload = check._build_payload()
        self.assertEqual(payload["order"]["cargo"]["weight_kg"], 8500)
        self.assertEqual(payload["order"]["cargo"]["packages"], 18)

    def test_blocked_check_prevents_order_closure(self):
        check = self.env["ufs.ai.document.check"].create({
            "name": "AI: CMR-AI-CHECK-001",
            "source_document_id": self.document.id,
            "forwarder_order_id": self.forwarder_order.id,
            "base_order_id": self.base_order.id,
            "source_checksum": "demo",
        })
        check._apply_result(self._blocked_result())
        self.assertEqual(check.state, "blocked")
        self.assertEqual(len(check.check_line_ids), 2)
        self.assertEqual(check.extracted_field_ids.document_value, "9250")
        with self.assertRaises(ValidationError):
            self.base_order.write({"close_datetime": fields.Datetime.now()})
