from odoo import fields, models

class UfsBaseOrder(models.Model):
    _inherit = "ufs.base.order"
    _order = "deal_order_order_start_date desc, id asc"
    order_reference = fields.Reference(string="Order Reference", help="Reference to the actual order record", selection=[("ufs.base.order", "Order")])
