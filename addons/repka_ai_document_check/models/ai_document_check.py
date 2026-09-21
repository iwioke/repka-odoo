import base64
import hashlib
import json
import logging
import os
from urllib import error as urlerror
from urllib import request as urlrequest

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


_logger = logging.getLogger(__name__)


class UfsAiDocumentCheck(models.Model):
    _name = "ufs.ai.document.check"
    _description = "AI Document Check"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Name", required=True, default="AI Document Check")
    source_document_id = fields.Many2one(string="Transport Document", required=True, ondelete="cascade", comodel_name="ufs.transport.document")
    forwarder_order_id = fields.Many2one(string="Forwarding Order", ondelete="set null", comodel_name="ufs.forwarder.order")
    base_order_id = fields.Many2one(string="Base Order", ondelete="set null", comodel_name="ufs.base.order")
    state = fields.Selection(
        string="State",
        required=True,
        readonly=True,
        default="queued",
        tracking=True,
        selection=[
            ("queued", "Queued"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("attention", "Attention"),
            ("blocked", "Blocked"),
            ("failed", "Failed"),
        ],
    )
    document_type = fields.Selection(
        string="Document Type",
        readonly=True,
        selection=[
            ("transport_request", "Transport Request"),
            ("cmr", "CMR"),
            ("invoice", "Invoice"),
            ("act", "Act"),
            ("unknown", "Unknown"),
        ],
    )
    document_type_confidence = fields.Float(string="Document Type Confidence", readonly=True, digits=(16, 4))
    summary = fields.Text(string="Summary", readonly=True)
    source_checksum = fields.Char(string="Source Checksum", readonly=True, index=True)
    payload_json = fields.Text(string="Request Payload", readonly=True, groups="repka_forwarding.group_57")
    result_json = fields.Text(string="AI Result", readonly=True, groups="repka_forwarding.group_57")
    checked_at = fields.Datetime(string="Checked At", readonly=True)
    approved_by_id = fields.Many2one(string="Approved By", readonly=True, comodel_name="res.users")
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    closure_override = fields.Boolean(string="Closure Override", readonly=True)
    closure_override_reason = fields.Text(string="Closure Override Reason")
    critical_activity_id = fields.Many2one(string="Critical Activity", readonly=True, ondelete="set null", comodel_name="mail.activity")
    check_line_ids = fields.One2many(string="Checks", comodel_name="ufs.ai.document.check.line", inverse_name="check_id", readonly=True)
    extracted_field_ids = fields.One2many(string="Extracted Fields", comodel_name="ufs.ai.document.check.field", inverse_name="check_id", readonly=True)
    is_demo = fields.Boolean(string="Demo Data", readonly=True, default=False)

    @api.model
    def _get_endpoint(self):
        return self.env["ir.config_parameter"].sudo().get_param("repka_ai_document_check.endpoint") or os.environ.get("AI_DOCUMENT_CHECK_URL")

    @api.model
    def _checksum(self, content):
        if isinstance(content, str):
            content = content.encode()
        try:
            source = base64.b64decode(content or b"", validate=True)
        except ValueError:
            source = content or b""
        return hashlib.sha256(source).hexdigest()

    def _field_value(self, record, name):
        if not record or name not in record._fields:
            return False
        value = record[name]
        return value.display_name if hasattr(value, "display_name") else value

    def _build_payload(self):
        self.ensure_one()
        base_order = self.base_order_id or self.forwarder_order_id.base_order_id
        route = [
            self._field_value(base_order, "origin_city") or self._field_value(base_order, "origin_id"),
            self._field_value(base_order, "destination_city") or self._field_value(base_order, "destination_id"),
        ]
        cargo_lines = self.forwarder_order_id.cargo_line_ids or base_order.cargo_line_ids
        scan = self.source_document_id.attached_scan or ""
        if isinstance(scan, bytes):
            scan = scan.decode()
        payload = {
            "request_id": str(self.id),
            "document_id": self.source_document_id.id,
            "order": {
                "number": self._field_value(base_order, "name"),
                "carrier": self._field_value(base_order, "carrier_id") or self._field_value(base_order, "partner_id"),
                "shipper": self._field_value(base_order, "shipper_id"),
                "consignee": self._field_value(base_order, "consignee_id"),
                "route": [point for point in route if point],
                "cargo": {
                    "weight_kg": sum(cargo_lines.mapped("weight")) or self._field_value(base_order, "cargo_weight") or 0,
                    "packages": sum(cargo_lines.mapped("units_count")) or self._field_value(base_order, "units_count") or 0,
                },
            },
            "document": {
                "filename": self.source_document_id.attached_scan_fname or self.source_document_id.name,
                "number": self.source_document_id.name,
                "content_base64": scan,
            },
        }
        return payload

    def _submit_to_ai(self):
        self.ensure_one()
        endpoint = self._get_endpoint()
        if not endpoint:
            self.write({"state": "failed", "summary": _("AI service endpoint is not configured.")})
            return False
        payload = self._build_payload()
        self.write({
            "state": "processing",
            "payload_json": json.dumps(payload, ensure_ascii=False),
            "summary": False,
        })
        request = urlrequest.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode())
        except (urlerror.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
            _logger.warning("AI document check %s failed: %s", self.id, error)
            self.write({"state": "failed", "summary": str(error)})
            return False
        self._apply_result(result)
        return True

    def _apply_result(self, result):
        self.ensure_one()
        state = result.get("status", "failed")
        if state not in dict(self._fields["state"].selection):
            state = "failed"
        document_type = result.get("document_type") or {}
        document_type_value = document_type.get("value", "unknown")
        if document_type_value not in dict(self._fields["document_type"].selection):
            document_type_value = "unknown"
        self.check_line_ids.unlink()
        self.extracted_field_ids.unlink()
        self.write({
            "state": state,
            "document_type": document_type_value,
            "document_type_confidence": document_type.get("confidence", 0),
            "summary": result.get("summary") or False,
            "result_json": json.dumps(result, ensure_ascii=False),
            "checked_at": fields.Datetime.now(),
        })
        self.env["ufs.ai.document.check.field"].create([
            {
                "check_id": self.id,
                "name": item.get("name"),
                "document_value": self._format_value(item.get("value")),
                "confidence": item.get("confidence", 0),
            }
            for item in result.get("extracted_fields", [])
        ])
        self.env["ufs.ai.document.check.line"].create([
            {
                "check_id": self.id,
                "code": item.get("code"),
                "severity": item.get("severity", "warning"),
                "document_value": self._format_value(item.get("document_value")),
                "crm_value": self._format_value(item.get("crm_value")),
                "message": item.get("message"),
            }
            for item in result.get("checks", [])
        ])
        if state == "blocked":
            self._schedule_critical_activity()

    @api.model
    def _format_value(self, value):
        if value in (None, False):
            return False
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _schedule_critical_activity(self):
        self.ensure_one()
        if self.critical_activity_id:
            return
        user = self.forwarder_order_id.responsible_op_user_id or self.base_order_id.responsible_user_id or self.env.user
        activity = self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=user.id,
            summary=_("AI document check blocks order closure"),
            note=self.summary or _("A critical transport document issue requires review."),
        )
        self.critical_activity_id = activity

    def action_submit(self):
        for check in self:
            check._submit_to_ai()
        return True

    def action_retry(self):
        self.write({"state": "queued", "summary": False})
        return True

    def action_approve(self):
        self.write({"approved_by_id": self.env.user.id, "approved_at": fields.Datetime.now()})
        return True

    def action_allow_closure(self):
        if not self.env.user.has_group("repka_forwarding.group_57"):
            raise AccessError(_("Only a forwarding manager can override an AI document closure block."))
        for check in self.filtered(lambda record: record.state == "blocked"):
            if not check.closure_override_reason:
                raise UserError(_("Enter a closure override reason before allowing closure."))
            check.closure_override = True
        return True

    @api.model
    def _cron_process_queued_checks(self):
        for check in self.sudo().search([("state", "=", "queued")], limit=20):
            check._submit_to_ai()


class UfsAiDocumentCheckLine(models.Model):
    _name = "ufs.ai.document.check.line"
    _description = "AI Document Check Line"
    _order = "severity desc, id"

    check_id = fields.Many2one(string="AI Check", required=True, ondelete="cascade", comodel_name="ufs.ai.document.check")
    code = fields.Char(string="Code", readonly=True)
    severity = fields.Selection(
        string="Severity",
        readonly=True,
        selection=[("info", "Info"), ("warning", "Warning"), ("critical", "Critical")],
    )
    document_value = fields.Char(string="Document Value", readonly=True)
    crm_value = fields.Char(string="CRM Value", readonly=True)
    message = fields.Text(string="Message", readonly=True)


class UfsAiDocumentCheckField(models.Model):
    _name = "ufs.ai.document.check.field"
    _description = "AI Document Check Field"
    _order = "id"

    check_id = fields.Many2one(string="AI Check", required=True, ondelete="cascade", comodel_name="ufs.ai.document.check")
    name = fields.Char(string="Field", readonly=True)
    document_value = fields.Char(string="Document Value", readonly=True)
    confidence = fields.Float(string="Confidence", readonly=True, digits=(16, 4))
