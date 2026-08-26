from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    wallet_advance_deduction_defaults = fields.Char(string="Advance Deduction Defaults", help="Default deduction tiers for new advance entries. Format: [(min_debt, percentage), ...]. Example: [(0,10),(1000,15),(2000,20)]")
    wallet_collapse_trip_costs = fields.Boolean(string="Collapse Trip Costs to Single Wallet Entry", help="When enabled, all trip costs are merged into one wallet entry per driver instead of separate lines.")
    wallet_show_vault_field = fields.Boolean(string="Show Vault/Cash Register Field", help="Display the vault/cash register field in advances. When enabled, you can manage different cash registers and track their balances.")
