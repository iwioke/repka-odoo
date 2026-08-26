from odoo import fields, models

class ResCurrencyRateProvider(models.Model):
    _inherit = "res.currency.rate.provider"
    _order = "name"
    service = fields.Selection(string="Provider", required=True, selection=[("placeholder", "Placeholder")])
