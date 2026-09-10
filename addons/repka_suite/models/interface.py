from odoo import api, fields, models


ORDER_TYPES = [
    ("customer", "Для клиента"),
    ("internal", "Внутренний заказ"),
    ("export", "Экспорт"),
    ("import", "Импорт"),
]

BASE_ORDER_VALUE_FIELDS = {
    "company_id",
    "responsible_user_id",
    "order_date",
    "partner_id",
    "contact_person_id",
    "incoming_ref",
    "external_nr",
    "ufs_contract_id",
    "ufs_payment_term_id",
    "n_days_count",
    "print_stamp",
    "freight_amount",
    "freight_currency_id",
    "invoice_notes",
    "order_type",
    "origin_id",
    "origin_city",
    "destination_id",
    "destination_city",
    "start_datetime",
    "stop_datetime",
    "planned_loading_date",
    "actual_loading_date",
    "planned_unloading_date",
    "actual_unloading_date",
    "carrier_id",
    "carrier_rate",
    "cargo_type",
    "pallets",
    "order_memo",
}


class UfsBaseOrder(models.Model):
    _inherit = "ufs.base.order"

    order_type = fields.Selection(selection=ORDER_TYPES, string="Тип заказа")
    planned_loading_date = fields.Datetime(string="Плановая погрузка")
    actual_loading_date = fields.Datetime(string="Фактическая погрузка")
    planned_unloading_date = fields.Datetime(string="Плановая выгрузка")
    actual_unloading_date = fields.Datetime(string="Фактическая выгрузка")
    carrier_id = fields.Many2one("res.partner", string="Перевозчик")
    carrier_rate = fields.Monetary(string="Ставка перевозчика", currency_field="company_currency_id")
    margin = fields.Monetary(
        string="Маржа",
        currency_field="company_currency_id",
        compute="_compute_repka_margin",
        store=True,
    )
    cargo_type = fields.Char(string="Вид груза")
    pallets = fields.Float(string="Паллеты")

    @api.depends("freight_amount", "carrier_rate")
    def _compute_repka_margin(self):
        for order in self:
            order.margin = order.freight_amount - order.carrier_rate


