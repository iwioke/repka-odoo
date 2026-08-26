from odoo import fields, models

class UfsTransportDocument(models.Model):
    _inherit = "ufs.transport.document"
    fleet_order_id = fields.Many2one(string="Fleet Order", comodel_name="ufs.fleet.order")
    fleet_order_ids = fields.Many2many(string="Fleet Orders", comodel_name="ufs.fleet.order")
