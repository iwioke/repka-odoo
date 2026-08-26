from odoo import fields, models

class MailComposeMessage(models.TransientModel):
    _name = "mail.compose.message"
    _description = "Email composition wizard"
    print_stamp = fields.Boolean(string="Print Stamp", help="Render generated report attachments with the company stamp.")
    show_print_stamp = fields.Boolean(string="Show Print Stamp", readonly=True, store=False)

class ResConfigSettings(models.TransientModel):
    _name = "res.config.settings"
    _description = "Config Settings"
    external_number_editable = fields.Boolean(string="External Number Editable")
    group_show_guid = fields.Boolean(string="Show GUID fields", help="If enabled, GUID fields will be visible in forms for users in the group.")
    invoicing_dept_email = fields.Char(string="Invoicing Department Email", help="Email address of the invoicing department for advance invoice requests.")
    lock_freight_on_act = fields.Boolean(string="Lock Freight Amount When Act Issued")
    use_contract_checks = fields.Boolean(string="Use Contract Checks")
    use_extended_naming = fields.Boolean(string="Use Extended Naming")
    use_orders_based_credit_limit = fields.Boolean(string="Orders Based Credit Limit")

class UfsGrantCompanyAccess(models.TransientModel):
    _name = "ufs.grant.company.access"
    _description = "Grant Access to a company (wizard)"
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    user_ids = fields.Many2many(string="Users", required=True, comodel_name="res.users")

class UfsTrackingSystemLocationsWizard(models.TransientModel):
    _name = "ufs.tracking.system.locations.wizard"
    _description = "Tracking System Locations Fetch Wizard"
    date_from = fields.Datetime(string="From", required=True)
    date_to = fields.Datetime(string="To", required=True)
    tracking_system_id = fields.Many2one(string="Tracking System", required=True, comodel_name="ufs.tracking.system")

class UfsTrackingSystemRefillWizard(models.TransientModel):
    _name = "ufs.tracking.system.refill.wizard"
    _description = "Tracking System Refuel Fetch Wizard"
    date_from = fields.Datetime(string="Start Date", required=True)
    date_to = fields.Datetime(string="End Date", required=True)
    tracking_system_id = fields.Many2one(string="Tracking System", required=True, comodel_name="ufs.tracking.system")

class UfsTrackingVlist(models.TransientModel):
    _name = "ufs.tracking.vlist"
    _description = "ufs.tracking.vlist"
    vehicles_list = fields.Text(string="Vehicles list")
