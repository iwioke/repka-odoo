from odoo import fields, models

class UfsLocation(models.Model):
    _inherit = "ufs.location"
    home_location_vehicle_ids = fields.One2many(string="Vehicles at home here", comodel_name="fleet.vehicle", inverse_name="home_location_id")
