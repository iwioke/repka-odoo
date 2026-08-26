from odoo import fields, models

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"
    xls_template = fields.Binary(string="Excel template")
