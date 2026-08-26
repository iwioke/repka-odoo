from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"
    forw_order_count = fields.Integer(string="Forwarding Order Count", readonly=True, store=False)
    forw_order_ids = fields.One2many(string="Forwarding Orders", comodel_name="ufs.forwarder.order", inverse_name="partner_id")
    forw_sub_order_count = fields.Integer(string="Forwarding SubOrder Count", readonly=True, store=False)
    forw_sub_order_ids = fields.One2many(string="Forwarding SubOrders", comodel_name="ufs.forwarder.suborder", inverse_name="partner_id")
