from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    cadv_waybill_limit = fields.Monetary(string="Cash Advances Limit for a Waybill", currency_field="currency_id")
