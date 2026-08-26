from odoo import fields, models

class UfsMultiOrderInvoiceWizard(models.TransientModel):
    _name = "ufs.multi.order.invoice.wizard"
    _description = "Multi-Order Invoice Wizard"
    can_create_invoice = fields.Boolean(string="Can Create Invoice", readonly=True, store=False)
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    currency_id = fields.Many2one(string="Currency", required=True, comodel_name="res.currency")
    invoice_date = fields.Date(string="Invoice Date", required=True)
    move_type = fields.Selection(string="Type", required=True, selection=[("placeholder", "Placeholder")])
    order_count = fields.Integer(string="Order Count", readonly=True, store=False)
    order_ids = fields.Many2many(string="Orders", comodel_name="ufs.base.order")
    partner_id = fields.Many2one(string="Customer/Vendor", required=True, comodel_name="res.partner")
    service_line_count = fields.Integer(string="Service Lines", readonly=True, store=False)
    total_amount = fields.Monetary(string="Total Amount", readonly=True, store=False, currency_field="currency_id")
    validation_message = fields.Html(string="Validation", readonly=True, store=False)
