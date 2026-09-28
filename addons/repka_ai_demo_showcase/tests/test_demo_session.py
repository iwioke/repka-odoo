import json
from unittest.mock import patch

from odoo.addons.repka_ai_demo_showcase.controllers.session import DemoLogout
from odoo.addons.repka_ai_demo_showcase.models.demo_session import AUTOMATIONS
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDemoSession(TransactionCase):
    def test_four_scenarios_and_scoped_cleanup(self):
        baseline = self.env['res.partner'].create({'name': 'Контрольная запись вне демо'})
        session = self.env['repka.ai.demo.session'].create({'name': 'Показ заказчику'})
        session.action_prepare()
        self.assertEqual(session.state, 'active')
        self.assertTrue(session.partner_ids)
        self.assertTrue(session.order_ids)
        self.assertTrue(session.document_ids)
        self.assertEqual(len(session.document_ids), len(self.env['ufs.ai.document.check'].search([
            ('source_document_id', 'in', session.document_ids.ids),
        ])))
        for slug in ('customer_360', 'margin_watch', 'document_readiness', 'executive_brief'):
            with self.subTest(scenario=slug):
                result_action = getattr(session, f'action_run_{slug}')()
                result = self.env['repka.ai.demo.result'].browse(result_action['res_id'])
                self.assertEqual(result.scenario, slug)
                expected = json.loads((AUTOMATIONS / 'scenarios' / slug / 'example_output.json').read_text(encoding='utf-8'))
                self.assertEqual(json.loads(result.output_json), expected)
                self.assertTrue(result.summary)
        self.assertEqual(len(session.result_ids), 4)
        session.action_run_customer_360()
        self.assertEqual(len(session.result_ids), 5)
        partner_ids, order_ids = session.partner_ids.ids, session.order_ids.ids
        document_ids, result_ids = session.document_ids.ids, session.result_ids.ids
        session.action_finish()
        self.assertFalse(session.exists())
        self.assertFalse(self.env['res.partner'].browse(partner_ids).exists())
        self.assertFalse(self.env['ufs.base.order'].browse(order_ids).exists())
        self.assertFalse(self.env['ufs.transport.document'].browse(document_ids).exists())
        self.assertFalse(self.env['repka.ai.demo.result'].browse(result_ids).exists())
        self.assertTrue(baseline.exists())

    def test_only_one_active_showcase(self):
        first = self.env['repka.ai.demo.session'].create({})
        second = self.env['repka.ai.demo.session'].create({})
        first.action_prepare()
        with self.assertRaises(UserError):
            second.action_prepare()
        first.action_finish()
        second.action_prepare()
        self.assertEqual(second.state, 'active')

    def test_logout_cleans_only_current_showcase(self):
        session = self.env['repka.ai.demo.session'].create({})
        session.action_prepare()
        baseline = self.env['res.partner'].create({'name': 'Не относится к показу'})
        with patch('odoo.addons.repka_ai_demo_showcase.controllers.session.request') as request, \
                patch('odoo.addons.web.controllers.session.Session.logout', return_value='redirect'):
            request.db = 'repka_test'
            request.session.uid = self.env.uid
            request.session.context = self.env.context
            request.env.cr = self.env.cr
            self.assertEqual(DemoLogout().logout(), 'redirect')
        self.assertFalse(session.exists())
        self.assertTrue(baseline.exists())

    def test_cleanup_stops_if_foreign_check_uses_demo_document(self):
        session = self.env['repka.ai.demo.session'].create({})
        session.action_prepare()
        document = session.document_ids[:1]
        self.env['ufs.ai.document.check'].create({
            'name': 'Контрольная проверка вне демо', 'source_document_id': document.id,
            'is_demo': False,
        })
        with self.assertRaises(UserError):
            session.action_finish()
        self.assertTrue(session.exists())
        self.assertTrue(document.exists())
