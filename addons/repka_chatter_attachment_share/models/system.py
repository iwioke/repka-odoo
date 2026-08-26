from odoo import fields, models

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    share_url = fields.Char(string="Share URL", readonly=True, store=False)
