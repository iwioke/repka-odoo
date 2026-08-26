from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"
    invoice_address_id = fields.Many2one(string="Invoice Address", readonly=True, store=False, comodel_name="res.partner")
