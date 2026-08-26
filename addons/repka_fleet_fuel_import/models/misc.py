from odoo import fields, models

class UfsFleetRefuel(models.Model):
    _name = "ufs.fleet.refuel"
    _description = "Fleet Refuel"
    _order = "operation_dttm desc"
    additional_data = fields.Char(string="Additional Data")
    api_brand = fields.Char(string="Brand")
    api_country = fields.Char(string="Country Code")
    api_site_id = fields.Char(string="Station ID", help="Provider station/site identifier")
    api_station_name = fields.Char(string="Station Name")
    bokeh_chart = fields.Text(string="Bokeh Chart")
    card_id = fields.Many2one(string="Fuel Card", comodel_name="ufs.fuel.card")
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    discount = fields.Monetary(string="Discount", currency_field="currency_id")
    dut_qty = fields.Float(string="DUT Quantity", help="If you enter quantuty here, it will be used in comparisons")
    external_uid = fields.Char(string="External Uid")
    external_uri = fields.Char(string="External Uri")
    location_data = fields.Char(string="Location Data")
    location_id = fields.Many2one(string="Location", comodel_name="ufs.location")
    name = fields.Char(string="Name", readonly=True, store=False)
    operation_dttm = fields.Datetime(string="Operation DTTM")
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    qty = fields.Float(string="Quantity")
    qty_by_stats = fields.Float(string="Quantity by Stats")
    record_hash = fields.Char(string="Record Hash")
    refill_diff = fields.Float(string="Refill Diff")
    refill_ratio = fields.Float(string="Refill Ratio")
    tax_ids = fields.Many2many(string="Taxes", comodel_name="account.tax")
    tax_value = fields.Float(string="Tax Value")
    total_amount = fields.Monetary(string="Total Amount", readonly=True, currency_field="currency_id")
    trip_cost_ids = fields.One2many(string="Attached to Trip Cost", comodel_name="ufs.trip.cost", inverse_name="refuel_id")
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    api_provider_id = fields.Many2one(string="API Provider", readonly=True, comodel_name="ufs.fuel.api.provider", related="card_id.api_provider_id")
    product_categ_id = fields.Many2one(string="Product Category", readonly=True, store=False, comodel_name="product.category", related="product_id.categ_id")
    product_uom_id = fields.Many2one(string="Unit of Measure", readonly=True, store=False, help="Default unit of measure used for all stock operations.", comodel_name="uom.uom", related="product_id.uom_id")
    vendor_id = fields.Many2one(string="Vendor ID", readonly=True, comodel_name="res.partner", related="card_id.vendor_id")

class UfsFleetTrip(models.Model):
    _inherit = "ufs.fleet.trip"
    _order = "start_datetime"
    # No fields captured

class UfsFuelApiInterface(models.Model):
    _name = "ufs.fuel.api.interface"
    _description = "Fuel API Interface"
    # No fields captured

class UfsFuelApiParser(models.Model):
    _name = "ufs.fuel.api.parser"
    _description = "ufs.fuel.api.parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserBl(models.Model):
    _name = "ufs.fuel.api.parser.bl"
    _description = "Berlio Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserBn(models.Model):
    _name = "ufs.fuel.api.parser.bn"
    _description = "Belorusneft Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserBpPl(models.Model):
    _name = "ufs.fuel.api.parser.bp_pl"
    _description = "ufs.fuel.api.parser.bp_pl"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserDiesel24(models.Model):
    _name = "ufs.fuel.api.parser.diesel24"
    _description = "Diesel24 Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserDkv(models.Model):
    _name = "ufs.fuel.api.parser.dkv"
    _description = "DKV Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    customerID = fields.Char(string="Customerid")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserDornet(models.Model):
    _name = "ufs.fuel.api.parser.dornet"
    _description = "ufs.fuel.api.parser.dornet"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserE100(models.Model):
    _name = "ufs.fuel.api.parser.e100"
    _description = "E100 Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserE100pro(models.Model):
    _name = "ufs.fuel.api.parser.e100pro"
    _description = "E100 Pro Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserGp(models.Model):
    _name = "ufs.fuel.api.parser.gp"
    _description = "Gazprom Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserGpncard(models.Model):
    _name = "ufs.fuel.api.parser.gpncard"
    _description = "GPN Card Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Datetime(string="From", required=True)
    date_to = fields.Datetime(string="To", required=True)
    endpoint = fields.Char(string="Endpoint")
    file_import_format = fields.Selection(string="File Import Format", selection=[("placeholder", "Placeholder")])
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserOkko(models.Model):
    _name = "ufs.fuel.api.parser.okko"
    _description = "ufs.fuel.api.parser.okko"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserRosneft(models.Model):
    _name = "ufs.fuel.api.parser.rosneft"
    _description = "Rosneft Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserShell(models.Model):
    _name = "ufs.fuel.api.parser.shell"
    _description = "Shell Fuel Parser"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserUkrnafta(models.Model):
    _name = "ufs.fuel.api.parser.ukrnafta"
    _description = "ufs.fuel.api.parser.ukrnafta"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserWog(models.Model):
    _name = "ufs.fuel.api.parser.wog"
    _description = "ufs.fuel.api.parser.wog"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiParserZapOnline(models.Model):
    _name = "ufs.fuel.api.parser.zap_online"
    _description = "ufs.fuel.api.parser.zap_online"
    _auth = fields.Char(string=" Auth")
    _card_mapping = fields.Char(string=" Card Mapping")
    _currency_mapping = fields.Char(string=" Currency Mapping")
    _json_response = fields.Char(string=" Json Response")
    _result_vals = fields.Binary(string=" Result Vals")
    access_token = fields.Char(string="Access Token")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    endpoint = fields.Char(string="Endpoint")
    newest_only = fields.Boolean(string="Newest Only")
    provider_id = fields.Many2one(string="Provider", comodel_name="ufs.fuel.api.provider")
    token_type = fields.Char(string="Token Type")

class UfsFuelApiProvider(models.Model):
    _name = "ufs.fuel.api.provider"
    _description = "Fuel API Provider"
    active = fields.Boolean(string="Active")
    additional_data = fields.Char(string="Additional Data", help="Additional data for API. JSON format")
    company_id = fields.Many2one(string="Company", required=True, comodel_name="res.company")
    endpoint = fields.Char(string="Endpoint")
    name = fields.Char(string="Name", readonly=True, store=False)
    parser_type = fields.Selection(string="Parser Type", selection=[("placeholder", "Placeholder")])
    parser_type_comments = fields.Text(string="Parser Type Comments")
    partner_id = fields.Many2one(string="Partner", required=True, comodel_name="res.partner")
    secret = fields.Char(string="Password or Secret(will not be hashed!!!!")
    username = fields.Char(string="Username")

class UfsFuelCard(models.Model):
    _inherit = "ufs.fuel.card"
    api_provider_id = fields.Many2one(string="API Provider", comodel_name="ufs.fuel.api.provider")
    refuels_count = fields.Integer(string="Refuels Count", readonly=True, store=False)
    vendor_id = fields.Many2one(string="Vendor ID", readonly=True, comodel_name="res.partner")

class UfsTripCost(models.Model):
    _inherit = "ufs.trip.cost"
    control_qty = fields.Float(string="Control Qty", help="External Control Value, DUT data in example")
    refuel_id = fields.Many2one(string="Refuel", comodel_name="ufs.fleet.refuel")
