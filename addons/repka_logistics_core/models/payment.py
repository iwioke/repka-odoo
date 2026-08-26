from odoo import fields, models

class UfsPaymentTerm(models.Model):
    _name = "ufs.payment.term"
    _description = "Payment Term"
    is_business_day_term = fields.Boolean(string="Is Business Day Term")
    is_n_term = fields.Boolean(string="Is N term")
    name = fields.Char(string="Name", translate=True)

class UfsUGuid(models.Model):
    _name = "ufs.u_guid"
    _description = "GUID Entry"
    model_name = fields.Char(string="Model Name", required=True)
    name = fields.Char(string="GUID", required=True)
    res_id = fields.Integer(string="Res", required=True)
