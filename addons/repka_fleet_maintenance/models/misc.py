from odoo import fields, models

class UfsFleetMaintenance(models.Model):
    _name = "ufs.fleet.maintenance"
    _description = "UFS Fleet Maintenance Model"
    active = fields.Boolean(string="Active", readonly=True)
    alert_range = fields.Float(string="Alert Range")
    bounded_maintenance_log_id = fields.Many2one(string="Service Log", readonly=True, store=False, comodel_name="fleet.vehicle.log.services")
    current_activity_id = fields.Many2one(string="Current Activity", comodel_name="mail.activity")
    employee_id = fields.Many2one(string="Responsive", required=True, comodel_name="hr.employee")
    last_check = fields.Datetime(string="Last Check", required=True)
    last_value = fields.Float(string="Last Value")
    name = fields.Char(string="Name")
    operation_type_id = fields.Many2one(string="Operation Type", required=True, comodel_name="ufs.fleet.maintenance.type")
    period = fields.Float(string="Period")
    res_id = fields.Integer(string="Id")
    res_model = fields.Char(string="Model")
    units_to_check = fields.Float(string="Units to Check rem.", readonly=True)
    units_to_check_to_days = fields.Float(string="Days to Check rem.", readonly=True)
    units_to_check_tr = fields.Float(string="To Check", readonly=True)
    vehicle_id = fields.Many2one(string="Asset", required=True, comodel_name="fleet.vehicle")
    period_type = fields.Selection(string="Period Type", readonly=True, store=False, selection=[("placeholder", "Placeholder")], related="operation_type_id.period_type")

class UfsFleetMaintenanceType(models.Model):
    _name = "ufs.fleet.maintenance.type"
    _description = "Fleet Maintenance Type"
    default_alert_range = fields.Float(string="Default Alert", required=True)
    default_period = fields.Float(string="Default Period Length", required=True)
    name = fields.Char(string="Name", required=True)
    period_type = fields.Selection(string="Period Type", required=True, selection=[("placeholder", "Placeholder")])
    service_type_id = fields.Many2one(string="Type", help="Service type purchased with this expense", comodel_name="fleet.service.type")

class UfsFleetMaintenanceRequest(models.Model):
    _inherit = "ufs.fleet.maintenance_request"
    _order = "create_date desc, state asc"
    bounded_maintenance_log_id = fields.Many2one(string="Service Log", readonly=True, store=False, comodel_name="fleet.vehicle.log.services")

class UfsFleetTrip(models.Model):
    _inherit = "ufs.fleet.trip"
    _order = "start_datetime"
    block_write_by_maint = fields.Boolean(string="Block Write By Maint", readonly=True, store=False)
