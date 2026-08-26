from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    numeric_code = fields.Char(string="ISO 4217 Code")
