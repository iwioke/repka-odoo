from odoo import fields, models


class FleetBattery(models.Model):
    _name = "ufs.fleet.battery"
    _description = "Fleet Battery"
    _order = "id"

    active = fields.Boolean(default=True)
    name = fields.Char(string="S/N", required=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        required=True,
        ondelete="restrict",
    )
    installation_date = fields.Date(string="Inst.", required=True)
    utilization_date = fields.Date(string="Utilized")
    notes = fields.Text()
    attachment_file = fields.Binary(string="Guarantee")
    manufacturer_id = fields.Many2one(
        "fleet.vehicle.battery.producer",
        ondelete="set null",
    )
    capacity_id = fields.Many2one(
        "ufs.fleet.battery.capacity",
        ondelete="restrict",
    )


class FleetVehicleBatteryProducer(models.Model):
    _name = "fleet.vehicle.battery.producer"
    _description = "Battery Producer"
    _order = "id"

    name = fields.Char()
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner Link",
        ondelete="set null",
    )


class FleetBatteryCapacity(models.Model):
    _name = "ufs.fleet.battery.capacity"
    _description = "Fleet Battery Capacity"
    _order = "id"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Capacity")
