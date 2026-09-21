import base64

from odoo import _, fields, models
from odoo.exceptions import UserError


class UfsAiDocumentCheckDemoWizard(models.TransientModel):
    _name = "ufs.ai.document.check.demo.wizard"
    _description = "AI Document Check Demo Wizard"

    name = fields.Char(string="Name", default="AI Document Check Demo")

    def action_create_demo(self):
        self.ensure_one()
        check_model = self.env["ufs.ai.document.check"]
        if not check_model._get_endpoint():
            raise UserError(_("Configure the AI document check endpoint before creating demo data."))
        existing = check_model.search([("is_demo", "=", True)], limit=1)
        if existing:
            return self._checks_action(existing.search([("is_demo", "=", True)]))
        customer = self.env["res.partner"].create({"name": "ООО «Демо Клиент»"})
        shipper = self.env["res.partner"].create({"name": "ООО «Демо Отправитель»"})
        consignee = self.env["res.partner"].create({"name": "ООО «Демо Получатель»"})
        base_order = self.env["ufs.base.order"].create({
            "name": "EXP-DEMO-001",
            "company_id": self.env.company.id,
            "partner_id": customer.id,
            "shipper_id": shipper.id,
            "consignee_id": consignee.id,
            "origin_city": "Минск, Беларусь",
            "destination_city": "Варшава, Польша",
            "order_date": fields.Date.context_today(self),
        })
        forwarder_order = self.env["ufs.forwarder.order"].create({"base_order_id": base_order.id})
        self.env["ufs.cargo_line"].create({
            "forwarder_order_id": forwarder_order.id,
            "name": "Бытовая техника",
            "weight": 8500,
            "units_count": 18,
        })
        checks = self.env["ufs.ai.document.check"]
        documents = [
            ("Заявка DEMO-001", "transport-request-demo.pdf"),
            ("CMR DEMO-001", "cmr-error-demo.pdf"),
            ("Счёт DEMO-001", "invoice-demo.pdf"),
            ("Акт DEMO-001", "act-demo.pdf"),
        ]
        for number, filename in documents:
            document = self.env["ufs.transport.document"].with_context(skip_ai_document_check=True).create({
                "name": number,
                "date": fields.Date.context_today(self),
                "attached_scan": self._demo_content(number),
                "attached_scan_fname": filename,
                "forwarder_order_ids": [(4, forwarder_order.id)],
            })
            checks |= check_model.create({
                "name": "AI: %s" % filename,
                "source_document_id": document.id,
                "forwarder_order_id": forwarder_order.id,
                "base_order_id": base_order.id,
                "source_checksum": check_model._checksum(document.attached_scan),
                "is_demo": True,
            })
        checks.action_submit()
        return self._checks_action(checks)

    def _demo_content(self, number):
        return base64.b64encode(("DEMO DOCUMENT: %s" % number).encode()).decode()

    def _checks_action(self, checks):
        return {
            "type": "ir.actions.act_window",
            "name": _("AI Document Checks"),
            "res_model": "ufs.ai.document.check",
            "view_mode": "list,form",
            "domain": [("id", "in", checks.ids)],
        }
