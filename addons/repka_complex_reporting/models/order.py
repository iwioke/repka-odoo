from odoo import fields, models

class UfsBaseOrder(models.Model):
    _inherit = "ufs.base.order"
    _order = "deal_order_order_start_date desc, id asc"
    deal_order_order_date = fields.Date(string="Deal Order Date", readonly=True, related="deal_order_id.order_date")
    deal_order_order_start_date = fields.Date(string="Deal Order Start", readonly=True, related="deal_order_id.start_date")
    sl_edi_amount = fields.Monetary(string="EDI SL", readonly=True, currency_field="company_currency_id")
    sl_freight_amount = fields.Monetary(string="Freight SL", readonly=True, currency_field="company_currency_id")
    sl_idle_amount = fields.Monetary(string="Idle SL", readonly=True, currency_field="company_currency_id")
    sl_mark_amount = fields.Monetary(string="Marking SL", readonly=True, currency_field="company_currency_id")
    sl_other_amount = fields.Monetary(string="Other SL", readonly=True, currency_field="company_currency_id")
    sl_reload_amount = fields.Monetary(string="Reload SL", readonly=True, currency_field="company_currency_id")
    sl_ved_amount = fields.Monetary(string="VED SL", readonly=True, currency_field="company_currency_id")
    trailer_types = fields.Char(string="Trailer Types", readonly=True)
    trailer_types_needed_ids = fields.Many2many(string="Trailer Type Needed", readonly=True, comodel_name="fleet.vehicle.trailer_type")
    vehicles_string = fields.Char(string="Vehicles", readonly=True)
    verbose_cargoes = fields.Char(string="Cargo Details", readonly=True)
    verbose_cargoes_no_weight = fields.Char(string="Cargo (No Weight)", readonly=True)
    verbose_route = fields.Char(string="Route", readonly=True)
