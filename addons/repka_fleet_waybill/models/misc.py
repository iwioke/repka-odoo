from odoo import fields, models

class UfsFleetTrip(models.Model):
    _inherit = "ufs.fleet.trip"
    _order = "start_datetime"
    waybill_id = fields.Many2one(string="Waybill", comodel_name="ufs.waybill")
    cadv_waybill_base_amount_sum = fields.Monetary(string="Cash Advance Sum In Waybill", readonly=True, store=False, related="waybill_id.cadv_base_amount_sum", currency_field="company_currency_id")

class UfsTripCadv(models.Model):
    _inherit = "ufs.trip.cadv"
    is_approval_needed = fields.Boolean(string="Approval Needed", readonly=True, store=False)
    waybill_id = fields.Many2one(string="Waybill", comodel_name="ufs.waybill")

class UfsWaybill(models.Model):
    _name = "ufs.waybill"
    _description = "Fleet Waybill"
    _order = "departure_dttm desc, id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    cadv_base_amount_sum = fields.Monetary(string="Cash Advance sum in base currency", readonly=True, store=False, currency_field="base_currency_id")
    cadv_ids = fields.One2many(string="Cash Advances", comodel_name="ufs.trip.cadv", inverse_name="waybill_id")
    departure_dttm = fields.Datetime(string="Departure Date and Time")
    driver2_docs_ids = fields.Many2many(string="Late Driver 2 Docs", readonly=True, comodel_name="ufs.doc")
    driver2_id = fields.Many2one(string="Driver 2", comodel_name="hr.employee")
    driver_docs_ids = fields.Many2many(string="Late Driver Docs", readonly=True, comodel_name="ufs.doc", relation="ufs_waybill_driver_docs_ids_rel")
    driver_id = fields.Many2one(string="Driver", required=True, comodel_name="hr.employee")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    issue_date = fields.Date(string="Issue Date")
    issue_date_verbose = fields.Char(string="Start Date Localized", readonly=True, store=False)
    kanban_state = fields.Selection(string="Kanban State", selection=[("placeholder", "Placeholder")])
    medic_control_dep_dttm = fields.Datetime(string="Medic Control Departure Date and Time")
    medic_control_ret_dttm = fields.Datetime(string="Medic Control Return Date and Time")
    mileage = fields.Integer(string="Mileage", readonly=True, store=False)
    name = fields.Char(string="Number", help="Unique Waybill Number")
    notes = fields.Text(string="Notes")
    odometer_dep = fields.Integer(string="Odometer Departure")
    odometer_ret = fields.Integer(string="Odometer Return")
    responsible_user_id = fields.Many2one(string="Responsible", comodel_name="res.users")
    return_dttm = fields.Datetime(string="Return Date and Time")
    reverse_trip_ids = fields.One2many(string="Trips", comodel_name="ufs.fleet.trip", inverse_name="waybill_id")
    same_name_int_count = fields.Integer(string="Same Number Counter")
    state = fields.Selection(string="Status", required=True, selection=[("placeholder", "Placeholder")])
    strict_doc_id = fields.Many2one(string="Strict Doc", comodel_name="ufs.strict_doc")
    trailer_docs_ids = fields.Many2many(string="Late Trailer Docs", readonly=True, comodel_name="ufs.doc", relation="ufs_waybill_trailer_docs_ids_rel")
    trailer_id = fields.Many2one(string="Trailer", comodel_name="fleet.vehicle")
    truck_docs_ids = fields.Many2many(string="Late Truck Docs", readonly=True, comodel_name="ufs.doc", relation="ufs_waybill_truck_docs_ids_rel")
    truck_id = fields.Many2one(string="Truck", required=True, comodel_name="fleet.vehicle")
    ufs_trailer_id = fields.Many2one(string="Trailer", comodel_name="ufs.vehicle")
    valid_until_date = fields.Date(string="Valid Until Date and Time", readonly=True)
    valid_until_date_verbose = fields.Char(string="Valid Date Localized", readonly=True, store=False)
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.base_currency_id")
    company_id = fields.Many2one(string="Company", readonly=True, comodel_name="res.company", related="truck_id.company_id")
