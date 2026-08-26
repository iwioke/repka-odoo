from odoo import fields, models

class UfsDriver(models.Model):
    _name = "ufs.driver"
    _description = "Base Simple Driver"
    _inherit = ['mail.thread']
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    name = fields.Char(string="Name")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    short_name = fields.Char(string="Name", readonly=True)
    ufs_object_id = fields.Reference(string="Object", readonly=True, selection=[("ufs.base.order", "Order")])

class UfsVehicle(models.Model):
    _name = "ufs.vehicle"
    _description = "Base Simple Vehicle"
    _order = "internal_name asc, name asc"
    _inherit = ['mail.thread']
    active = fields.Boolean(string="Active")
    fleet_type = fields.Selection(string="Asset Type", selection=[("placeholder", "Placeholder")])
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    internal_name = fields.Char(string="Internal Name", readonly=True)
    name = fields.Char(string="License Plate")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    power_type = fields.Many2one(string="Power Unit Type", comodel_name="fleet.vehicle.power_type")
    trailer_type = fields.Many2one(string="Trailer Type", comodel_name="fleet.vehicle.trailer_type")
    u_guid = fields.Char(string="GUID")
    ufs_object_id = fields.Reference(string="Object", readonly=True, selection=[("ufs.base.order", "Order")])
    ufs_object_res_id = fields.Integer(string="Object ID", readonly=True)
