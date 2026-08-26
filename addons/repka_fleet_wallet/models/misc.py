from odoo import fields, models

class UfsFleetTrip(models.Model):
    _inherit = "ufs.fleet.trip"
    _order = "start_datetime"
    payroll_ids = fields.Many2many(string="Trips", comodel_name="ufs.driver.payroll")
    wallet_balance_end = fields.Char(string="Wallet Balance End", readonly=True, store=False)
    wallet_balance_start = fields.Char(string="Wallet Balance Start", readonly=True, store=False)
    wallet_entry_count = fields.Integer(string="Wallet Entry Count", readonly=True, store=False)
    wallet_entry_ids = fields.One2many(string="Wallet Entries", comodel_name="ufs.driver.wallet_entry", inverse_name="trip_id")

class UfsTripCadv(models.Model):
    _inherit = "ufs.trip.cadv"
    show_vault_field = fields.Boolean(string="Show Vault Field", readonly=True, store=False, help="Computed field to control vault field visibility based on settings")
    vault_id = fields.Many2one(string="Vault", comodel_name="ufs.wallet.vault")
    wallet_entry_ids = fields.One2many(string="Wallet Entries", comodel_name="ufs.driver.wallet_entry", inverse_name="cadv_id")

class UfsWalletAdvanceDeductionRule(models.Model):
    _name = "ufs.wallet.advance.deduction.rule"
    _description = "Advance Deduction Percentage Rule"
    _order = "min_debt"
    min_debt = fields.Float(string="From Amount", required=True)
    name = fields.Char(string="Name", readonly=True)
    percentage = fields.Float(string="Percentage %", required=True)
    wallet_entry_id = fields.Many2one(string="Wallet Entry", comodel_name="ufs.driver.wallet_entry")

class UfsWalletVault(models.Model):
    _name = "ufs.wallet.vault"
    _description = "UFS Wallet Vault"
    company_id = fields.Many2one(string="Company", readonly=True, comodel_name="res.company")
    current_balance_display = fields.Char(string="Current Balance", readonly=True, store=False, help="Current balance in all currencies")
    journal_id = fields.Many2one(string="Account Journal", comodel_name="account.journal")
    name = fields.Char(string="Name", required=True, translate=True)
    owner_partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    responsible_user_id = fields.Many2one(string="Responsible User", comodel_name="res.users")
    wallet_entry_count = fields.Integer(string="Transaction Count", readonly=True, store=False)
    wallet_entry_ids = fields.One2many(string="Wallet Entries", help="All transactions in this vault", comodel_name="ufs.driver.wallet_entry", inverse_name="vault_id")
