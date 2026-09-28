import json
import subprocess
import sys
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


AUTOMATIONS = Path('/opt/repka/ai-automations')
SCENARIOS = {
    'customer_360': 'Профиль клиента',
    'margin_watch': 'Экономика перевозок',
    'document_readiness': 'Готовность документов',
    'executive_brief': 'Сводка руководителю',
}
DOCUMENT_TYPES = {'transport_request': 'заявка', 'cmr': 'CMR', 'invoice': 'счёт', 'act': 'акт'}


class DemoPartner(models.Model):
    _inherit = 'res.partner'

    demo_session_id = fields.Many2one('repka.ai.demo.session', string='Демо-показ', ondelete='restrict', index=True)


class DemoBaseOrder(models.Model):
    _inherit = 'ufs.base.order'

    demo_session_id = fields.Many2one('repka.ai.demo.session', string='Демо-показ', ondelete='restrict', index=True)
    demo_revenue = fields.Float(string='Демо: выручка')
    demo_direct_cost = fields.Float(string='Демо: прямые затраты')
    demo_currency_code = fields.Char(string='Демо: валюта')


class DemoForwarderOrder(models.Model):
    _inherit = 'ufs.forwarder.order'

    demo_session_id = fields.Many2one('repka.ai.demo.session', string='Демо-показ', ondelete='restrict', index=True)


class DemoTransportDocument(models.Model):
    _inherit = 'ufs.transport.document'

    demo_session_id = fields.Many2one('repka.ai.demo.session', string='Демо-показ', ondelete='restrict', index=True)


