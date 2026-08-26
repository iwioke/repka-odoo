from odoo import fields, models

class ResBank(models.Model):
    _inherit = "res.bank"
    correspondent_bank_ru = fields.Char(string="Correspondent Bank")
    country_code = fields.Char(string="Country Code", readonly=True, store=False, help="The ISO country code in two chars. \nYou can use this field for quick search.", related="country.code")
    tin = fields.Char(string="TIN")

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    correspondent_bank_id = fields.Many2one(string="Correspondent Bank Account", comodel_name="res.partner.bank.correspondent")
