from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    # No ufs_base-owned fields captured for this extension

class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"
    # No ufs_base-owned fields captured for this extension
