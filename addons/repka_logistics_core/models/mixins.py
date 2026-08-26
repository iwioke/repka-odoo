from odoo import fields, models

class ModelUtils(models.AbstractModel):
    _name = "model.utils"
    _description = "Model Utilities"
    # No ufs_base-owned fields captured for this extension

class UfsAiohelper(models.AbstractModel):
    _name = "ufs.aiohelper"
    _description = "Async IO Helper"
    # No fields captured

class UfsBaseTrace(models.AbstractModel):
    _name = "ufs.base.trace"
    _description = "Base Trace"
    coords = fields.Char(string="Coordinates")
    coords_verbose = fields.Char(string="Coordinates Verbose")
    name = fields.Char(string="Name", required=True)
    trace_type = fields.Selection(string="Type", selection=[("placeholder", "Placeholder")])

class UfsMixinCargo(models.AbstractModel):
    _name = "ufs.mixin.cargo"
    _description = "Cargo Mixin"
    cargo_line_ids = fields.Many2many(string="Cargo", comodel_name="ufs.cargo_line")
    cargo_volume = fields.Float(string="Cargo Volume", readonly=True, store=False)
    cargo_weight = fields.Float(string="Cargo Weight", readonly=True, store=False)
    cargo_weight_uom_id = fields.Many2one(string="Weight UOM", comodel_name="uom.uom")
    is_adr = fields.Boolean(string="ADR", readonly=True, store=False)
    loading_units_count = fields.Integer(string="Loading Units", readonly=True, store=False)
    units_count = fields.Float(string="Cargo Count", readonly=True, store=False, help="No Recalc! Simply Sum.")
    verbose_cargoes = fields.Char(string="Cargoes", readonly=True, store=False)
    verbose_cargoes_no_weight = fields.Char(string="Cargo(es)", readonly=True, store=False)

class UfsMixinGuid(models.AbstractModel):
    _name = "ufs.mixin.guid"
    _description = "GUID Mixin"
    u_guid = fields.Char(string="GUID")

class UfsMixinState(models.AbstractModel):
    _name = "ufs.mixin.state"
    _description = "State Check Mixin"
    # No fields captured

class UfsMixinsRouteLine(models.AbstractModel):
    _name = "ufs.mixins.route_line"
    _description = "Route Line Mixin"
    _order = "datetime, id"
    _inherit = ['mail.thread']
    address_auto = fields.Char(string="Address", readonly=True)
    datetime = fields.Datetime(string="Date and Time")
    fact_arrival_dttm = fields.Datetime(string="Fact Arrival")
    fact_leave_dttm = fields.Datetime(string="Fact Leave")
    free_time = fields.Float(string="Free Time")
    has_message = fields.Boolean(string="Has Message", readonly=True, store=False)
    is_first = fields.Boolean(string="Is First", readonly=True, store=False)
    is_last = fields.Boolean(string="Is Last", readonly=True, store=False)
    line_type = fields.Selection(string="Type", selection=[("placeholder", "Placeholder")])
    location_id = fields.Many2one(string="Location", comodel_name="ufs.location")
    name = fields.Char(string="Name", readonly=True, store=False)
    notes = fields.Text(string="Notes")
    owner_partner_id = fields.Many2one(string="Owner Partner", comodel_name="res.partner")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    location_postcode = fields.Char(string="Postcode", readonly=True, store=False, related="location_id.postcode")

class UfsMixinsServices(models.AbstractModel):
    _name = "ufs.mixins.services"
    _description = "Service Name Mixin"
    # No fields captured

class UfsOrderMixin(models.AbstractModel):
    _name = "ufs.order.mixin"
    _description = "ufs.order.mixin"
    show_fact_arrival = fields.Boolean(string="Show Fact Arrival", readonly=True, store=False)

class UfsPaymentTermMixin(models.AbstractModel):
    _name = "ufs.payment.term.mixin"
    _description = "Payment Term Mixin"
    is_cash_expected = fields.Boolean(string="Cash Expected", help="If you expect Cash for order Payment, mark order as Cash, so we will create Invoices with Cash attributes")
    n_days_count = fields.Integer(string="N")
    payment_term_id = fields.Many2one(string="Payment Terms", comodel_name="account.payment.term")
    payment_term_verbose = fields.Char(string="Verbose Term", readonly=True, store=False)
    ufs_payment_term_id = fields.Many2one(string="Payment Terms", comodel_name="ufs.payment.term")
    is_business_day_term = fields.Boolean(string="Is Business Day Term", readonly=True, store=False, related="ufs_payment_term_id.is_business_day_term")
    is_n_term = fields.Boolean(string="Is N term", readonly=True, store=False, related="ufs_payment_term_id.is_n_term")
