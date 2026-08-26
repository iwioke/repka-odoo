from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    tire_history_log_ids = fields.One2many(string="Tires History", comodel_name="fleet.vehicle.tire.log", inverse_name="vehicle_id")
    tire_ids = fields.One2many(string="Tires on Vehicle", comodel_name="fleet.vehicle.tire", inverse_name="vehicle_id")

class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"
    # No ufs_base-owned fields captured for this extension

class FleetVehicleTire(models.Model):
    _name = "fleet.vehicle.tire"
    _description = "Vehicle Tire"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    active = fields.Boolean(string="Not Utilized")
    attachment_ids = fields.Many2many(string="Photos", comodel_name="ir.attachment")
    axis = fields.Selection(string="Axis", selection=[("placeholder", "Placeholder")])
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    installation_mileage = fields.Integer(string="Mileage by Start", help="Non-editable if you have something in history")
    mileage = fields.Integer(string="Common Mileage(T)", readonly=True)
    mileage_rate = fields.Integer(string="Mileage Rate")
    mileage_v = fields.Integer(string="Common Mileage", readonly=True)
    name = fields.Char(string="Serial Number", help="Non-editable if you have something in history")
    notes = fields.Text(string="Notes")
    position = fields.Selection(string="Tire Position", selection=[("placeholder", "Placeholder")])
    side = fields.Selection(string="Side", selection=[("placeholder", "Placeholder")])
    tire_history_log_ids = fields.One2many(string="Tires History", comodel_name="fleet.vehicle.tire.log", inverse_name="tire_id")
    tire_model_id = fields.Many2one(string="Tire Model", help="Non-editable if you have something in history", comodel_name="fleet.vehicle.tire.model")
    tire_size_id = fields.Many2one(string="Tire Size", required=True, help="Non-editable if you have something in history", comodel_name="fleet.vehicle.tire.size")
    tire_suffix = fields.Char(string="Suffix", help="Non-editable if you have something in history")
    usage_percentage = fields.Float(string="Usage %(T)", readonly=True, store=False)
    usage_percentage_v = fields.Float(string="Usage %", readonly=True, store=False)
    vehicle_id = fields.Many2one(string="Current Vehicle", comodel_name="fleet.vehicle")
    vendor_id = fields.Many2one(string="Vendor", comodel_name="res.partner")
    fleet_type = fields.Selection(string="Asset Type", readonly=True, store=False, selection=[("placeholder", "Placeholder")], related="vehicle_id.fleet_type")
    producer_id = fields.Many2one(string="Tire Producer", readonly=True, store=False, help="Non-editable if you have something in history", comodel_name="fleet.vehicle.tire.producer", related="tire_model_id.producer_id")
    type_ = fields.Char(string="Typo", readonly=True, store=False, related="tire_size_id.name")

class FleetVehicleTireLog(models.Model):
    _name = "fleet.vehicle.tire.log"
    _description = "Vehicle Tire Log"
    _order = "operation_dt desc, id desc"
    axis = fields.Selection(string="Axis", selection=[("placeholder", "Placeholder")])
    is_editable = fields.Boolean(string="Is Editable", readonly=True, store=False)
    line_close_dt = fields.Date(string="Next")
    mileage_by_odometers = fields.Integer(string="Mileage by Od.(F)")
    mileage_by_trips = fields.Integer(string="Mileage by trips", readonly=True, store=False)
    mileage_v = fields.Integer(string="Mileage by Od.", readonly=True, store=False)
    odometer_start = fields.Integer(string="Odometer On")
    odometer_v_start = fields.Integer(string="Odometer Start By Od.")
    operation_dt = fields.Date(string="When", required=True)
    position = fields.Selection(string="Tire Position", selection=[("placeholder", "Placeholder")])
    side = fields.Selection(string="Side", selection=[("placeholder", "Placeholder")])
    tire_id = fields.Many2one(string="Tire", comodel_name="fleet.vehicle.tire")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    fleet_type = fields.Selection(string="Asset Type", readonly=True, store=False, selection=[("placeholder", "Placeholder")], related="tire_id.fleet_type")

class FleetVehicleTireModel(models.Model):
    _name = "fleet.vehicle.tire.model"
    _description = "fleet.vehicle.tire.model"
    mileage_rate = fields.Integer(string="Mileage Rate")
    name = fields.Char(string="Name")
    producer_id = fields.Many2one(string="Producer", required=True, comodel_name="fleet.vehicle.tire.producer")

class FleetVehicleTireProducer(models.Model):
    _name = "fleet.vehicle.tire.producer"
    _description = "Tire Producer"
    name = fields.Char(string="Name")
    partner_id = fields.Many2one(string="Partner Link", comodel_name="res.partner")

class FleetVehicleTireSize(models.Model):
    _name = "fleet.vehicle.tire.size"
    _description = "Tire Size"
    name = fields.Char(string="Name", readonly=True)
    profile = fields.Integer(string="Profile")
    radius = fields.Float(string="Radius")
    width = fields.Integer(string="Width")
