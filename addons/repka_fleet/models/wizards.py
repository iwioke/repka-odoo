from odoo import fields, models

class HrEmployeeCopyWizard(models.TransientModel):
    _name = "hr.employee.copy_wizard"
    _description = "hr.employee.copy_wizard"
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    copy_documents = fields.Boolean(string="Copy Documents")
    employee_ids = fields.Many2many(string="Employees", readonly=True, comodel_name="hr.employee")
    new_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")

class HrEmployeeUpdateRatesWizard(models.TransientModel):
    _name = "hr.employee.update_rates_wizard"
    _description = "Update Employee Rates Wizard"
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    date_from = fields.Date(string="Date From", required=True)
    employee_ids = fields.Many2many(string="Employees", required=True, comodel_name="hr.employee")
    new_value = fields.Float(string="New Value", required=True)
    rate_type = fields.Selection(string="Rate Type", required=True, selection=[("placeholder", "Placeholder")])

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    add_economy_to_drivers_salary = fields.Boolean(string="Take Burnout from Drivers salary")
    add_stop_point_for_all_trips = fields.Boolean(string="Add Stop Point for All Trips", help="When enabled, a stop (end) point is always added to a trip even if the last route point is an unload point. Only relevant in points mode.")
    cadv_responsible_user_ids = fields.Many2many(string="Cash Advance Responsible Users", comodel_name="res.users", related="company_id.cadv_responsible_user_ids")
    cadv_trip_limit = fields.Monetary(string="Cash Advances Limit for a Trip", store=False, related="company_id.cadv_trip_limit", currency_field="currency_id")
    driver_salary_currency_mode = fields.Selection(string="Driver Salary Currency Mode", required=True, help="Determines which currency is used to compute and display driver payment sum, and to generate salary expenses.", selection=[("placeholder", "Placeholder")])
    hide_advances_in_trip = fields.Boolean(string="Hide Advances in Trips")
    hide_fact_arrival_dttm = fields.Boolean(string="Hide Fact Arrival Datetime", help="Hide the 'Fact Arrival' column from trip point lists, portal, and driver app.")
    not_use_segments_and_norms = fields.Boolean(string="Not Use Segments and Norms")
    second_driver_salary_coef = fields.Float(string="If we have 2 drivers, this coefficient will be used for recalc")
    service_name_contract = fields.Boolean(string="Contract")
    service_name_documents = fields.Boolean(string="Documents")
    service_name_driver = fields.Boolean(string="Driver")
    service_name_incoming_ref = fields.Boolean(string="Incoming Ref.")
    service_name_loading_date = fields.Boolean(string="Load Date")
    service_name_unloading_date = fields.Boolean(string="Unload Date")
    service_name_vehicle = fields.Boolean(string="Vehicle")
    show_cadv_paid_button = fields.Boolean(string="Show 'Paid' Button on Cash Advances", help="Display a 'Mark as Paid' button on cash advances in Done state. Useful for versions without 1C integration to manually track payment completion.")
    show_can_consumption = fields.Boolean(string="Show CAN Consumption")
    show_can_distance = fields.Boolean(string="Show CAN Distance")
    show_fls_data = fields.Boolean(string="Show Fuel Level Sensor (FLS) Data")
    take_burnout_from_drivers_salary = fields.Boolean(string="Take Burnout from Drivers salary")
    trailer_consumption_schema = fields.Selection(string="Trailer Consumption Schema", required=True, selection=[("placeholder", "Placeholder")])
    ufs_trip_driver_rate_by_segments = fields.Boolean(string="Specify driver rates pro trip segment")
    use_costs_in_fleet_order = fields.Boolean(string="Use Costs in Transport Order")

class UfsCadvRequestApprovalWizard(models.TransientModel):
    _name = "ufs.cadv.request.approval.wizard"
    _description = "CADV Request Approval Wizard"
    available_user_ids = fields.Many2many(string="Available Users", readonly=True, comodel_name="res.users")
    cadv_id = fields.Many2one(string="Cash Advance", required=True, readonly=True, comodel_name="ufs.trip.cadv")
    message = fields.Text(string="Message", required=True, help="Message to be included in the activity notification")
    user_ids = fields.Many2many(string="Responsible Users", required=True, help="Select users who should approve this cash advance", comodel_name="res.users", relation="ufs_cadv_request_approval_wizard_user_ids_rel")
    company_id = fields.Many2one(string="Company", readonly=True, store=False, comodel_name="res.company", related="cadv_id.company_id")
    trip_id = fields.Many2one(string="Trip", readonly=True, store=False, comodel_name="ufs.fleet.trip", related="cadv_id.trip_id")

