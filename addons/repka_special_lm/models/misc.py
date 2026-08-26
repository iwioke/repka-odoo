from odoo import fields, models

class UfsForwarderOrder(models.Model):
    _inherit = "ufs.forwarder.order"
    cargo_details = fields.Char(string="Cargo Details", readonly=True, store=False)
    carrier_freight_amount = fields.Monetary(string="Carrier Rate", readonly=True, store=False, currency_field="company_currency_id")
    customs_clearance_date = fields.Date(string="Customs Clearance Date")
    head_partner_id = fields.Many2one(string="Головной партнёр", comodel_name="res.partner")
    marking_approval_date = fields.Date(string="Marking Approved")
    marking_codes_date = fields.Date(string="Marking Codes Received")
    marking_finish_date = fields.Date(string="Marking Finished")
    marking_planned_date = fields.Date(string="Marking Planned")
    order_start_date = fields.Date(string="Order Start", readonly=True)
    shipment_rb_to_rf_date = fields.Date(string="Shipment BY to RU Date")
    state_id = fields.Many2one(string="Stage", help="Current state of the order", comodel_name="ufs.order.state")

class UfsForwarderSuborder(models.Model):
    _inherit = "ufs.forwarder.suborder"
    head_partner_id = fields.Many2one(string="Head Partner", readonly=True, comodel_name="res.partner", related="forwarder_order_id.head_partner_id")
    state_id = fields.Many2one(string="Stage", help="Current state of the SubOrder", comodel_name="ufs.order.state")
