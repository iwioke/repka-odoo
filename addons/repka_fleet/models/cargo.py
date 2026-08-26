from odoo import fields, models

class UfsCargoLine(models.Model):
    _inherit = "ufs.cargo_line"
    fleet_based_on_order_id = fields.Many2one(string="Based on", readonly=True, comodel_name="ufs.fleet.order")
    fleet_close_datetime = fields.Datetime(string="Act Date", readonly=True)
    fleet_order_id = fields.Many2one(string="Fleet Order", comodel_name="ufs.fleet.order")
    fleet_partner_id = fields.Many2one(string="Customer", readonly=True, comodel_name="res.partner")
