from odoo import api, fields, models


class UfsTransportDocument(models.Model):
    _inherit = "ufs.transport.document"

    ai_check_ids = fields.One2many(string="AI Checks", comodel_name="ufs.ai.document.check", inverse_name="source_document_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        documents = super().create(vals_list)
        if not self.env.context.get("skip_ai_document_check"):
            documents._queue_ai_document_checks()
        return documents

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get("skip_ai_document_check") and {"attached_scan", "attached_scan_fname"} & set(vals):
            self._queue_ai_document_checks()
        return result

    def _queue_ai_document_checks(self):
        check_model = self.env["ufs.ai.document.check"]
        if not check_model._get_endpoint():
            return
        for document in self.filtered("attached_scan"):
            checksum = check_model._checksum(document.attached_scan)
            existing = check_model.search([
                ("source_document_id", "=", document.id),
                ("source_checksum", "=", checksum),
            ], limit=1)
            if existing:
                continue
            forwarder_order = document.forwarder_order_ids[:1]
            check_model.create({
                "name": "AI: %s" % (document.attached_scan_fname or document.name),
                "source_document_id": document.id,
                "forwarder_order_id": forwarder_order.id,
                "base_order_id": forwarder_order.base_order_id.id,
                "source_checksum": checksum,
            })
