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

    def test_admin_has_forwarding_access(self):
        admin = self.env.ref("base.user_admin")

        self.assertTrue(admin.has_group("repka_forwarding.group_56"))
        self.assertTrue(admin.has_group("repka_forwarding.group_57"))
        self.env["ufs.forwarder.order.line"].with_user(admin).check_access("read")

    def test_forwarder_order_input_fields_are_editable(self):
        editable = {
            "name",
            "partner_id",
            "incoming_ref",
            "external_nr",
            "order_date",
            "ufs_contract_id",
            "ufs_payment_term_id",
            "n_days_count",
            "order_finish_date",
            "print_stamp",
            "company_id",
            "order_type",
            "responsible_user_id",
            "freight_amount",
            "freight_currency_id",
            "carrier_id",
            "carrier_rate",
        }
        calculated = {
            "parent_partner_id",
            "margin",
            "amount",
            "amount_company_currency",
            "profitability_by_sub",
            "full_profitability",
        }
        order_fields = self.env["ufs.forwarder.order"]._fields

        self.assertFalse({name for name in editable if order_fields[name].readonly})
        self.assertFalse({name for name in calculated if not order_fields[name].readonly})

    def test_forwarder_order_inputs_are_saved_to_base_order(self):
        partner = self.env["res.partner"].create({"name": "Test Customer"})
        order = self.env["ufs.forwarder.order"].create({
            "name": "TEST/INPUT",
            "partner_id": partner.id,
            "incoming_ref": "IN-42",
            "external_nr": "EXT-42",
            "order_date": "2026-09-10",
            "n_days_count": 14,
            "order_finish_date": "2026-09-24",
            "print_stamp": True,
            "order_type": "customer",
            "freight_amount": 1250.0,
            "freight_currency_id": self.env.company.currency_id.id,
            "carrier_id": partner.id,
            "carrier_rate": 900.0,
        })
        base_order = order.base_order_id

        self.assertEqual(base_order.name, "TEST/INPUT")
        self.assertEqual(base_order.partner_id, partner)
        self.assertEqual(base_order.incoming_ref, "IN-42")
        self.assertEqual(base_order.external_nr, "EXT-42")
        self.assertEqual(base_order.n_days_count, 14)
        self.assertTrue(base_order.print_stamp)
        self.assertEqual(base_order.order_type, "customer")
        self.assertEqual(base_order.freight_amount, 1250.0)
        self.assertEqual(base_order.carrier_id, partner)
        self.assertEqual(base_order.carrier_rate, 900.0)
