from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    # No ufs_base-owned fields captured for this extension
