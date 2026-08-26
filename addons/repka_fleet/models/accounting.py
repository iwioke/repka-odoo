from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    amount_residual_base = fields.Monetary(string="Residual Amount in Base Currency", readonly=True, currency_field="currency_id")
    amount_total_base = fields.Monetary(string="Amount in Base Currency", readonly=True, currency_field="currency_id")
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.base_currency_id")
    is_business_day_term = fields.Boolean(string="Is Business day N term", readonly=True)
    is_cash_expected = fields.Boolean(string="Cash Expected")
    is_n_term = fields.Boolean(string="Is N term", readonly=True)
    is_ufs_move = fields.Boolean(string="Is UFS Move", readonly=True)
    line_refs = fields.Text(string="Line Refs", readonly=True)
    n_days_count = fields.Integer(string="N", readonly=True)
    order_cost_id = fields.Many2one(string="Fleet Order Cost", comodel_name="ufs.fleet.order.cost")
    payment_term_id = fields.Many2one(string="Payment Terms", readonly=True, comodel_name="account.payment.term")
    ufs_fleet_order_id = fields.Many2one(string="Fleet Order", help="Main fleet order - computed from service lines or can be set manually", comodel_name="ufs.fleet.order")
    ufs_fleet_order_ids = fields.Many2many(string="All Fleet Orders", readonly=True, help="All fleet orders connected via service lines", comodel_name="ufs.fleet.order")
    ufs_payment_term_id = fields.Many2one(string="Payment Terms", readonly=True, comodel_name="ufs.payment.term")
    ufs_state = fields.Selection(string="Ufs State", readonly=True, store=False, translate=True, selection=[("placeholder", "Placeholder")])
    ufs_state_localized = fields.Char(string="Inv.state", readonly=True, store=False)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    ufs_fleet_order_id = fields.Many2one(string="Fleet Order", readonly=True, store=False, help="Main fleet order - computed from service lines or can be set manually", comodel_name="ufs.fleet.order", related="move_id.ufs_fleet_order_id")
    verbose_cargoes_no_weight = fields.Char(string="Cargo Verbose", readonly=True, store=False)
