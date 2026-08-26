from odoo import fields, models

class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    # No ufs_base-owned fields captured for this extension
