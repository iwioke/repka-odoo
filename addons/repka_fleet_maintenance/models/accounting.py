from odoo import fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    cost_line_id = fields.Many2one(string="Cost Line", comodel_name="fleet.vehicle.log.services.line")
    vehicle_service_id = fields.Many2one(string="Service Order", comodel_name="fleet.vehicle.log.services")
