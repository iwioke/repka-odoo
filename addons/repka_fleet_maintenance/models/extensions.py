from odoo import fields, models

class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"
    is_a_category = fields.Boolean(string="Is a Category")

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    maintenance_ids = fields.One2many(string="Planned Maintenances", comodel_name="ufs.fleet.maintenance", inverse_name="vehicle_id")
    overdue_maintenance_ids = fields.Many2many(string="Overdue Maint", readonly=True, comodel_name="ufs.fleet.maintenance")

class FleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"
    account_move_ids = fields.Many2many(string="Bills", comodel_name="account.move")
    amount = fields.Monetary(string="Amount", readonly=True, currency_field="base_currency_id")
    base_amount = fields.Monetary(string="Base Amount", readonly=True, currency_field="base_currency_id")
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    cost_line_ids = fields.One2many(string="Cost Lines", comodel_name="fleet.vehicle.log.services.line", inverse_name="service_id")
    currency_id = fields.Many2one(string="Currency", required=True, comodel_name="res.currency")
    fact_date_from = fields.Date(string="Fact From")
    fact_date_to = fields.Date(string="Fact To")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    last_log_message = fields.Html(string="Last Log Message", readonly=True, store=False)
    maintenance_plan_id = fields.Many2one(string="Maintenance Generator", comodel_name="ufs.fleet.maintenance")
    maintenance_request_id = fields.Many2one(string="Maintenance Request", comodel_name="ufs.fleet.maintenance_request")
    plan_date_from = fields.Date(string="Plan From")
    plan_date_to = fields.Date(string="Plan To")
    repair_place = fields.Selection(string="Repair Place", required=True, selection=[("placeholder", "Placeholder")])
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.base_currency_id")

class FleetVehicleLogServicesLine(models.Model):
    _name = "fleet.vehicle.log.services.line"
    _description = "Fleet Log Service Line"
    amount = fields.Monetary(string="Amount", readonly=True, currency_field="currency_id")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    move_line_ids = fields.One2many(string="Move Lines", comodel_name="account.move.line", inverse_name="service_line_id")
    price_unit = fields.Monetary(string="Price", currency_field="currency_id")
    product_id = fields.Many2one(string="Product", required=True, comodel_name="product.product")
    qty = fields.Float(string="Qty")
    service_id = fields.Many2one(string="Service", comodel_name="fleet.vehicle.log.services")
    tax_ids = fields.Many2many(string="Tax", comodel_name="account.tax")
    company_id = fields.Many2one(string="Company", readonly=True, store=False, comodel_name="res.company", related="service_id.company_id")

class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"
    # No ufs_base-owned fields captured for this extension
