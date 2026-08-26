from odoo import fields, models

class UfsFleetMaintenanceRequestWizard(models.TransientModel):
    _name = "ufs_fleet.maintenance_request.wizard"
    _description = "ufs_fleet.maintenance_request.wizard"
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    maintenance_resolution = fields.Text(string="Vehicle Maintenance Resolution")
    request_id = fields.Many2one(string="Request", readonly=True, comodel_name="ufs.fleet.maintenance_request")
    vehicle_id = fields.Many2one(string="Vehicle", readonly=True, store=False, comodel_name="fleet.vehicle", related="request_id.vehicle_id")
