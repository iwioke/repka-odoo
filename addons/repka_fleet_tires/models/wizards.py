from odoo import fields, models

class TireSwapWizard(models.TransientModel):
    _name = "tire.swap_wizard"
    _description = "tire.swap_wizard"
    left_axis = fields.Integer(string="Axis")
    left_tire = fields.Many2one(string="Left Tire", readonly=True, store=False, comodel_name="fleet.vehicle.tire")
    right_axis = fields.Integer(string="Axis")
    right_tire = fields.Many2one(string="Right Tire", readonly=True, store=False, comodel_name="fleet.vehicle.tire")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")

class UfsFleetVehicleCopyWizard(models.TransientModel):
    _inherit = "ufs.fleet.vehicle_copy_wizard"
    # No fields captured