class UfsFleetOrder(models.Model):
    _inherit = "ufs.fleet.order"

    services_included_line_ids = fields.One2many(
        related="base_order_id.services_included_line_ids",
        readonly=False,
        string="Включённые услуги",
    )
    planned_loading_date = fields.Datetime(related="base_order_id.planned_loading_date", readonly=False)
    actual_loading_date = fields.Datetime(related="base_order_id.actual_loading_date", readonly=False)
    planned_unloading_date = fields.Datetime(related="base_order_id.planned_unloading_date", readonly=False)
    actual_unloading_date = fields.Datetime(related="base_order_id.actual_unloading_date", readonly=False)
    carrier_id = fields.Many2one(related="base_order_id.carrier_id", readonly=False)
    carrier_rate = fields.Monetary(
        related="base_order_id.carrier_rate",
        readonly=False,
        currency_field="company_currency_id",
    )
    margin = fields.Monetary(related="base_order_id.margin", currency_field="company_currency_id")
    cargo_type = fields.Char(related="base_order_id.cargo_type", readonly=False)
    pallets = fields.Float(related="base_order_id.pallets", readonly=False)
    invoice_status = fields.Selection(
        selection=[
            ("no_invoice", "Нет счёта"),
            ("draft", "Черновик"),
            ("invoiced", "Выставлен"),
            ("paid", "Оплачен"),
        ],
        default="no_invoice",
        string="Статус счёта",
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
                if name in BASE_ORDER_VALUE_FIELDS and name in base_fields:
                    base_vals[name] = vals.pop(name)
                    continue
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

    name = fields.Char(related="base_order_id.name", readonly=False)
    partner_id = fields.Many2one(related="base_order_id.partner_id", readonly=False)
    incoming_ref = fields.Char(related="base_order_id.incoming_ref", readonly=False)
    external_nr = fields.Char(related="base_order_id.external_nr", readonly=False)
    order_date = fields.Date(related="base_order_id.order_date", readonly=False)
    ufs_contract_id = fields.Many2one(related="base_order_id.ufs_contract_id", readonly=False)
    ufs_payment_term_id = fields.Many2one(
        related="base_order_id.ufs_payment_term_id",
        readonly=False,
    )
    n_days_count = fields.Integer(related="base_order_id.n_days_count", readonly=False)
    order_finish_date = fields.Date(related="base_order_id.order_finish_date", readonly=False)
    print_stamp = fields.Boolean(related="base_order_id.print_stamp", readonly=False)
    company_id = fields.Many2one(related="base_order_id.company_id", readonly=False)
    order_type = fields.Selection(related="base_order_id.order_type", readonly=False)
    responsible_user_id = fields.Many2one(
        related="base_order_id.responsible_user_id",
        readonly=False,
    )
    freight_amount = fields.Monetary(
        related="base_order_id.freight_amount",
        readonly=False,
        currency_field="company_currency_id",
    )
    freight_currency_id = fields.Many2one(
        related="base_order_id.freight_currency_id",
        readonly=False,
    )
    services_included_line_ids = fields.One2many(
        related="base_order_id.services_included_line_ids",
        readonly=False,
        string="Включённые услуги",
    )
    planned_loading_date = fields.Datetime(related="base_order_id.planned_loading_date", readonly=False)
    actual_loading_date = fields.Datetime(related="base_order_id.actual_loading_date", readonly=False)
    planned_unloading_date = fields.Datetime(related="base_order_id.planned_unloading_date", readonly=False)
    actual_unloading_date = fields.Datetime(related="base_order_id.actual_unloading_date", readonly=False)
    carrier_id = fields.Many2one(related="base_order_id.carrier_id", readonly=False)
    carrier_rate = fields.Monetary(
        related="base_order_id.carrier_rate",
        readonly=False,
        currency_field="company_currency_id",
    )
    margin = fields.Monetary(related="base_order_id.margin", currency_field="company_currency_id")
    cargo_type = fields.Char(related="base_order_id.cargo_type", readonly=False)

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
                if name in BASE_ORDER_VALUE_FIELDS and name in base_fields:
                    base_vals[name] = vals.pop(name)
                    continue
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

    def action_auto_suborder(self):
        self.ensure_one()
        suborder_type = self.env["ufs.forwarder.suborder.type"].search([], limit=1)
        if not suborder_type:
            suborder_type = self.env["ufs.forwarder.suborder.type"].create({
                "name": "Автоперевозка",
                "service_type": "placeholder",
                "active": True,
            })
        base_order = self.base_order_id.copy({"name": f"{self.name or 'Новый'}/1"})
        suborder = self.env["ufs.forwarder.suborder"].create({
            "forwarder_order_id": self.id,
            "base_order_id": base_order.id,
            "sub_order_type_id": suborder_type.id,
            "state_id": self.state_id.id,
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "ufs.forwarder.suborder",
            "res_id": suborder.id,
            "view_mode": "form",
            "target": "current",
        }


class UfsForwarderSuborder(models.Model):
    _inherit = "ufs.forwarder.suborder"

    services_included_line_ids = fields.One2many(
        related="base_order_id.services_included_line_ids",
        readonly=False,
        string="Услуги",
    )
    carrier_id = fields.Many2one(related="base_order_id.carrier_id", readonly=False)
    carrier_rate = fields.Monetary(
        related="base_order_id.carrier_rate",
        readonly=False,
        currency_field="company_currency_id",
    )
    margin = fields.Monetary(related="base_order_id.margin", currency_field="company_currency_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("base_order_id"):
                continue
            parent = self.env["ufs.forwarder.order"].browse(vals.get("forwarder_order_id")).exists()
            name = vals.pop("name", False)
            if parent:
                base_order = parent.base_order_id.copy({
                    "name": name or f"{parent.name or 'Новый'}/подзаказ",
                })
                vals.setdefault("state_id", parent.state_id.id)
            else:
                base_order = self.env["ufs.base.order"].create({
                    "name": name or "Новый подзаказ",
                    "company_id": self.env.company.id,
                    "responsible_user_id": self.env.user.id,
                    "order_date": fields.Date.context_today(self),
                })
            vals["base_order_id"] = base_order.id
        return super().create(vals_list)


class UfsWaybill(models.Model):
    _inherit = "ufs.waybill"

    state = fields.Selection(
        selection=[
            ("issued", "Выдан"),
            ("in_progress", "В пути"),
            ("returned", "Возвращён"),
            ("closed", "Закрыт"),
        ],
        default="issued",
        required=True,
        string="Статус",
    )
    fuel_issued = fields.Float(string="Выдано топлива, л")
    fuel_remaining = fields.Float(string="Остаток топлива, л")
    arrival_dttm = fields.Datetime(string="Дата и время прибытия")

    def action_mark_in_progress(self):
        self.write({"state": "in_progress"})
        return True

    def action_mark_returned(self):
        self.write({"state": "returned", "return_dttm": fields.Datetime.now()})
        return True

    def action_mark_closed(self):
        self.write({"state": "closed"})
        return True

    def action_duplicate_without_number(self):
        self.ensure_one()
        duplicate = self.copy({"name": False, "state": "issued"})
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
        selection=[
            ("ready", "В порядке"),
            ("repair", "В ремонте"),
            ("decommissioned", "Списан"),
        ],
        default="ready",
        required=True,
        string="Статус ТС",
        tracking=True,
    )
