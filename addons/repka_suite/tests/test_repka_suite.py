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

    def test_custom_app_menu_icons(self):
        expected = {
            "repka_fleet.menu_256": "transport.svg",
            "repka_forwarding.menu_293": "forwarding.svg",
            "repka_special_lm.menu_487": "goods.svg",
            "repka_fleet_waybill.menu_291": "waybill.svg",
            "repka_fleet_wallet.menu_311": "wallet.svg",
            "repka_logistics_core.menu_240": "ufs.svg",
        }

        for xml_id, filename in expected.items():
            menu = self.env.ref(xml_id)
            self.assertEqual(
                menu.web_icon,
                f"repka_suite,static/description/{filename}",
            )
