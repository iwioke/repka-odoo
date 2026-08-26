from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepkaBase(TransactionCase):
    def test_manager_inherits_user_group(self):
        user_group = self.env.ref("repka_base.group_repka_user")
        manager_group = self.env.ref("repka_base.group_repka_manager")

        self.assertIn(user_group, manager_group.implied_ids)

    def test_russian_language_is_active(self):
        language = self.env["res.lang"].with_context(active_test=False).search([
            ("code", "=", "ru_RU"),
        ], limit=1)

        self.assertTrue(language.active)
