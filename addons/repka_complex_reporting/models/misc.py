from odoo import fields, models

class UfsForwarderOrder(models.Model):
    _inherit = "ufs.forwarder.order"
    deal_order_order_date = fields.Date(string="Deal Order Date", readonly=True, store=False, related="base_order_id.deal_order_order_date")
    deal_order_order_start_date = fields.Date(string="Deal Order Start", readonly=True, store=False, related="base_order_id.deal_order_order_start_date")
    sl_edi_amount = fields.Monetary(string="EDI SL", readonly=True, store=False, related="base_order_id.sl_edi_amount", currency_field="company_currency_id")
    sl_freight_amount = fields.Monetary(string="Freight SL", readonly=True, store=False, related="base_order_id.sl_freight_amount", currency_field="company_currency_id")
    sl_freight_margin = fields.Monetary(string="Freight Margin SL", readonly=True, currency_field="company_currency_id")
    sl_freight_responsible_id = fields.Many2one(string="Freight Responsible", comodel_name="res.users")
    sl_idle_amount = fields.Monetary(string="Idle SL", readonly=True, store=False, related="base_order_id.sl_idle_amount", currency_field="company_currency_id")
    sl_mark_amount = fields.Monetary(string="Marking SL", readonly=True, store=False, related="base_order_id.sl_mark_amount", currency_field="company_currency_id")
    sl_mark_margin = fields.Monetary(string="Marking Margin SL", readonly=True, currency_field="company_currency_id")
    sl_mark_responsible_id = fields.Many2one(string="Marking Responsible", comodel_name="res.users")
    sl_other_amount = fields.Monetary(string="Other SL", readonly=True, store=False, related="base_order_id.sl_other_amount", currency_field="company_currency_id")
    sl_reload_amount = fields.Monetary(string="Reload SL", readonly=True, store=False, related="base_order_id.sl_reload_amount", currency_field="company_currency_id")
    sl_ved_amount = fields.Monetary(string="VED SL", readonly=True, store=False, related="base_order_id.sl_ved_amount", currency_field="company_currency_id")
    sl_ved_margin = fields.Monetary(string="VED Margin SL", readonly=True, currency_field="company_currency_id")
    sl_ved_responsible_id = fields.Many2one(string="VED Responsible", comodel_name="res.users")
    trailer_types = fields.Char(string="Trailer Types", readonly=True, store=False, related="base_order_id.trailer_types")
    trailer_types_needed_ids = fields.Many2many(string="Trailer Type Needed", readonly=True, comodel_name="fleet.vehicle.trailer_type", related="base_order_id.trailer_types_needed_ids")
