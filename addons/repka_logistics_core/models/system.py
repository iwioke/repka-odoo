from odoo import fields, models

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"
    # No ufs_base-owned fields captured for this extension

class IrSequence(models.Model):
    _inherit = "ir.sequence"
    # No ufs_base-owned fields captured for this extension

class MailMail(models.Model):
    _inherit = "mail.mail"
    # No ufs_base-owned fields captured for this extension

class MailTemplate(models.Model):
    _inherit = "mail.template"
    force_stamp = fields.Boolean(string="Force Stamp", help="Render the attached report(s) with the company stamp, regardless of the Print Stamp flag on the document.")

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"
    # No ufs_base-owned fields captured for this extension