class UfsFleetAddOrderLine(models.TransientModel):
    _name = "ufs.fleet.add_order.line"
    _description = "Add Order Wizard Line"
    _order = "datetime, id"
    _inherit = ['mail.thread']
    address_auto = fields.Char(string="Address", readonly=True)
    datetime = fields.Datetime(string="Date and Time")
    fact_arrival_dttm = fields.Datetime(string="Fact Arrival")
    fact_leave_dttm = fields.Datetime(string="Fact Leave")
    free_time = fields.Float(string="Free Time")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    is_first = fields.Boolean(string="Is First", readonly=True, store=False)
    is_last = fields.Boolean(string="Is Last", readonly=True, store=False)
    line_type = fields.Selection(string="Type", selection=[("placeholder", "Placeholder")])
    location_id = fields.Many2one(string="Location", comodel_name="ufs.location")
    name = fields.Char(string="Name", readonly=True, store=False)
    notes = fields.Text(string="Notes")
    order_id = fields.Many2one(string="Order", comodel_name="ufs.fleet.order")
    owner_partner_id = fields.Many2one(string="Owner Partner", comodel_name="res.partner")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    wizard_id = fields.Many2one(string="Wizard", comodel_name="ufs.fleet.trip.add_order_wizard")
    location_postcode = fields.Char(string="Postcode", readonly=True, store=False, related="location_id.postcode")

class UfsFleetEmployeeLetterWizard(models.TransientModel):
    _name = "ufs.fleet.employee.letter_wizard"
    _description = "ufs.fleet.employee.letter_wizard"
    employee_id = fields.Many2one(string="Employee", readonly=True, comodel_name="hr.employee")
    letter_driver_place_name = fields.Char(string="Place(p 22)")
    letter_driver_sign_date = fields.Date(string="Sign Date(p 22)")
    letter_from = fields.Datetime(string="From")
    letter_place_name = fields.Char(string="Place")
    letter_sign_date = fields.Date(string="Sign Date")
    letter_to = fields.Datetime(string="To")
    company_id = fields.Many2one(string="Company", readonly=True, store=False, comodel_name="res.company", related="employee_id.company_id")

class UfsFleetOrderPartnerInfoWizard(models.TransientModel):
    _name = "ufs.fleet.order.partner_info_wizard"
    _description = "Order Partner Info Wizard"
    message = fields.Text(string="Message")
    order_id = fields.Many2one(string="Order", readonly=True, comodel_name="ufs.fleet.order")

class UfsFleetReorderWizard(models.TransientModel):
    _name = "ufs.fleet.reorder_wizard"
    _description = "Reorder Wizard"
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    freight_amount = fields.Monetary(string="Freight Rate", currency_field="currency_id")
    name = fields.Char(string="Name")
    source_order_id = fields.Many2one(string="Order", comodel_name="ufs.fleet.order")
    target_company_id = fields.Many2one(string="Order Company", comodel_name="res.company")
    target_trailer_id = fields.Many2one(string="Target Trailer", comodel_name="fleet.vehicle")
    target_vehicle_id = fields.Many2one(string="Target Truck", comodel_name="fleet.vehicle")
    source_company_id = fields.Many2one(string="Order Company", readonly=True, store=False, comodel_name="res.company", related="source_order_id.company_id")

class UfsFleetTripAddOrderWizard(models.TransientModel):
    _name = "ufs.fleet.trip.add_order_wizard"
    _description = "Add Order to Trip Wizard"
    freight_amount = fields.Monetary(string="Freight Rate", currency_field="currency_id")
    name = fields.Char(string="Name")
    source_trip_id = fields.Many2one(string="Trip", comodel_name="ufs.fleet.trip")
    target_company_id = fields.Many2one(string="Order Company", comodel_name="res.company")
    target_end_point_id = fields.Many2one(string="Switch Location", comodel_name="ufs.fleet.order.line")
    target_order_id = fields.Many2one(string="Order", comodel_name="ufs.fleet.order")
    target_order_line_ids = fields.One2many(string="Order Lines", comodel_name="ufs.fleet.add_order.line", inverse_name="wizard_id")
    currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency", related="target_order_id.currency_id")
    source_company_id = fields.Many2one(string="Trip Company", readonly=True, store=False, comodel_name="res.company", related="source_trip_id.company_id")

