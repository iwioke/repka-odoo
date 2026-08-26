from odoo.tests import TransactionCase, tagged


EXPECTED_VERSIONS = {
    "base_fontawesome": "18.0.1.0.0",
    "base_view_inheritance_extension": "18.0.1.0.1",
    "currency_rate_update": "18.0.1.0.1",
    "jsonifier": "18.0.1.1.0",
    "web_chatter_position": "18.0.1.0.0",
    "web_notify": "18.0.1.1.0",
    "web_responsive": "18.0.1.0.0",
    "web_timeline": "18.0.1.0.3",
}


@tagged("post_install", "-at_install")
class TestOcaModules(TransactionCase):
    def test_expected_oca_versions_are_installed(self):
        modules = self.env["ir.module.module"].search([
            ("name", "in", sorted(EXPECTED_VERSIONS)),
        ])
        actual = {
            module.name: module.installed_version
            for module in modules
            if module.state == "installed"
        }

        self.assertEqual(actual, EXPECTED_VERSIONS)
