from odoo import fields, models

class UfsTrackingSystem(models.Model):
    _name = "ufs.tracking.system"
    _description = "Tracking Provider"
    active = fields.Boolean(string="Active")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    credentials = fields.Text(string="Credentials in JSON")
    endpoint_uri = fields.Char(string="Endpoint URI")
    force_verify_false = fields.Boolean(string="Force Verify False")
    func_name = fields.Char(string="Function name for coords fetch")
    name = fields.Char(string="Name", required=True)
    parse_schema = fields.Selection(string="Parse Schema", selection=[("placeholder", "Placeholder")])
    parse_schema_comment = fields.Text(string="Parse Schema Comment", readonly=True)
    session = fields.Binary(string="Session", store=False)
    token = fields.Char(string="Token", store=False)

class UfsTrackingSystemRefill(models.Model):
    _name = "ufs.tracking.system.refill"
    _description = "Refuel Event From Tracking System"
    address = fields.Char(string="Address")
    amount = fields.Float(string="Amount")
    driver_id = fields.Many2one(string="Driver", comodel_name="hr.employee")
    event_type = fields.Selection(string="Event Type", selection=[("placeholder", "Placeholder")])
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    name = fields.Char(string="Name", required=True)
    operation_dttm = fields.Datetime(string="Operation Datetime", required=True)
    raw_data = fields.Text(string="Raw Data")
    tracking_system_id = fields.Many2one(string="Tracking System", comodel_name="ufs.tracking.system")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")

class UfsTransportDocument(models.Model):
    _name = "ufs.transport.document"
    _description = "Transport Document"
    attached_scan = fields.Binary(string="Attached Scan")
    attached_scan_fname = fields.Char(string="FName")
    date = fields.Date(string="Date")
    move_ids = fields.Many2many(string="Account Moves", comodel_name="account.move")
    move_line_ids = fields.Many2many(string="Move Lines", comodel_name="account.move.line")
    name = fields.Char(string="Number", required=True)
    original_receive_date = fields.Date(string="Original Receive Date")
    receive_date = fields.Date(string="Receive Date")
    type_id = fields.Many2one(string="Type", comodel_name="ufs.transport.document.type")
