from odoo import fields, models

class UfsDoc(models.Model):
    _name = "ufs.doc"
    _description = "Document"
    _inherit = ['mail.thread']
    attached_scan = fields.Binary(string="Attached Scan")
    attached_scan_fname = fields.Char(string="FName")
    color = fields.Integer(string="Color Index", readonly=True, store=False)
    display_prefix = fields.Char(string="Display Prefix")
    doc_type = fields.Many2one(string="Doc Type", required=True, comodel_name="ufs.doc.type")
    expiration_date = fields.Date(string="Expiration Date", required=True)
    full_name = fields.Char(string="Full Name", readonly=True, store=False)
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    is_given = fields.Boolean(string="Is given")
    notes = fields.Text(string="Notes")
    object_id = fields.Reference(string="Object", selection=[("ufs.base.order", "Order")])
    object_name = fields.Char(string="Object Name")
    responsible_ids = fields.Many2many(string="Responsible Users", comodel_name="res.users")
    state = fields.Selection(string="Stage", selection=[("placeholder", "Placeholder")])
    days_to_renew = fields.Integer(string="Days To Renew Reminder", readonly=True, store=False, related="doc_type.days_to_renew")
    name = fields.Char(string="Name", readonly=True, store=False, translate=True, related="doc_type.name")

class UfsDocType(models.Model):
    _name = "ufs.doc.type"
    _description = "Base Document Types"
    active = fields.Boolean(string="Active")
    days_to_renew = fields.Integer(string="Days To Renew Reminder")
    models_selection = fields.Selection(string="Models Selection", selection=[("placeholder", "Placeholder")])
    name = fields.Char(string="Name", required=True, translate=True)
    responsible_ids = fields.Many2many(string="Responsible Users", comodel_name="res.users")

class UfsStrictDoc(models.Model):
    _name = "ufs.strict_doc"
    _description = "Strict Document"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    active = fields.Boolean(string="Active")
    additional_info = fields.Char(string="Additional Info")
    base_cost = fields.Monetary(string="Cost in base currency", readonly=True, currency_field="base_currency_id")
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, comodel_name="res.currency")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    cost = fields.Monetary(string="Cost", currency_field="base_currency_id")
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    doc_type = fields.Selection(string="Doc Type", selection=[("placeholder", "Placeholder")])
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    is_used = fields.Boolean(string="Is Used")
    issue_date = fields.Date(string="Issue Date")
    name = fields.Char(string="Unique number", required=True)
    partner_id = fields.Many2one(string="Vendor", comodel_name="res.partner")
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    returned_to_vendor_date = fields.Date(string="Returned to Vendor")
    subtype_id = fields.Many2one(string="Subtype", comodel_name="ufs.strict_doc.subtype")
    use_date = fields.Date(string="Use date")
    valid_date = fields.Date(string="Valid until")
    expiration_date = fields.Date(string="Valid until", readonly=True, store=False, related="valid_date")
    use_type = fields.Selection(string="Use Type", readonly=True, store=False, selection=[("placeholder", "Placeholder")], related="subtype_id.use_type")

class UfsStrictDocSubtype(models.Model):
    _name = "ufs.strict_doc.subtype"
    _description = "Strict Document Subtype"
    active = fields.Boolean(string="Active")
    doc_type = fields.Selection(string="Doc Type", required=True, selection=[("placeholder", "Placeholder")])
    name = fields.Char(string="Name")
    note = fields.Text(string="Note")
    use_type = fields.Selection(string="Use Type", selection=[("placeholder", "Placeholder")])
