from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    at_home_location = fields.Boolean(string="Is at home location")
    equipment_ids = fields.One2many(string="Equipments", comodel_name="ufs.base.equipment", inverse_name="vehicle_id")
    fleet_type = fields.Selection(string="Asset Type", readonly=True, selection=[("placeholder", "Placeholder")], related="model_id.vehicle_type")
    fleet_type_has_cargo_bay = fields.Boolean(string="Has Cargo Bay", readonly=True, store=False, related="power_type.has_cargo_bay")
    home_location_id = fields.Many2one(string="Home Location", comodel_name="ufs.location")
    internal_name = fields.Char(string="Internal Name")
    last_loc_datetime = fields.Datetime(string="Last Loc Datetime")
    longitude_latitude = fields.Char(string="Tracking Coordinates")
    main_odometer_source = fields.Selection(string="Main Odometer Source", selection=[("placeholder", "Placeholder")])
    max_load_weight = fields.Float(string="Max load weight")
    own_trailer_id = fields.Many2one(string="Own Trailer", comodel_name="fleet.vehicle")
    power_type = fields.Many2one(string="Power Unit Type", comodel_name="fleet.vehicle.power_type")
    responsible_emp_id = fields.Many2one(string="Responsible Employee", comodel_name="hr.employee")
    tracking_provider_id = fields.Many2one(string="Tracking Provider", comodel_name="ufs.tracking.system")
    tracking_system = fields.Selection(string="Parse Schema", readonly=True, store=False, selection=[("placeholder", "Placeholder")], related="tracking_provider_id.parse_schema")
    tracking_system_uid = fields.Char(string="Tracking UID")
    trailer_type = fields.Many2one(string="Trailer Type", comodel_name="fleet.vehicle.trailer_type")
    ufs_vehicle_id = fields.Many2one(string="UFS Vehicle", comodel_name="ufs.vehicle")
    verbose_location_small = fields.Char(string="Current location", readonly=True)
    verbose_tracking_location = fields.Text(string="Truck location by Tracking System", readonly=True)

class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"
    vehicle_type = fields.Selection(string="Vehicle Type", required=True, selection=[("placeholder", "Placeholder")])

class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"
    fuel_consumption_can = fields.Float(string="Fuel Consumption Can")
    fuel_level_dut = fields.Float(string="Fuel Level Dut")
    fuel_level_perc = fields.Float(string="Fuel Level Percentage")
    fuel_level_v = fields.Float(string="Fuel Level Vehicle")
    is_a_refuel_entry = fields.Boolean(string="Is a Refuel Entry")
    longitude_latitude = fields.Char(string="Tracking Coordinates")
    odometer_can = fields.Float(string="Odometer CAN")
    odometer_gps = fields.Float(string="Odometer GPS")
    operation_dttm = fields.Datetime(string="Operation Datetime")
    raw_data = fields.Text(string="Raw Data")
    refuel_amount = fields.Float(string="Refuel Amount")
    special_data = fields.Text(string="Special Data (JSON)")
    verbose_address = fields.Char(string="Verbose Address")

class FleetVehiclePowerType(models.Model):
    _name = "fleet.vehicle.power_type"
    _description = "Fleet Vehicle Power Unit Type"
    has_cargo_bay = fields.Boolean(string="Has Cargo Bay")
    is_refrigerator = fields.Boolean(string="Refrigerator")
    name = fields.Char(string="Power Type", translate=True)

class FleetVehicleTrailerType(models.Model):
    _name = "fleet.vehicle.trailer_type"
    _description = "Fleet Vehicle Trailer Type"
    is_refrigerator = fields.Boolean(string="Refrigerator")
    name = fields.Char(string="Trailer Type", translate=True)

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    citizen_country_id = fields.Many2one(string="Citizen of", comodel_name="res.country")
    fathername = fields.Char(string="Father Name")
    firstname = fields.Char(string="First name")
    is_driver = fields.Boolean(string="Is a driver")
    is_trainee = fields.Boolean(string="Is a trainee")
    lastname = fields.Char(string="Last name")
    passport_date = fields.Date(string="Passport Issue Date")
    passport_name = fields.Char(string="Passport Name")
    passport_number = fields.Char(string="Passport Number")
    passport_place = fields.Char(string="Passport Issue Place")
    passport_series = fields.Char(string="Passport Series")
    private_number = fields.Char(string="Private Number")
    u_guid = fields.Char(string="GUID")
    ufs_driver_id = fields.Many2one(string="UFS Driver", comodel_name="ufs.driver")

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    citizen_country_id = fields.Many2one(string="Citizen of", comodel_name="res.country")
    fathername = fields.Char(string="Father Name")
    firstname = fields.Char(string="First name")
    is_driver = fields.Boolean(string="Is a driver")
    is_trainee = fields.Boolean(string="Is a trainee")
    lastname = fields.Char(string="Last name")
    passport_date = fields.Date(string="Passport Issue Date")
    passport_name = fields.Char(string="Passport Name")
    passport_number = fields.Char(string="Passport Number")
    passport_place = fields.Char(string="Passport Issue Place")
    passport_series = fields.Char(string="Passport Series")
    private_number = fields.Char(string="Private Number")
    u_guid = fields.Char(string="GUID")

class HrEmployeePublic(models.AbstractModel):
    _inherit = "hr.employee.public"
    citizen_country_id = fields.Many2one(string="Citizen of", comodel_name="res.country")
    fathername = fields.Char(string="Father Name")
    firstname = fields.Char(string="First name")
    is_driver = fields.Boolean(string="Is a driver")
    is_trainee = fields.Boolean(string="Is a trainee")
    lastname = fields.Char(string="Last name")
    passport_date = fields.Date(string="Passport Issue Date")
    passport_name = fields.Char(string="Passport Name")
    passport_number = fields.Char(string="Passport Number")
    passport_place = fields.Char(string="Passport Issue Place")
    passport_series = fields.Char(string="Passport Series")
    private_number = fields.Char(string="Private Number")
    u_guid = fields.Char(string="GUID")

class ProductProduct(models.Model):
    _inherit = "product.product"
    # No ufs_base-owned fields captured for this extension
