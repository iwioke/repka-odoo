from odoo import fields, models

class UfsFleetRefuelUpdateWizard(models.TransientModel):
    _name = "ufs.fleet.refuel.update.wizard"
    _description = "Refuel Update Wizard"
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    provider_id = fields.Many2one(string="Provider", required=True, comodel_name="ufs.fuel.api.provider")
    update_existing = fields.Boolean(string="Update exising", help="Will update existing transactions only! No new created!")

class UfsFleetRefuelVUpdateWizard(models.TransientModel):
    _name = "ufs.fleet.refuel.v_update_wizard"
    _description = "Update Vehicle For Refuels Wizard"
    refuel_ids = fields.Many2many(string="Refuels", comodel_name="ufs.fleet.refuel")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")

class UfsFuelApiCards(models.TransientModel):
    _name = "ufs.fuel.api.cards"
    _description = "Fuel API Card List"
    cards_list = fields.Text(string="Cards List")
