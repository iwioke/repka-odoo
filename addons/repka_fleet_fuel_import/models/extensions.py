from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = "product.product"
    bn_code = fields.Char(string="BN Product Code", store=False, related="product_tmpl_id.bn_code")
    bp_polska_code = fields.Char(string="BP Polska Product Code", store=False, related="product_tmpl_id.bp_polska_code")
    e100_code = fields.Char(string="E100 Product Code", store=False, related="product_tmpl_id.e100_code")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    bn_code = fields.Char(string="BN Product Code")
    bp_polska_code = fields.Char(string="BP Polska Product Code")
    e100_code = fields.Char(string="E100 Product Code")
