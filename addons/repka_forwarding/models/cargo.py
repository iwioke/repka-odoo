from odoo import fields, models

class UfsCargoLine(models.Model):
    _inherit = "ufs.cargo_line"
    forwarder_order_id = fields.Many2one(string="Order", comodel_name="ufs.forwarder.order")
    forwarder_suborder_id = fields.Many2one(string="Order", comodel_name="ufs.forwarder.suborder")
