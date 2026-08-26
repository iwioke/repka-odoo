from odoo import fields, models

class UfsTransportDocumentType(models.Model):
    _name = "ufs.transport.document.type"
    _description = "Transport Document Type"
    active = fields.Boolean(string="Active")
    name = fields.Char(string="Name")
    show_in_partner_form = fields.Boolean(string="Show in Partner Form", help="If checked, this document type appears in the public partner registration form.")
    to_move = fields.Boolean(string="To Move", help="If checked, the document will be passed to the account move")
