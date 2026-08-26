from odoo import fields, models

class ResBank(models.Model):
    _inherit = "res.bank"
    bic_2 = fields.Char(string="Additional BIC", help="For some countries BIC is not euqal to international SWIFT code")
    name_transliterated = fields.Char(string="Name (Transliterated)", help="Name in transliterated form")

class ResPartner(models.Model):
    _inherit = "res.partner"
    address_en = fields.Char(string="Address Latin")
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency")
    city_en = fields.Char(string="City Latin")
    contact_subtype = fields.Selection(string="Contact Type", selection=[("placeholder", "Placeholder")])
    contract_ids = fields.One2many(string="Contracts", readonly=True, comodel_name="ufs.contract", inverse_name="partner_id")
    contractor_status = fields.Selection(string="Contractor Status", selection=[("placeholder", "Placeholder")])
    contracts_count = fields.Integer(string="Contracts Count", readonly=True, store=False)
    count_authority_text = fields.Char(string="Authority Text", translate=True)
    count_signed_by_partner_id = fields.Many2one(string="Signed by", comodel_name="res.partner")
    credit_balance = fields.Monetary(string="Credit Balance", readonly=True, store=False, help="Open Order Freight Sum - Already Paid Amount", currency_field="currency_id")
    credit_limit_line_ids = fields.One2many(string="Credit Limits", comodel_name="res.partner.credit_limit", inverse_name="partner_id")
    credit_sum = fields.Monetary(string="Credit", readonly=True, store=False, currency_field="currency_id")
    debit_sum = fields.Monetary(string="Debit", readonly=True, store=False, currency_field="currency_id")
    doc_preference_ids = fields.One2many(string="Document Delivery Preferences", comodel_name="res.partner.doc.preference", inverse_name="partner_id")
    document_ids = fields.One2many(string="Documents", comodel_name="ufs.partner.doc.line", inverse_name="partner_id")
    full_name = fields.Char(string="Full Name")
    internal_ref = fields.Char(string="Internal RefNr.")
    is_cash_expected = fields.Boolean(string="Cash Expected", help="If you expect Cash for order Payment, mark order as Cash, so we will create Invoices with Cash attributes")
    limit_overdue = fields.Monetary(string="Limit Overdue", readonly=True, store=False, currency_field="currency_id")
    location_ids = fields.One2many(string="Location", comodel_name="ufs.location", inverse_name="partner_id")
    locations_count = fields.Integer(string="Locations", readonly=True, store=False)
    n_days_count = fields.Integer(string="N")
    other_subtype = fields.Selection(string="Other Subtype", selection=[("placeholder", "Placeholder")])
    payment_term_id = fields.Many2one(string="Payment Terms", comodel_name="account.payment.term")
    payment_term_verbose = fields.Char(string="Verbose Term", readonly=True, store=False)
    required_doc_type_ids = fields.Many2many(string="Required Docs for Order", help="Choose Document Types required by default for new Orders", comodel_name="ufs.transport.document.type")
    ru_kpp = fields.Char(string="KPP")
    ru_ogrn = fields.Char(string="OGRN")
    short_name = fields.Char(string="Short Name")
    subsidiary_ids = fields.One2many(string="Subsidiaries", comodel_name="res.partner", inverse_name="parent_id")
    text_address = fields.Text(string="Text Address", readonly=True, store=False)
    translit_name = fields.Char(string="Name Latin")
    u_guid = fields.Char(string="GUID")
    ufs_credit_limit = fields.Float(string="Credit Limit", readonly=True, store=False, help="O means not set")
    ufs_payment_term_id = fields.Many2one(string="Payment Terms", comodel_name="ufs.payment.term")
    use_extended_naming = fields.Boolean(string="Use Extended Naming", readonly=True, store=False)
    use_orders_based_credit_limit = fields.Boolean(string="Use Orders Based Credit Limit", readonly=True, store=False)
    is_business_day_term = fields.Boolean(string="Is Business Day Term", readonly=True, store=False, related="ufs_payment_term_id.is_business_day_term")
    is_n_term = fields.Boolean(string="Is N term", readonly=True, store=False, related="ufs_payment_term_id.is_n_term")
    name_en = fields.Char(string="Name Latin", store=False, related="translit_name")

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    bank_bic_2 = fields.Char(string="Additional BIC", readonly=True, store=False, help="For some countries BIC is not equal to international SWIFT code", related="bank_id.bic_2")
    company_id = fields.Many2one(string="Company", comodel_name="res.company", related="partner_id.company_id")
    u_guid = fields.Char(string="GUID")

class ResPartnerCreditLimit(models.Model):
    _name = "res.partner.credit_limit"
    _description = "Credit Limit For Partner/Company"
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    partner_id = fields.Many2one(string="Partner", required=True, comodel_name="res.partner")
    currency_id = fields.Many2one(string="Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.base_currency_id")

class ResPartnerDocPreference(models.Model):
    _name = "res.partner.doc.preference"
    _description = "Partner Document Delivery Preference"
    _order = "doc_type_id"
    by_edi = fields.Boolean(string="By EDI")
    by_email = fields.Boolean(string="By Email")
    by_post = fields.Boolean(string="By Post")
    doc_type_id = fields.Many2one(string="Document Type", required=True, comodel_name="ufs.transport.document.type")
    docs_email = fields.Char(string="Email for Documents")
    partner_id = fields.Many2one(string="Partner", required=True, comodel_name="res.partner")
    postal_contact_name = fields.Char(string="Postal Contact (FIO)")
    postal_contact_phone = fields.Char(string="Postal Contact Phone")

class UfsPartnerDocLine(models.Model):
    _name = "ufs.partner.doc.line"
    _description = "Partner Document Line"
    doc_id = fields.Many2one(string="Doc", required=True, comodel_name="ufs.doc")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    attached_scan = fields.Binary(string="Attached Scan", store=False, related="doc_id.attached_scan")
    attached_scan_fname = fields.Char(string="FName", store=False, related="doc_id.attached_scan_fname")
    color = fields.Integer(string="Color Index", readonly=True, store=False, related="doc_id.color")
    days_to_renew = fields.Integer(string="Days To Renew Reminder", readonly=True, store=False, related="doc_id.days_to_renew")
    display_prefix = fields.Char(string="Display Prefix", store=False, related="doc_id.display_prefix")
    doc_type = fields.Many2one(string="Doc Type", required=True, store=False, comodel_name="ufs.doc.type", related="doc_id.doc_type")
    expiration_date = fields.Date(string="Expiration Date", required=True, store=False, related="doc_id.expiration_date")
    full_name = fields.Char(string="Full Name", readonly=True, store=False, related="doc_id.full_name")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False, related="doc_id.has_message")
    is_given = fields.Boolean(string="Is given", store=False, related="doc_id.is_given")
    name = fields.Char(string="Name", readonly=True, store=False, translate=True, related="doc_id.name")
    notes = fields.Text(string="Notes", store=False, related="doc_id.notes")
    object_id = fields.Reference(string="Object", store=False, selection=[("ufs.base.order", "Order")], related="doc_id.object_id")
    object_name = fields.Char(string="Object Name", store=False, related="doc_id.object_name")
    responsible_ids = fields.Many2many(string="Responsible Users", comodel_name="res.users", related="doc_id.responsible_ids")
    state = fields.Selection(string="Stage", store=False, selection=[("placeholder", "Placeholder")], related="doc_id.state")
