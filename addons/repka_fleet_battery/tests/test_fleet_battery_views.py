import ast

from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFleetBatteryViews(TransactionCase):
    def _arch(self, xml_id):
        view = self.env.ref(xml_id)
        return etree.fromstring(view.arch.encode())

    def test_manifest_and_security_group_metadata(self):
        module = self.env["ir.module.module"].search(
            [("name", "=", "repka_fleet_battery")],
            limit=1,
        )
        category = self.env.ref("repka_fleet_battery.module_category_ufs_tech")
        manager_group = self.env.ref("repka_fleet_battery.group_battery_manager")
        fleet_group = self.env.ref("fleet.fleet_group_user")

        self.assertEqual(module.installed_version, "18.0.1.1.0")
        self.assertEqual(module.license, "LGPL-3")
        self.assertIn("fleet", module.dependencies_id.mapped("name"))
        self.assertEqual(category.name, "UFS Tech")
        self.assertEqual(category.sequence, 2)
        self.assertTrue(category.visible)
        self.assertEqual(manager_group.name, "Battery Manager")
        self.assertEqual(manager_group.category_id, category)
        self.assertIn(fleet_group, manager_group.implied_ids)

    def test_battery_list_view(self):
        arch = self._arch("repka_fleet_battery.view_ufs_fleet_battery_list")

        self.assertEqual(arch.tag, "list")
        self.assertEqual(
            arch.xpath("./field/@name"),
            [
                "name",
                "manufacturer_id",
                "capacity_id",
                "vehicle_id",
                "installation_date",
                "utilization_date",
                "notes",
            ],
        )

    def test_battery_form_view(self):
        arch = self._arch("repka_fleet_battery.view_ufs_fleet_battery_form")
        columns = arch.xpath("./sheet/group[1]/group")

        self.assertEqual(len(columns), 2)
        self.assertEqual(
            columns[0].xpath("./field/@name"),
            ["name", "vehicle_id", "manufacturer_id", "capacity_id"],
        )
        self.assertEqual(
            columns[1].xpath("./field/@name"),
            ["installation_date", "utilization_date"],
        )
        self.assertEqual(
            arch.xpath("./sheet/group[2]/field/@name"),
            ["notes", "attachment_file"],
        )
        for field_name in ("vehicle_id", "manufacturer_id", "capacity_id"):
            field = arch.xpath(f".//field[@name='{field_name}']")[0]
            self.assertTrue(ast.literal_eval(field.get("options"))["no_create"])

    def test_battery_search_view(self):
        arch = self._arch("repka_fleet_battery.view_ufs_fleet_battery_search")
        utilized = arch.xpath("./filter[@name='utilized']")[0]
        vehicle_group = arch.xpath(
            ".//filter[@name='group_by_vehicle']"
        )[0]
        installation_group = arch.xpath(
            ".//filter[@name='group_by_installation_month']"
        )[0]

        self.assertEqual(arch.xpath("./field/@name"), ["name", "vehicle_id"])
        self.assertEqual(
            ast.literal_eval(utilized.get("domain")),
            [("utilization_date", "!=", False)],
        )
        self.assertEqual(
            ast.literal_eval(vehicle_group.get("context")),
            {"group_by": "vehicle_id"},
        )
        self.assertEqual(
            ast.literal_eval(installation_group.get("context")),
            {"group_by": "installation_date:month"},
        )

    def test_vehicle_form_battery_page(self):
        inherited_view = self.env.ref(
            "repka_fleet_battery.view_fleet_vehicle_form_batteries"
        )
        stock_view = self.env.ref("fleet.fleet_vehicle_view_form")
        inherited_arch = etree.fromstring(inherited_view.arch.encode())
        combined_view = self.env["fleet.vehicle"].get_view(
            view_id=stock_view.id,
            view_type="form",
        )
        combined_arch = etree.fromstring(combined_view["arch"].encode())

        self.assertEqual(inherited_view.inherit_id, stock_view)
        self.assertEqual(
            inherited_arch.xpath("./@expr"),
            ["//notebook"],
        )
        embedded_lists = combined_arch.xpath(
            "//page[@name='batteries']/field[@name='battery_ids']/list"
        )
        self.assertEqual(len(embedded_lists), 1)
        self.assertEqual(
            embedded_lists[0].xpath("./field/@name"),
            [
                "name",
                "manufacturer_id",
                "capacity_id",
                "installation_date",
                "utilization_date",
                "notes",
            ],
        )

    def test_producer_and_capacity_views(self):
        producer_list = self.env.ref(
            "repka_fleet_battery.view_fleet_vehicle_battery_producer_list"
        )
        producer_arch = etree.fromstring(producer_list.arch.encode())
        module_view_data = self.env["ir.model.data"].search([
            ("module", "=", "repka_fleet_battery"),
            ("model", "=", "ir.ui.view"),
        ])
        module_views = self.env["ir.ui.view"].browse(module_view_data.mapped("res_id"))

        self.assertEqual(producer_arch.tag, "list")
        self.assertEqual(producer_arch.xpath("./field/@name"), ["name", "partner_id"])
        self.assertEqual(
            module_views.filtered(
                lambda view: view.model == "fleet.vehicle.battery.producer"
            ),
            producer_list,
        )
        self.assertFalse(
            module_views.filtered(
                lambda view: view.model == "ufs.fleet.battery.capacity"
            )
        )

    def test_window_actions(self):
        action_specs = {
            "repka_fleet_battery.action_ufs_fleet_battery": (
                "ufs.fleet.battery",
                "Batteries",
            ),
            "repka_fleet_battery.action_fleet_vehicle_battery_producer": (
                "fleet.vehicle.battery.producer",
                "Battery Producers",
            ),
            "repka_fleet_battery.action_ufs_fleet_battery_capacity": (
                "ufs.fleet.battery.capacity",
                "Battery Capacity",
            ),
        }
        for xml_id, (model_name, action_name) in action_specs.items():
            with self.subTest(action=xml_id):
                action = self.env.ref(xml_id)
                self.assertEqual(action.name, action_name)
                self.assertEqual(action.res_model, model_name)
                self.assertEqual(action.view_mode, "list,form")
                self.assertEqual(action.limit, 80)

        battery_action = self.env.ref(
            "repka_fleet_battery.action_ufs_fleet_battery"
        )
        self.assertEqual(
            battery_action.search_view_id,
            self.env.ref("repka_fleet_battery.view_ufs_fleet_battery_search"),
        )

    def test_menu_hierarchy_actions_and_sequences(self):
        battery_menu = self.env.ref("repka_fleet_battery.menu_fleet_batteries")
        configuration_menu = self.env.ref(
            "repka_fleet_battery.menu_fleet_battery_configuration"
        )
        producer_menu = self.env.ref(
            "repka_fleet_battery.menu_fleet_battery_producers"
        )
        capacity_menu = self.env.ref(
            "repka_fleet_battery.menu_fleet_battery_capacity"
        )

        self.assertEqual(battery_menu.name, "Batteries")
        self.assertEqual(battery_menu.parent_id, self.env.ref("fleet.fleet_vehicles"))
        self.assertEqual(
            battery_menu.action,
            self.env.ref("repka_fleet_battery.action_ufs_fleet_battery"),
        )
        self.assertEqual(battery_menu.sequence, 60)
        self.assertEqual(configuration_menu.name, "Batteries")
        self.assertEqual(
            configuration_menu.parent_id,
            self.env.ref("fleet.fleet_config_settings_menu"),
        )
        self.assertEqual(configuration_menu.sequence, 60)
        self.assertFalse(configuration_menu.action)
        self.assertEqual(producer_menu.parent_id, configuration_menu)
        self.assertEqual(producer_menu.name, "Battery Producers")
        self.assertEqual(producer_menu.sequence, 10)
        self.assertEqual(
            producer_menu.action,
            self.env.ref(
                "repka_fleet_battery.action_fleet_vehicle_battery_producer"
            ),
        )
        self.assertEqual(capacity_menu.parent_id, configuration_menu)
        self.assertEqual(capacity_menu.name, "Battery Capacity")
        self.assertEqual(capacity_menu.sequence, 60)
        self.assertEqual(
            capacity_menu.action,
            self.env.ref("repka_fleet_battery.action_ufs_fleet_battery_capacity"),
        )
