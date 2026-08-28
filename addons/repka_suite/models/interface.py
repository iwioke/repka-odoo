from odoo import api, fields, models


ORDER_TYPES = [
    ("customer", "Для клиента"),
    ("internal", "Внутренний заказ"),
    ("export", "Экспорт"),
    ("import", "Импорт"),
]


class UfsBaseOrder(models.Model):
    _inherit = "ufs.base.order"

    order_type = fields.Selection(selection=ORDER_TYPES, string="Тип заказа")


class UfsFleetOrder(models.Model):
    _inherit = "ufs.fleet.order"

    services_included_line_ids = fields.One2many(
        related="base_order_id.services_included_line_ids",
        readonly=False,
        string="Включённые услуги",
    )

    @api.model
    def _repka_default_state(self):
        return self.env["ufs.order.state"].search([("code", "=", "new")], limit=1)

    state_id = fields.Many2one(default=_repka_default_state)

    @api.model_create_multi
    def create(self, vals_list):
        base_fields = self.env["ufs.base.order"]._fields
        for vals in vals_list:
            if vals.get("base_order_id"):
                continue
            base_vals = {}
            if vals.get("name"):
                base_vals["name"] = vals.pop("name")
            for name in list(vals):
                field = self._fields.get(name)
                if field and field.related and field.related[0] == "base_order_id":
                    target = field.related[-1]
                    if target in base_fields:
                        base_vals[target] = vals.pop(name)
            base_vals.setdefault("company_id", self.env.company.id)
            base_vals.setdefault("responsible_user_id", self.env.user.id)
            base_vals.setdefault("order_date", fields.Date.context_today(self))
            base_vals.setdefault("name", "Новый")
            vals["base_order_id"] = self.env["ufs.base.order"].create(base_vals).id
            vals.setdefault("state_id", self._repka_default_state().id)
        return super().create(vals_list)

    def action_set_customer_order(self):
        self.mapped("base_order_id").write({"order_type": "customer"})
        return True

    def action_set_internal_order(self):
        self.mapped("base_order_id").write({"order_type": "internal"})
        return True

    def action_request_advance_invoice(self):
        self.mapped("base_order_id").write({"advance_invoice_requested": True})
        return True


class UfsForwarderOrder(models.Model):
    _inherit = "ufs.forwarder.order"

    services_included_line_ids = fields.One2many(
        related="base_order_id.services_included_line_ids",
        readonly=False,
        string="Включённые услуги",
    )

    @api.model
    def _repka_default_state(self):
        return self.env["ufs.order.state"].search([("code", "=", "new")], limit=1)

    state_id = fields.Many2one(default=_repka_default_state)

    @api.model_create_multi
    def create(self, vals_list):
        base_fields = self.env["ufs.base.order"]._fields
        for vals in vals_list:
            if vals.get("base_order_id"):
                continue
            base_vals = {}
            if vals.get("name"):
                base_vals["name"] = vals.pop("name")
            for name in list(vals):
                field = self._fields.get(name)
                if field and field.related and field.related[0] == "base_order_id":
                    target = field.related[-1]
                    if target in base_fields:
                        base_vals[target] = vals.pop(name)
            base_vals.setdefault("company_id", self.env.company.id)
            base_vals.setdefault("responsible_user_id", self.env.user.id)
            base_vals.setdefault("order_date", fields.Date.context_today(self))
            base_vals.setdefault("name", "Новый")
            vals["base_order_id"] = self.env["ufs.base.order"].create(base_vals).id
            vals.setdefault("state_id", self._repka_default_state().id)
        return super().create(vals_list)

    def action_request_advance_invoice(self):
        self.mapped("base_order_id").write({"advance_invoice_requested": True})
        return True


class UfsWaybill(models.Model):
    _inherit = "ufs.waybill"

    state = fields.Selection(
        selection=[
            ("new", "Новый"),
            ("issued", "Выдан"),
            ("returned", "Сдан"),
            ("closed", "Закрыт"),
        ],
        default="new",
        required=True,
        string="Статус",
    )

    def action_mark_returned(self):
        self.write({"state": "returned", "return_dttm": fields.Datetime.now()})
        return True

    def action_duplicate_without_number(self):
        self.ensure_one()
        duplicate = self.copy({"name": False, "state": "new"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "ufs.waybill",
            "res_id": duplicate.id,
            "view_mode": "form",
            "target": "current",
        }


class ResUsers(models.Model):
    _inherit = "res.users"

    is_redirect_home = fields.Boolean(default=True)


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    repka_operational_state = fields.Selection(
        selection=[("ready", "В порядке"), ("repair", "Ремонт")],
        default="ready",
        required=True,
        string="Статус ТС",
        tracking=True,
    )
