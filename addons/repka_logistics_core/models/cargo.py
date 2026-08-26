from odoo import fields, models

class UfsCargo(models.Model):
    _name = "ufs.cargo"
    _description = "Cargo"
    active = fields.Boolean(string="Active")
    adr_class = fields.Char(string="ADR Class")
    cargo_code = fields.Char(string="Cargo Code")
    is_adr = fields.Boolean(string="ADR")
    name = fields.Char(string="Name", required=True)

class UfsCargoLine(models.Model):
    _name = "ufs.cargo_line"
    _description = "Cargo Line"
    adr_class = fields.Char(string="ADR Class")
    base_weight_total = fields.Float(string="Base Weight")
    cargo_id = fields.Many2one(string="Cargo", comodel_name="ufs.cargo")
    cargo_packing = fields.Char(string="Cargo Packing")
    cargo_value = fields.Monetary(string="Cargo Commercial Value")
    cargo_volume = fields.Float(string="Volume in m3")
    code = fields.Char(string="Code")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    details = fields.Text(string="Cargo Details", help="no additional details")
    is_adr = fields.Boolean(string="ADR", readonly=True)
    loading_type = fields.Many2one(string="Load", comodel_name="ufs.loading_type")
    name = fields.Char(string="Cargo Name")
    pallet_count = fields.Integer(string="Pallets")
    temp_mode = fields.Selection(string="Temperature Mode", selection=[("placeholder", "Placeholder")])
    temp_requirements = fields.Char(string="Temperature Requirements (legacy)")
    temp_value = fields.Float(string="Temperature, °C")
    trailer_type = fields.Many2one(string="Trailer Type", comodel_name="fleet.vehicle.trailer_type")
    units_count = fields.Float(string="Units Count")
    units_uom_id = fields.Many2one(string="Units UOM", comodel_name="uom.uom")
    weight = fields.Float(string="Weight")
    weight_uom_id = fields.Many2one(string="Weight UOM", comodel_name="uom.uom")