class DemoResult(models.Model):
    _name = 'repka.ai.demo.result'
    _description = 'Результат демонстрационного сценария'
    _order = 'create_date desc, id desc'

    session_id = fields.Many2one('repka.ai.demo.session', string='Показ', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Сценарий', required=True)
    scenario = fields.Selection([(slug, name) for slug, name in SCENARIOS.items()], string='Тип сценария', required=True)
    summary = fields.Char(string='Итог', required=True)
    details = fields.Text(string='Результат', required=True)
    output_json = fields.Text(string='Технический результат', required=True)


class DemoSession(models.Model):
    _name = 'repka.ai.demo.session'
    _description = 'Демонстрационный показ AI-сценариев'
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Название', required=True, default='Демонстрационный показ')
    user_id = fields.Many2one('res.users', string='Демонстратор', required=True, default=lambda self: self.env.user, readonly=True)
    state = fields.Selection([('draft', 'Подготовка'), ('active', 'Идёт показ')], string='Состояние', default='draft', required=True)
    partner_ids = fields.One2many('res.partner', 'demo_session_id', string='Синтетические клиенты', readonly=True)
    order_ids = fields.One2many('ufs.base.order', 'demo_session_id', string='Синтетические заказы', readonly=True)
    forwarder_order_ids = fields.One2many('ufs.forwarder.order', 'demo_session_id', string='Экспедиционные заказы', readonly=True)
    document_ids = fields.One2many('ufs.transport.document', 'demo_session_id', string='Документы', readonly=True)
    result_ids = fields.One2many('repka.ai.demo.result', 'session_id', string='Результаты сценариев', readonly=True)
    required_document_types = fields.Char(string='Обязательные типы документов', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        self._check_environment()
        return super().create([{**vals, 'user_id': self.env.uid, 'state': 'draft'} for vals in vals_list])

    def _check_environment(self):
        if self.env.cr.dbname != 'repka_test' or not self.env.user.has_group('base.group_system'):
            raise AccessError('Демонстрация доступна только администратору базы repka_test.')

    def _check_owner(self):
        self._check_environment()
        if any(session.user_id != self.env.user for session in self):
            raise AccessError('Можно управлять только собственным демонстрационным показом.')

    def _example(self, slug):
        path = AUTOMATIONS / 'scenarios' / slug / 'example_input.json'
        try:
            if path.stat().st_size > 1024 * 1024:
                raise ValueError()
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, UnicodeError) as exc:
            raise UserError('Пример сценария недоступен. Проверьте подключение ai_automations в dev-контейнере.') from exc

    def _customer_records(self, data, prefix):
        partners = {}
        for row in data['partners']:
            partner = self.env['res.partner'].sudo().create({
                'name': row['name'], 'demo_session_id': self.id,
            })
            partners[row['id']] = partner
        for row in data['orders']:
            self.env['ufs.base.order'].sudo().create({
                'name': f'{prefix}-{row["id"]}', 'demo_session_id': self.id,
                'company_id': self.env.company.id, 'partner_id': partners[row['partner_id']].id,
                'order_date': row['order_date'], 'is_paid': row['is_paid'],
            })

    def _margin_records(self, data, prefix):
        partner = self.env['res.partner'].sudo().create({
            'name': f'Синтетический клиент: {prefix}', 'demo_session_id': self.id,
        })
        for row in data['orders']:
            self.env['ufs.base.order'].sudo().create({
                'name': f'{prefix}-{row["id"]}', 'demo_session_id': self.id,
                'company_id': self.env.company.id, 'partner_id': partner.id,
                'demo_revenue': float(row['revenue']), 'demo_direct_cost': float(row['direct_cost']),
                'demo_currency_code': row['currency'],
            })

    def _document_records(self, data, prefix):
        partner = self.env['res.partner'].sudo().create({
            'name': f'Синтетический клиент: {prefix}', 'demo_session_id': self.id,
        })
        for row in data['orders']:
            order = self.env['ufs.base.order'].sudo().create({
                'name': f'{prefix}-{row["id"]}', 'demo_session_id': self.id,
                'company_id': self.env.company.id, 'partner_id': partner.id,
            })
            forwarding = self.env['ufs.forwarder.order'].sudo().create({
                'base_order_id': order.id, 'demo_session_id': self.id,
            })
            for check in row['checks']:
                document = self.env['ufs.transport.document'].sudo().with_context(skip_ai_document_check=True).create({
                    'name': f'{prefix}-{row["id"]}-{DOCUMENT_TYPES[check["document_type"]]}',
                    'demo_session_id': self.id, 'forwarder_order_ids': [(4, forwarding.id)],
                })
                self.env['ufs.ai.document.check'].sudo().create({
                    'name': document.name, 'source_document_id': document.id,
                    'forwarder_order_id': forwarding.id, 'base_order_id': order.id,
                    'document_type': check['document_type'], 'state': check['state'], 'is_demo': True,
                })

    def action_prepare(self):
        self.ensure_one()
        self._check_owner()
        if self.state != 'draft':
            raise UserError('Этот показ уже подготовлен.')
        if self.search_count([('state', '=', 'active')]):
            raise UserError('Сначала завершите текущий показ.')
        customer = self._example('customer_360')
        margin = self._example('margin_watch')
        documents = self._example('document_readiness')
        brief = self._example('executive_brief')
        self._customer_records(customer, 'ДЕМО-КЛИЕНТ')
        self._margin_records(margin, 'ДЕМО-МАРЖА')
        self._document_records(documents, 'ДЕМО-ДОКУМЕНТЫ')
        self._customer_records(brief['customer_data'], 'ДЕМО-СВОДКА-КЛИЕНТ')
        self._margin_records(brief['margin_data'], 'ДЕМО-СВОДКА-МАРЖА')
        self._document_records(brief['document_data'], 'ДЕМО-СВОДКА-ДОКУМЕНТЫ')
        self.write({
            'state': 'active',
            'required_document_types': ', '.join(DOCUMENT_TYPES[kind] for kind in documents['required_types']),
        })
        return self._open_self()

    def _run(self, slug):
        self.ensure_one()
        self._check_owner()
        if self.state != 'active' or slug not in SCENARIOS:
            raise UserError('Сценарий не зарегистрирован или показ не начат.')
        command = [sys.executable, str(AUTOMATIONS / 'scenarios' / slug / 'run.py'), '--mode', 'demo']
        try:
            completed = subprocess.run(command, capture_output=True, timeout=12, cwd=AUTOMATIONS)
            if completed.returncode or len(completed.stdout) > 1024 * 1024:
                raise ValueError()
            payload = json.loads(completed.stdout)
            if (not isinstance(payload, dict) or payload.get('scenario') != slug
                    or payload.get('mode') != 'DEMO' or payload.get('method') != 'deterministic_rules_not_llm'):
                raise ValueError()
            result = payload['result']
            lines = self._result_lines(slug, result)
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
            raise UserError('Не удалось выполнить сценарий. Проверьте синтетический пример и подключение каталога.') from exc
        record = self.env['repka.ai.demo.result'].create({
            'session_id': self.id, 'scenario': slug, 'name': SCENARIOS[slug],
            'summary': lines[0], 'details': '\n'.join(lines),
            'output_json': json.dumps(payload, ensure_ascii=False, indent=2),
        })
        return {'type': 'ir.actions.act_window', 'res_model': 'repka.ai.demo.result',
                'res_id': record.id, 'view_mode': 'form', 'target': 'current'}

    def _result_lines(self, slug, result):
        if slug == 'customer_360':
            return [f'Клиентов для проверки: {result["review_reactivation"]}'] + [
                f'{row["name"]}: заказов {row["orders"]}, неоплаченных {row["unpaid_orders"]}; {row["reason"]}'
                for row in result['customers']
            ]
        if slug == 'margin_watch':
            return [f'Заказов с замечаниями: {result["review_count"]}'] + [
                f'{row["name"]}: разница {row["result"]} {row["currency"]}; {row["reason"]}'
                for row in result['orders']
            ]
        if slug == 'document_readiness':
            return [f'Заказов для проверки: {result["review_count"]}'] + [
                f'Заказ {row["id"]}: отсутствуют {", ".join(DOCUMENT_TYPES[kind] for kind in row["missing"]) or "нет"}; '
                f'требуют внимания {", ".join(DOCUMENT_TYPES[kind] for kind in row["needs_review"]) or "нет"}; {row["reason"]}'
                for row in result['orders']
            ]
        return ['Сводка по трём отдельным синтетическим выборкам:'] + [
            f'{label}: {result["kpis"][key]}' for key, label in (
                ('customers_to_review', 'Клиентов для проверки'),
                ('orders_with_margin_alert', 'Финансовых замечаний'),
                ('orders_with_document_gaps', 'Пробелов в документах'),
            )
        ] + result['actions'] + [result['note']]

    def action_run_customer_360(self):
        return self._run('customer_360')

    def action_run_margin_watch(self):
        return self._run('margin_watch')

    def action_run_document_readiness(self):
        return self._run('document_readiness')

    def action_run_executive_brief(self):
        return self._run('executive_brief')

    def _open_self(self):
        return {'type': 'ir.actions.act_window', 'res_model': self._name,
                'res_id': self.id, 'view_mode': 'form', 'target': 'current'}

    def action_open_partners(self):
        self.ensure_one()
        self._check_owner()
        return {'type': 'ir.actions.act_window', 'name': 'Синтетические клиенты',
                'res_model': 'res.partner', 'view_mode': 'list,form',
                'domain': [('demo_session_id', '=', self.id)]}

    def action_open_orders(self):
        self.ensure_one()
        self._check_owner()
        return {'type': 'ir.actions.act_window', 'name': 'Синтетические заказы',
                'res_model': 'ufs.base.order', 'view_mode': 'list,form',
                'views': [(self.env.ref('repka_ai_demo_showcase.view_demo_order_list').id, 'list'),
                          (self.env.ref('repka_ai_demo_showcase.view_demo_order_form').id, 'form')],
                'domain': [('demo_session_id', '=', self.id)]}

    def action_open_documents(self):
        self.ensure_one()
        self._check_owner()
        return {'type': 'ir.actions.act_window', 'name': 'Синтетические документы',
                'res_model': 'ufs.transport.document', 'view_mode': 'list,form',
                'domain': [('demo_session_id', '=', self.id)]}

    def action_finish(self):
        self._check_owner()
        for session in self:
            if session.state == 'active':
                documents = self.env['ufs.transport.document'].sudo().search([('demo_session_id', '=', session.id)])
                checks = self.env['ufs.ai.document.check'].sudo().search([('source_document_id', 'in', documents.ids)])
                if any(not check.is_demo for check in checks):
                    raise UserError('Найдена проверка вне демо: удаление остановлено.')
                self.env['repka.ai.demo.result'].search([('session_id', '=', session.id)]).unlink()
                checks.unlink()
                documents.unlink()
                self.env['ufs.forwarder.order'].sudo().search([('demo_session_id', '=', session.id)]).unlink()
                self.env['ufs.base.order'].sudo().search([('demo_session_id', '=', session.id)]).unlink()
                self.env['res.partner'].sudo().search([('demo_session_id', '=', session.id)]).unlink()
            session.unlink()
        return {'type': 'ir.actions.act_window', 'res_model': self._name,
                'view_mode': 'list,form', 'target': 'current'}
