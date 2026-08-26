from odoo import fields, models

class UfsTransportDocument(models.Model):
    _inherit = "ufs.transport.document"
    forwarder_order_ids = fields.Many2many(string="Forwarder Orders", comodel_name="ufs.forwarder.order")
    forwarder_suborder_ids = fields.Many2many(string="Forwarder SubOrders", comodel_name="ufs.forwarder.suborder")
    sub_orders_partner_id = fields.Many2one(string="Sub Orders Partner", readonly=True, store=False, comodel_name="res.partner")
