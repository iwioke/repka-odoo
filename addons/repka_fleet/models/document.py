from odoo import fields, models

class UfsStrictDoc(models.Model):
    _inherit = "ufs.strict_doc"
    connected_trip_ids = fields.Many2many(string="Connected Trips", comodel_name="ufs.fleet.trip")
    doc_line_ids = fields.Many2many(string="Connected Lines", comodel_name="ufs.fleet.trip.docs_inout.line")
    is_given = fields.Boolean(string="Is Given", readonly=True)
    last_history_state = fields.Selection(string="Last History State", readonly=True, selection=[("placeholder", "Placeholder")])
    on_hand_employee_id = fields.Many2one(string="On Hand Employee", readonly=True, comodel_name="hr.employee")
    on_hand_truck_id = fields.Many2one(string="On Hand Truck", readonly=True, comodel_name="fleet.vehicle")
