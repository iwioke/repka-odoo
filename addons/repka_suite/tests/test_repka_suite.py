from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRepkaSuite(TransactionCase):
    def test_suite_modules_are_installed(self):
        expected = {
            "repka_base",
            "repka_currency_numeric_codes",
            "repka_oca",
            "repka_standard",
            "repka_fleet_battery",
            "repka_suite",
        }
        modules = self.env["ir.module.module"].search([
            ("name", "in", sorted(expected)),
            ("state", "=", "installed"),
        ])

        self.assertEqual(set(modules.mapped("name")), expected)
