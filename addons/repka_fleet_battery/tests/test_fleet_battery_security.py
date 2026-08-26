from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged("post_install", "-at_install")
class TestFleetBatterySecurity(TransactionCase):
    model_names = (
        "ufs.fleet.battery",
        "fleet.vehicle.battery.producer",
        "ufs.fleet.battery.capacity",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordinary_user = new_test_user(
            cls.env,
            login="battery_ordinary_user",
            groups="base.group_user",
        )
        cls.fleet_user = new_test_user(
            cls.env,
            login="battery_fleet_user",
            groups="fleet.fleet_group_user",
        )
        cls.battery_manager = new_test_user(
            cls.env,
            login="battery_manager",
            groups="repka_fleet_battery.group_battery_manager",
        )
        cls.brand = cls.env["fleet.vehicle.model.brand"].create(
            {"name": "Battery Security Brand"}
        )
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "Battery Security Model",
                "brand_id": cls.brand.id,
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.vehicle_model.id,
                "license_plate": "SEC-001",
                "driver_id": cls.battery_manager.partner_id.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Battery Security Partner"}
        )
        cls.producer = cls.env["fleet.vehicle.battery.producer"].create(
            {
                "name": "Security Producer",
                "partner_id": cls.partner.id,
            }
        )
        cls.capacity = cls.env["ufs.fleet.battery.capacity"].create(
            {"name": "Security Capacity"}
        )
        cls.battery = cls.env["ufs.fleet.battery"].create(
            {
                "name": "SEC-BATTERY",
                "vehicle_id": cls.vehicle.id,
                "installation_date": "2026-04-01",
                "manufacturer_id": cls.producer.id,
                "capacity_id": cls.capacity.id,
            }
        )
        cls.records = {
            "ufs.fleet.battery": cls.battery,
            "fleet.vehicle.battery.producer": cls.producer,
            "ufs.fleet.battery.capacity": cls.capacity,
        }

    def _create_values(self, model_name, suffix):
        if model_name == "ufs.fleet.battery":
            return {
                "name": f"BATTERY-{suffix}",
                "vehicle_id": self.vehicle.id,
                "installation_date": "2026-05-01",
                "manufacturer_id": self.producer.id,
                "capacity_id": self.capacity.id,
            }
        if model_name == "fleet.vehicle.battery.producer":
            return {
                "name": f"PRODUCER-{suffix}",
                "partner_id": self.partner.id,
            }
        return {"name": f"CAPACITY-{suffix}"}

    def test_access_control_records(self):
        fleet_group = self.env.ref("fleet.fleet_group_user")
        manager_group = self.env.ref("repka_fleet_battery.group_battery_manager")
        expected = {
            ("ufs.fleet.battery", fleet_group.id): (True, False, False, False),
            ("ufs.fleet.battery", manager_group.id): (True, True, True, False),
            (
                "fleet.vehicle.battery.producer",
                fleet_group.id,
            ): (True, False, False, False),
            (
                "fleet.vehicle.battery.producer",
                manager_group.id,
            ): (True, True, True, False),
            (
                "ufs.fleet.battery.capacity",
                fleet_group.id,
            ): (True, False, False, False),
            (
                "ufs.fleet.battery.capacity",
                manager_group.id,
            ): (True, True, True, False),
        }
        model_records = self.env["ir.model"].search(
            [("model", "in", self.model_names)]
        )
        access_records = self.env["ir.model.access"].search(
            [("model_id", "in", model_records.ids)]
        )
        actual = {
            (access.model_id.model, access.group_id.id): (
                access.perm_read,
                access.perm_write,
                access.perm_create,
                access.perm_unlink,
            )
            for access in access_records
        }

        self.assertEqual(actual, expected)
        self.assertIn(fleet_group, manager_group.implied_ids)

    def test_no_record_rules_or_company_fields(self):
        model_records = self.env["ir.model"].search(
            [("model", "in", self.model_names)]
        )
        rules = self.env["ir.rule"].search(
            [("model_id", "in", model_records.ids)]
        )

        self.assertFalse(rules)
        for model_name in self.model_names:
            with self.subTest(model=model_name):
                self.assertNotIn("company_id", self.env[model_name]._fields)

    def test_ordinary_user_has_no_access(self):
        for model_name in self.model_names:
            record = self.records[model_name]
            model = self.env[model_name].with_user(self.ordinary_user)
            with self.subTest(model=model_name, operation="read"):
                with self.assertRaises(AccessError):
                    record.with_user(self.ordinary_user).read(["name"])
            with self.subTest(model=model_name, operation="search"):
                with self.assertRaises(AccessError):
                    model.search([])
            with self.subTest(model=model_name, operation="create"):
                with self.assertRaises(AccessError):
                    model.create(self._create_values(model_name, "ORDINARY"))
            with self.subTest(model=model_name, operation="write"):
                with self.assertRaises(AccessError):
                    record.with_user(self.ordinary_user).write(
                        {"name": "Ordinary Write"}
                    )
            with self.subTest(model=model_name, operation="unlink"):
                with self.assertRaises(AccessError):
                    record.with_user(self.ordinary_user).unlink()

    def test_fleet_user_has_read_only_access(self):
        for model_name in self.model_names:
            record = self.records[model_name]
            model = self.env[model_name].with_user(self.fleet_user)
            with self.subTest(model=model_name, operation="read"):
                self.assertEqual(
                    record.with_user(self.fleet_user).read(["name"])[0]["name"],
                    record.name,
                )
                self.assertIn(record, model.search([("id", "=", record.id)]))
            with self.subTest(model=model_name, operation="create"):
                with self.assertRaises(AccessError):
                    model.create(self._create_values(model_name, "FLEET"))
            with self.subTest(model=model_name, operation="write"):
                with self.assertRaises(AccessError):
                    record.with_user(self.fleet_user).write({"name": "Fleet Write"})
            with self.subTest(model=model_name, operation="unlink"):
                with self.assertRaises(AccessError):
                    record.with_user(self.fleet_user).unlink()

    def test_battery_manager_can_read_write_create_but_not_unlink(self):
        for model_name in self.model_names:
            model = self.env[model_name].with_user(self.battery_manager)
            with self.subTest(model=model_name, operation="create"):
                record = model.create(self._create_values(model_name, "MANAGER"))
                self.assertTrue(record.exists())
            with self.subTest(model=model_name, operation="read"):
                self.assertIn(record, model.search([("id", "=", record.id)]))
            with self.subTest(model=model_name, operation="write"):
                record.write({"name": "Manager Write"})
                self.assertEqual(record.name, "Manager Write")
            with self.subTest(model=model_name, operation="unlink"):
                with self.assertRaises(AccessError):
                    record.unlink()
