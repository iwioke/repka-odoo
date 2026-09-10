from xml.etree import ElementTree

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
            "sl_freight_responsible_id",
            "sl_mark_responsible_id",
            "sl_ved_responsible_id",
        }
        calculated = {
            "parent_partner_id",
            "margin",
            "amount",
            "amount_company_currency",
            "profitability_by_sub",
            "full_profitability",
            "sl_freight_amount",
            "sl_mark_amount",
            "sl_ved_amount",
            "sl_freight_margin",
            "sl_mark_margin",
            "sl_ved_margin",
            "invoice_states_char",
        }
        order_fields = self.env["ufs.forwarder.order"]._fields

        self.assertFalse({name for name in editable if order_fields[name].readonly})
        self.assertFalse({name for name in calculated if not order_fields[name].readonly})

    def test_forwarder_order_inputs_are_saved_to_base_order(self):
        partner = self.env["res.partner"].create({"name": "Test Customer"})
        product = self.env["product.product"].create({
            "name": "Test Freight Service",
            "type": "service",
        })
        currency = self.env.company.currency_id
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
            "freight_currency_id": currency.id,
            "carrier_id": partner.id,
            "carrier_rate": 900.0,
            "sl_freight_responsible_id": self.env.user.id,
            "sl_mark_responsible_id": self.env.user.id,
            "sl_ved_responsible_id": self.env.user.id,
            "services_included_line_ids": [(0, 0, {
                "product_id": product.id,
                "qty": 1.0,
                "price": 1250.0,
                "currency_id": currency.id,
            })],
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
        self.assertEqual(order.sl_freight_responsible_id, self.env.user)
        self.assertEqual(order.sl_mark_responsible_id, self.env.user)
        self.assertEqual(order.sl_ved_responsible_id, self.env.user)
        self.assertEqual(len(base_order.services_included_line_ids), 1)
        service = base_order.services_included_line_ids
        self.assertEqual(service.product_id, product)
        self.assertEqual(service.qty, 1.0)
        self.assertEqual(service.price, 1250.0)
        self.assertEqual(service.amount, 1250.0)
        self.assertEqual(service.currency_id, currency)

    def test_forwarder_services_and_financial_summary_order(self):
        view = self.env.ref("repka_suite.forwarder_order_reference_form")
        arch = view.arch_db
        root = ElementTree.fromstring(arch)
        summary = root.find(".//group[@class='o_forwarder_financial_summary']")
        expected_columns = [
            [
                "amount",
                "sl_freight_amount",
                "sl_freight_margin",
                "sl_freight_responsible_id",
                "invoice_states_char",
            ],
            [
                "profitability_by_sub",
                "sl_mark_amount",
                "sl_mark_margin",
                "sl_mark_responsible_id",
            ],
            [
                "amount_company_currency",
                "sl_ved_amount",
                "sl_ved_margin",
                "sl_ved_responsible_id",
            ],
        ]

        self.assertIsNotNone(summary)
        columns = summary.findall("./group")
        self.assertEqual(len(columns), 3)
        for column, expected in zip(columns, expected_columns):
            self.assertEqual([field.attrib["name"] for field in column.findall("./field")], expected)
            self.assertEqual([label.attrib["for"] for label in column.findall("./label")], expected)
        self.assertLess(arch.index('name="freight_amount"'), arch.index('name="services_included_line_ids"'))
        self.assertLess(arch.index('name="services_included_line_ids"'), arch.index('class="o_forwarder_financial_summary"'))
        self.assertNotIn('name="forwarder_services"', arch)