class UfsFleetTripDriverSwitchWizard(models.TransientModel):
    _name = "ufs.fleet.trip.driver_switch_wizard"
    _description = "Trip Driver Switch Wizard"
    source_trip_id = fields.Many2one(string="Source Trip", comodel_name="ufs.fleet.trip")
    switch_location_id = fields.Many2one(string="Driver Switch Place", required=True, comodel_name="ufs.location")
    target_company_id = fields.Many2one(string="Company", comodel_name="res.company")
    target_driver2_id = fields.Many2one(string="Target Trip Driver 2", comodel_name="hr.employee")
    target_driver_id = fields.Many2one(string="Target Trip Driver 1", comodel_name="hr.employee")
    target_start_datetime = fields.Datetime(string="Start Datetime")
    target_trailer_id = fields.Many2one(string="Target Trip Trailer", comodel_name="fleet.vehicle")
    target_trip_id = fields.Many2one(string="Target Trip", comodel_name="ufs.fleet.trip")
    target_vehicle_id = fields.Many2one(string="Target Trip Truck", comodel_name="fleet.vehicle")
    source_driver2_id = fields.Many2one(string="Driver 2", readonly=True, store=False, comodel_name="hr.employee", related="source_trip_id.driver2_id")
    source_driver_id = fields.Many2one(string="Driver", readonly=True, store=False, comodel_name="hr.employee", related="source_trip_id.driver_id")
    source_trailer_id = fields.Many2one(string="Trailer", readonly=True, store=False, comodel_name="fleet.vehicle", related="source_trip_id.trailer_id")
    source_vehicle_id = fields.Many2one(string="Truck", readonly=True, store=False, comodel_name="fleet.vehicle", related="source_trip_id.vehicle_id")

class UfsFleetTripPartnerInfoWizard(models.TransientModel):
    _name = "ufs.fleet.trip.partner_info_wizard"
    _description = "Trip Partner Info Wizard"
    message = fields.Text(string="Message")
    trip_id = fields.Many2one(string="Trip", readonly=True, comodel_name="ufs.fleet.trip")

class UfsFleetTripSwitchWizard(models.TransientModel):
    _name = "ufs.fleet.trip.switch_wizard"
    _description = "ufs.fleet.trip.switch_wizard"
    send_switch_letter = fields.Boolean(string="Send Switch Letter")
    source_trip_id = fields.Many2one(string="Source Trip", comodel_name="ufs.fleet.trip")
    switch_location_id = fields.Many2one(string="Switch Place", required=True, comodel_name="ufs.location")
    target_company_id = fields.Many2one(string="Target Company", comodel_name="res.company")
    target_driver2_id = fields.Many2one(string="Target Trip Driver 2", comodel_name="hr.employee")
    target_driver_id = fields.Many2one(string="Target Trip Driver 1", comodel_name="hr.employee")
    target_order_ids = fields.Many2many(string="Target Trip Orders", comodel_name="ufs.fleet.order", relation="ufs_fleet_trip_switch_wizard_target_order_ids_rel")
    target_start_datetime = fields.Datetime(string="Start Datetime")
    target_trailer_id = fields.Many2one(string="Target Trip Trailer", comodel_name="fleet.vehicle")
    target_trip_id = fields.Many2one(string="Target Trip", comodel_name="ufs.fleet.trip")
    target_vehicle_id = fields.Many2one(string="Target Trip Truck", comodel_name="fleet.vehicle")
    source_driver2_id = fields.Many2one(string="Driver 2", readonly=True, store=False, comodel_name="hr.employee", related="source_trip_id.driver2_id")
    source_driver_id = fields.Many2one(string="Driver", readonly=True, store=False, comodel_name="hr.employee", related="source_trip_id.driver_id")
    source_trailer_id = fields.Many2one(string="Trailer", readonly=True, store=False, comodel_name="fleet.vehicle", related="source_trip_id.trailer_id")
    source_trip_order_ids = fields.Many2many(string="Orders in trip", readonly=True, comodel_name="ufs.fleet.order", related="source_trip_id.order_ids")
    source_vehicle_id = fields.Many2one(string="Truck", readonly=True, store=False, comodel_name="fleet.vehicle", related="source_trip_id.vehicle_id")

class UfsFleetTripTimeLine(models.TransientModel):
    _name = "ufs.fleet.trip_time.line"
    _description = "Trip Time Report Line"
    duration_trips = fields.Float(string="Duration by Trips in hrs.")
    duration_trips_days = fields.Float(string="Duration by Trips in days.")
    truck_id = fields.Many2one(string="Truck", comodel_name="fleet.vehicle")

class UfsFleetTripTimeWizard(models.TransientModel):
    _name = "ufs.fleet.trip_time.wizard"
    _description = "Trip Time Utility Report Wizard"
    end_date = fields.Date(string="Report End", required=True)
    start_date = fields.Date(string="Report Start", required=True)

class UfsFleetVehicleCopyWizard(models.TransientModel):
    _name = "ufs.fleet.vehicle_copy_wizard"
    _description = "ufs.fleet.vehicle_copy_wizard"
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    copy_crew = fields.Boolean(string="Copy Crew")
    copy_documents = fields.Boolean(string="Copy Documents")
    copy_tires = fields.Boolean(string="Copy Tires")
    is_single = fields.Boolean(string="Is Single", readonly=True, store=False)
    license_plate = fields.Char(string="License Plate", help="Used only when copying a single vehicle. Auto-suffixed otherwise.")
    vehicle_ids = fields.Many2many(string="Vehicles", readonly=True, comodel_name="fleet.vehicle")
