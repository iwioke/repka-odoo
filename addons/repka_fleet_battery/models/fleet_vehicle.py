from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    battery_ids = fields.One2many(
        "ufs.fleet.battery",
        "vehicle_id",
        string="Batteries",
    )
