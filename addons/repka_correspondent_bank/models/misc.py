from odoo import fields, models

class ResPartnerBankCorrespondent(models.Model):
    _name = "res.partner.bank.correspondent"
    _description = "__doc__"
    _order = "sequence, id"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    acc_holder_name = fields.Char(string="Account Holder Name", help="Account holder name, in case it is different than the name of the Account Holder")
    acc_number = fields.Char(string="Account Number", required=True)
    acc_type = fields.Selection(string="Type", readonly=True, store=False, help="Bank account type: Normal or IBAN. Inferred from the bank account number.", selection=[("placeholder", "Placeholder")])
    account_name = fields.Char(string="Account Name")
    active = fields.Boolean(string="Active")
    allow_out_payment = fields.Boolean(string="Send Money", help="Sending fake invoices with a fraudulent account number is a common phishing practice. To protect yourself, always verify new bank account numbers, preferably by calling the vendor, as phishing usually happens when their emails are compromised. Once verified, you can activate the ability to send money.")
    bank_id = fields.Many2one(string="Bank", comodel_name="res.bank")
    correspondent_bank_id = fields.Many2one(string="Correspondent Bank Account", comodel_name="res.partner.bank.correspondent")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    duplicate_bank_partner_ids = fields.Many2many(string="Duplicate Bank Partner", readonly=True, comodel_name="res.partner")
    has_iban_warning = fields.Boolean(string="Has Iban Warning", readonly=True, help="Technical field used to display a warning if the IBAN country is different than the holder country.")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    has_money_transfer_warning = fields.Boolean(string="Has Money Transfer Warning", readonly=True, help="Technical field used to display a warning if the account is a transfer service account.")
    journal_id = fields.One2many(string="Account Journal", readonly=True, help="The accounting journal corresponding to this bank account.", comodel_name="account.journal", inverse_name="bank_account_id")
    lock_trust_fields = fields.Boolean(string="Lock Trust Fields", readonly=True, store=False)
    money_transfer_service = fields.Char(string="Money Transfer Service", readonly=True, store=False)
    partner_id = fields.Many2one(string="Account Holder", required=True, comodel_name="res.partner")
    related_moves = fields.One2many(string="Related Moves", comodel_name="account.move", inverse_name="partner_bank_id")
    sanitized_acc_number = fields.Char(string="Sanitized Account Number", readonly=True)
    sequence = fields.Integer(string="Sequence")
    user_has_group_validate_bank_account = fields.Boolean(string="User Has Group Validate Bank Account", readonly=True, store=False)
    bank_bic = fields.Char(string="Bank Identifier Code", store=False, help="Sometimes called BIC or Swift.", related="bank_id.bic")
    bank_name = fields.Char(string="Name", store=False, related="bank_id.name")
    bank_tin = fields.Char(string="TIN", readonly=True, store=False, related="bank_id.tin")
    company_id = fields.Many2one(string="Company", comodel_name="res.company", related="partner_id.company_id")
    country_code = fields.Char(string="Country Code", readonly=True, store=False, help="The ISO country code in two chars. \nYou can use this field for quick search.", related="partner_id.country_code")
    partner_country_name = fields.Char(string="Country Name", readonly=True, store=False, translate=True, related="partner_id.country_id.name")
    partner_customer_rank = fields.Integer(string="Customer Rank", readonly=True, store=False, related="partner_id.customer_rank")
    partner_supplier_rank = fields.Integer(string="Supplier Rank", readonly=True, store=False, related="partner_id.supplier_rank")
