from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    cadv_responsible_user_ids = fields.Many2many(string="Cash Advance Responsible Users", comodel_name="res.users")
    cadv_trip_limit = fields.Monetary(string="Cash Advances Limit for a Trip", currency_field="currency_id")
