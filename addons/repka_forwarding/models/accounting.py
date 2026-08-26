from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    ufs_forwarder_order_id = fields.Many2one(string="Forwarding Order", help="Main forwarder order - computed from service lines", comodel_name="ufs.forwarder.order")
    ufs_forwarder_order_ids = fields.Many2many(string="All Forwarder Orders", readonly=True, help="All forwarder orders connected via service lines", comodel_name="ufs.forwarder.order")
    ufs_forwarder_sub_order_id = fields.Many2one(string="Forwarding SubOrder", help="Main forwarder suborder - computed from service lines", comodel_name="ufs.forwarder.suborder")
    ufs_forwarder_sub_order_ids = fields.Many2many(string="All Forwarder SubOrders", readonly=True, help="All forwarder suborders connected via service lines", comodel_name="ufs.forwarder.suborder")
    verbose_cargoes_no_weight = fields.Char(string="Cargo Verbose")

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    attached_documents = fields.Char(string="Attached Documents")
    ufs_act_date = fields.Date(string="Act Date")
    ufs_container = fields.Char(string="Container")
    ufs_forwarder_sub_order_id = fields.Many2one(string="Forwarding Order", comodel_name="ufs.forwarder.suborder")
    ufs_route = fields.Char(string="Route")
    ufs_vehicle = fields.Char(string="Vehicle")
