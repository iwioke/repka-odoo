from odoo import _, models
from odoo.exceptions import ValidationError


class UfsBaseOrder(models.Model):
    _inherit = "ufs.base.order"

    def write(self, vals):
        if vals.get("close_datetime"):
            blocked = self.env["ufs.ai.document.check"].search([
                ("base_order_id", "in", self.ids),
                ("state", "=", "blocked"),
                ("closure_override", "=", False),
            ], limit=1)
            if blocked:
                raise ValidationError(_("Order closure is blocked by an unresolved AI document check."))
        return super().write(vals)
