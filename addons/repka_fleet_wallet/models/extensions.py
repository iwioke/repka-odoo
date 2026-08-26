from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    advance_debt_balance = fields.Monetary(string="Outstanding Advance Debt", readonly=True, store=False, help="Remaining unpaid debt from 'advance' wallet entries (advance amount minus repayments already made).", currency_field="currency_id")
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, comodel_name="res.currency", related="company_id.base_currency_id")
    company_wallet_balance = fields.Monetary(string="Driver Wallet Balance (Company Currency)", readonly=True, store=False, help="Same as Driver Wallet Balance, expressed in the company's operating currency.", currency_field="currency_id")
    ufs_fleet_wallet_balance = fields.Monetary(string="UFS Fleet Wallet Balance", readonly=True, store=False, help="Net balance: wallet cash minus outstanding advance debt.", currency_field="currency_id")
    wallet_balance = fields.Monetary(string="Driver Wallet Balance", readonly=True, store=False, help="Cash balance from 'basic' wallet entries only (salary top-ups, trip expenses). Excludes outstanding advance debt — see Advance Debt Balance.", currency_field="currency_id")
    wallet_entry_ids = fields.One2many(string="Driver Wallet", comodel_name="ufs.driver.wallet_entry", inverse_name="employee_id")
