from odoo import _, api, fields, models


class UfsAiLogistWizard(models.TransientModel):
    _name = "ufs.ai.logist.wizard"
    _description = "AI Logist Wizard"

    forwarder_order_id = fields.Many2one(
        string="Экспедиционный заказ",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("default_forwarder_order_id") or self.env.context.get("active_id"),
        comodel_name="ufs.forwarder.order",
    )
    overall_state = fields.Selection(
        string="Итог",
        readonly=True,
        compute="_compute_ai_summary",
        selection=[
            ("no_checks", "Нет проверок"),
            ("completed", "Всё в порядке"),
            ("attention", "Требует внимания"),
            ("blocked", "Закрытие заблокировано"),
        ],
    )
    headline = fields.Char(string="Итог AI Logist", readonly=True, compute="_compute_ai_summary")
    summary = fields.Text(string="Заключение", readonly=True, compute="_compute_ai_summary")
    recommendation = fields.Text(string="Рекомендуемое действие", readonly=True, compute="_compute_ai_summary")
    checks_count = fields.Integer(string="Всего проверок", readonly=True, compute="_compute_ai_summary")
    completed_count = fields.Integer(string="Без замечаний", readonly=True, compute="_compute_ai_summary")
    attention_count = fields.Integer(string="Требуют внимания", readonly=True, compute="_compute_ai_summary")
    blocked_count = fields.Integer(string="Критичные ошибки", readonly=True, compute="_compute_ai_summary")
    check_ids = fields.Many2many(string="Проверки документов", readonly=True, compute="_compute_ai_summary", comodel_name="ufs.ai.document.check")

    @api.depends("forwarder_order_id")
    def _compute_ai_summary(self):
        check_model = self.env["ufs.ai.document.check"]
        for wizard in self:
            checks = check_model.search([("forwarder_order_id", "=", wizard.forwarder_order_id.id)]) if wizard.forwarder_order_id else check_model.browse()
            wizard.check_ids = checks
            wizard.checks_count = len(checks)
            wizard.completed_count = len(checks.filtered(lambda check: check.state == "completed"))
            wizard.attention_count = len(checks.filtered(lambda check: check.state in ("attention", "failed", "processing", "queued")))
            blocked_checks = checks.filtered(lambda check: check.state == "blocked" and not check.closure_override)
            wizard.blocked_count = len(blocked_checks)
            if blocked_checks:
                wizard.overall_state = "blocked"
                wizard.headline = _("Найден критический риск")
                wizard.summary = "\n".join(filter(None, blocked_checks.mapped("summary")))
                wizard.recommendation = _("Проверьте CMR, запросите подписанный документ у перевозчика и устраните расхождения перед закрытием заказа.")
            elif wizard.attention_count:
                wizard.overall_state = "attention"
                wizard.headline = _("Нужна проверка логиста")
                wizard.summary = _("AI нашёл документы с замечаниями, низкой уверенностью или незавершённой обработкой.")
                wizard.recommendation = _("Откройте проверки ниже, подтвердите черновики и повторите проверку документов с ошибками.")
            elif checks:
                wizard.overall_state = "completed"
                wizard.headline = _("Документы проверены")
                wizard.summary = _("Критичных замечаний по проверенным документам не найдено.")
                wizard.recommendation = _("Можно продолжить работу с заказом. Перед закрытием убедитесь, что загружены все обязательные документы.")
            else:
                wizard.overall_state = "no_checks"
                wizard.headline = _("Проверок пока нет")
                wizard.summary = _("Загрузите транспортный документ, чтобы AI Logist подготовил результат проверки.")
                wizard.recommendation = _("Добавьте CMR, заявку, счёт или акт в документы заказа.")

    def action_open_checks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("AI-проверки документов"),
            "res_model": "ufs.ai.document.check",
            "view_mode": "list,form",
            "domain": [("forwarder_order_id", "=", self.forwarder_order_id.id)],
        }
