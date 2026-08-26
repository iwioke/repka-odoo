from odoo import fields, models

class UfsBaseEquipment(models.Model):
    _name = "ufs.base.equipment"
    _description = "Base Equipment"
    _inherit = ['mail.thread']
    active = fields.Boolean(string="Can Be Used")
    amount = fields.Monetary(string="Total Cost", readonly=True, currency_field="base_currency_id")
    amount_base = fields.Monetary(string="Amount In Base Currency", readonly=True, store=False, currency_field="base_currency_id")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    employee_id = fields.Many2one(string="Employee/Driver", comodel_name="hr.employee")
    expiry_date = fields.Date(string="Expiry Date")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    price_unit = fields.Monetary(string="Unit Price", currency_field="base_currency_id")
    product_id = fields.Many2one(string="Equipment", comodel_name="product.product")
    product_qty = fields.Float(string="Quantity", required=True)
    serial_number = fields.Char(string="Serial Number")
    use_log_ids = fields.One2many(string="Use History", comodel_name="ufs.base.equipment.log", inverse_name="equipment_id")
    use_start = fields.Date(string="Use start")
    vehicle_id = fields.Many2one(string="Asset", comodel_name="fleet.vehicle")
    base_currency_id = fields.Many2one(string="Base Currency", readonly=True, store=False, comodel_name="res.currency", related="company_id.currency_id")
    name = fields.Char(string="Name", readonly=True, store=False, translate=True, related="product_id.name")
    product_uom_id = fields.Many2one(string="Unit of Measure", readonly=True, store=False, help="Default unit of measure used for all stock operations.", comodel_name="uom.uom", related="product_id.uom_id")

class UfsBaseEquipmentLine(models.Model):
    _name = "ufs.base.equipment.line"
    _description = "Equipment Line"
    equipment_id = fields.Many2one(string="Equipment", required=True, comodel_name="ufs.base.equipment")
    employee_id = fields.Many2one(string="Employee/Driver", readonly=True, store=False, comodel_name="hr.employee", related="equipment_id.employee_id")
    name = fields.Char(string="Name", readonly=True, store=False, translate=True, related="equipment_id.name")
    product_id = fields.Many2one(string="Equipment", readonly=True, store=False, comodel_name="product.product", related="equipment_id.product_id")
    product_qty = fields.Float(string="Quantity", readonly=True, store=False, related="equipment_id.product_qty")
    serial_number = fields.Char(string="Serial Number", readonly=True, store=False, related="equipment_id.serial_number")
    vehicle_id = fields.Many2one(string="Asset", readonly=True, store=False, comodel_name="fleet.vehicle", related="equipment_id.vehicle_id")

class UfsBaseEquipmentLog(models.Model):
    _name = "ufs.base.equipment.log"
    _description = "Equipment Log"
    _order = "date_start desc, id desc"
    can_not_edit_start_date = fields.Boolean(string="Can Not Edit Start Date", readonly=True, store=False)
    date_end = fields.Datetime(string="Date End", readonly=True)
    date_start = fields.Datetime(string="Date Start", readonly=True)
    employee_id = fields.Many2one(string="Employee/Driver", comodel_name="hr.employee")
    equipment_id = fields.Many2one(string="Equipment", comodel_name="ufs.base.equipment")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    name = fields.Char(string="Name", readonly=True, store=False, translate=True, related="equipment_id.name")
    product_qty = fields.Float(string="Quantity", readonly=True, store=False, related="equipment_id.product_qty")
