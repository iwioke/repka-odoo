from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    cadv_waybill_limit = fields.Monetary(string="Cash Advances Limit for a Waybill", store=False, related="company_id.cadv_waybill_limit", currency_field="currency_id")
