from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    create_trip_after_order = fields.Boolean(string="Create Trip After Fleet Order")
    enable_chain_actions = fields.Boolean(string="Enable Chain Actions in Forwarding")
    f_service_name_contract = fields.Boolean(string="Contract(s)")
    f_service_name_documents = fields.Boolean(string="Document(s)")
    f_service_name_driver = fields.Boolean(string="Driver(s)")
    f_service_name_incoming_ref = fields.Boolean(string="Incoming Ref.")
    f_service_name_loading_date = fields.Boolean(string="Load Date(s)")
    f_service_name_unloading_date = fields.Boolean(string="Unload Date(s)")
    f_service_name_vehicle = fields.Boolean(string="Vehicle(s)")
    forwarding_invoicing_rule = fields.Selection(string="How we create Forwarding Invoice", selection=[("placeholder", "Placeholder")])
    log_transport_documents = fields.Boolean(string="Log Transport Documents in Chatter")
    pass_data_to_fleet_order = fields.Boolean(string="Pass Data Changes to Fleet Order")
    pass_data_to_forwarder_order = fields.Boolean(string="Pass Data Changes to Forwarder Order")

class UfsForwarderChainCreateWizard(models.TransientModel):
    _name = "ufs.forwarder.chain_create.wizard"
    _description = "Create Chain Order Wizard"
    company_ufs_contract_id = fields.Many2one(string="Internal Contract", required=True, help="Contract between the current contractor and selected internal company", comodel_name="ufs.contract")
    freight_amount = fields.Monetary(string="Freight Amount", required=True, help="Freight amount we should paid Contractor", currency_field="currency_id")
    internal_company_id = fields.Many2one(string="Internal Company", required=True, help="Select the internal company to act as intermediate contractor", comodel_name="res.company")
    internal_freight_amount = fields.Monetary(string="Internal Freight Amount", help="Freight amount for the internal order (between our companies). If not set, will use the same as freight_amount", currency_field="currency_id")
    internal_freight_currency_id = fields.Many2one(string="Internal Freight Currency", comodel_name="res.currency")
    s_order_id = fields.Many2one(string="Source Sub Order", required=True, comodel_name="ufs.forwarder.suborder")
    ufs_contract_id = fields.Many2one(string="Contract", required=True, help="Contract between the current contractor and selected internal company", comodel_name="ufs.contract")
    currency_id = fields.Many2one(string="Currency", readonly=True, store=False, comodel_name="res.currency", related="freight_currency_id")
    freight_currency_id = fields.Many2one(string="Currency", readonly=True, store=False, comodel_name="res.currency", related="s_order_id.freight_currency_id")
    internal_company_partner_id = fields.Many2one(string="Internal Company Partner", readonly=True, store=False, comodel_name="res.partner", related="internal_company_id.partner_id")
    source_company_id = fields.Many2one(string="Source Company", readonly=True, store=False, comodel_name="res.company", related="s_order_id.company_id")
    source_company_partner_id = fields.Many2one(string="Source Company Partner", readonly=True, store=False, comodel_name="res.partner", related="s_order_id.company_id.partner_id")
    source_partner_id = fields.Many2one(string="Current Contractor", readonly=True, store=False, comodel_name="res.partner", related="s_order_id.partner_id")

class UfsForwarderCreateParentWizard(models.TransientModel):
    _name = "ufs.forwarder.create_parent.wizard"
    _description = "Create Parent Order Wizard"
    forwarder_order_id = fields.Many2one(string="Source Oder", comodel_name="ufs.forwarder.order")
    freight_amount = fields.Monetary(string="Freight Amount", currency_field="currency_id")
    new_company_id = fields.Many2one(string="New Company", comodel_name="res.company")
    currency_id = fields.Many2one(string="Currency", readonly=True, store=False, comodel_name="res.currency", related="forwarder_order_id.freight_currency_id")
    forwarder_company_id = fields.Many2one(string="Company", readonly=True, store=False, comodel_name="res.company", related="forwarder_order_id.company_id")

class UfsForwarderSubSwitchWizard(models.TransientModel):
    _name = "ufs.forwarder.sub.switch_wizard"
    _description = "ufs.forwarder.sub.switch_wizard"
    partner_id = fields.Many2one(string="Subcontractor", comodel_name="res.partner")
    s_order_id = fields.Many2one(string="Source Sub Order", comodel_name="ufs.forwarder.suborder")
    switch_datetime = fields.Datetime(string="Date and Time", required=True)
    switch_location_id = fields.Many2one(string="Switch Place", required=True, comodel_name="ufs.location")
    switch_type = fields.Selection(string="Switch Type", required=True, selection=[("placeholder", "Placeholder")])
    ufs_driver2_id = fields.Many2one(string="Driver 2", comodel_name="ufs.driver")
    ufs_driver_id = fields.Many2one(string="Driver", comodel_name="ufs.driver")
    ufs_trailer_id = fields.Many2one(string="Trailer", comodel_name="ufs.vehicle")
    ufs_truck_id = fields.Many2one(string="Truck", comodel_name="ufs.vehicle")
