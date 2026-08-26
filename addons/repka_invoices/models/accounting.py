from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    amount_tax_company = fields.Monetary(string="Amount Tax Company", readonly=True, store=False, currency_field="currency_id")
    amount_total_company = fields.Monetary(string="Amount Total Company", readonly=True, store=False, currency_field="currency_id")
    amount_untaxed_company = fields.Monetary(string="Amount UntaxedTotal Company", readonly=True, store=False, currency_field="currency_id")
    invoice_type = fields.Selection(string="Invoice Type", readonly=True, store=False, selection=[("placeholder", "Placeholder")])
    is_a_proforma_invoice = fields.Boolean(string="Proforma Invoice")
    pl_currency_text = fields.Char(string="Pl Currency Text", readonly=True, store=False)
    proforma_invoice_nr = fields.Char(string="Number")

class AccountMoveAct(models.Model):
    _inherit = "account.move.act"
    amount_tax_company = fields.Monetary(string="Amount Tax Company", readonly=True, store=False, currency_field="currency_id")
    amount_total_company = fields.Monetary(string="Amount Total Company", readonly=True, store=False, currency_field="currency_id")
    amount_untaxed_company = fields.Monetary(string="Amount UntaxedTotal Company", readonly=True, store=False, currency_field="currency_id")
    company_currency_id = fields.Many2one(string="Company Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.currency_id")
    invoice_partner_bank_ids = fields.Many2many(string="Bank Accounts for Report", help="If is set, these accounts will be printed out for some reports", comodel_name="res.partner.bank")

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    price_subtotal_company = fields.Monetary(string="Price Subtotal Company", readonly=True, store=False, currency_field="currency_id")
    price_tax_company = fields.Monetary(string="Price Tax Company", readonly=True, store=False, currency_field="currency_id")
    price_total_company = fields.Monetary(string="Price Total Company", readonly=True, store=False, currency_field="currency_id")
    price_unit_company = fields.Monetary(string="Price Unit Company", readonly=True, store=False, currency_field="currency_id")
    tax_sum = fields.Monetary(string="Tax Sum", readonly=True, store=False, currency_field="currency_id")
