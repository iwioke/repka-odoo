from odoo import fields, models

class UfsLoadingType(models.Model):
    _name = "ufs.loading_type"
    _description = "Loading Type"
    active = fields.Boolean(string="Active")
    name = fields.Char(string="Name")

class UfsLocation(models.Model):
    _name = "ufs.location"
    _description = "Base Location Model"
    active = fields.Boolean(string="Active")
    address = fields.Char(string="Address")
    address_found = fields.Text(string="We found such an address", readonly=True)
    city = fields.Char(string="City", required=True)
    complete_name = fields.Char(string="Complete Name", readonly=True, store=False)
    contact_person = fields.Char(string="Contact Person")
    country_id = fields.Many2one(string="Country", required=True, comodel_name="res.country")
    latitude = fields.Float(string="Latitude", help="GPS Latitude")
    longitude = fields.Float(string="Longitude", help="GPS Longitude")
    name = fields.Char(string="Location Name", required=True)
    owner_partner_id = fields.Many2one(string="Owner of the Location", comodel_name="res.partner")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    postcode = fields.Char(string="Postcode")
    state = fields.Selection(string="Writable state", selection=[("placeholder", "Placeholder")])
    state_id = fields.Many2one(string="State", comodel_name="res.country.state")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    text_address = fields.Text(string="Text Address", readonly=True, store=False)
