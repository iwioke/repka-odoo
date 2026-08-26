import base64

from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestFleetBattery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["fleet.vehicle.model.brand"].create(
            {"name": "Battery Test Brand"}
        )
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create(
            {
                "name": "Battery Test Model",
                "brand_id": cls.brand.id,
            }
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {
                "model_id": cls.vehicle_model.id,
                "license_plate": "BAT-001",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Battery Producer Partner"}
        )
        cls.producer = cls.env["fleet.vehicle.battery.producer"].create(
            {
                "name": "Battery Producer",
                "partner_id": cls.partner.id,
            }
        )
        cls.capacity = cls.env["ufs.fleet.battery.capacity"].create(
            {"name": "100 Ah"}
        )
        cls.battery = cls.env["ufs.fleet.battery"].create(
            {
                "name": "SN-001",
                "vehicle_id": cls.vehicle.id,
                "installation_date": "2026-01-15",
                "manufacturer_id": cls.producer.id,
                "capacity_id": cls.capacity.id,
                "notes": "Installed for testing",
            }
        )

    def test_model_and_field_metadata(self):
        battery_model = self.env["ufs.fleet.battery"]
        battery_fields = battery_model._fields

        self.assertEqual(battery_model._description, "Fleet Battery")
        self.assertEqual(battery_model._order, "id")
        self.assertEqual(battery_fields["active"].type, "boolean")
        self.assertTrue(battery_model.default_get(["active"])["active"])
        self.assertEqual(battery_fields["name"].type, "char")
        self.assertEqual(battery_fields["name"].string, "S/N")
        self.assertTrue(battery_fields["name"].required)
        self.assertEqual(battery_fields["vehicle_id"].comodel_name, "fleet.vehicle")
        self.assertTrue(battery_fields["vehicle_id"].required)
        self.assertEqual(battery_fields["vehicle_id"].ondelete, "restrict")
        self.assertEqual(battery_fields["installation_date"].string, "Inst.")
        self.assertTrue(battery_fields["installation_date"].required)
        self.assertEqual(battery_fields["utilization_date"].string, "Utilized")
        self.assertEqual(battery_fields["notes"].type, "text")
        self.assertEqual(battery_fields["attachment_file"].type, "binary")
        self.assertEqual(battery_fields["attachment_file"].string, "Guarantee")
        self.assertEqual(
            battery_fields["manufacturer_id"].comodel_name,
            "fleet.vehicle.battery.producer",
        )
        self.assertEqual(battery_fields["manufacturer_id"].ondelete, "set null")
        self.assertEqual(
            battery_fields["capacity_id"].comodel_name,
            "ufs.fleet.battery.capacity",
        )
        self.assertEqual(battery_fields["capacity_id"].ondelete, "restrict")

        vehicle_batteries = self.env["fleet.vehicle"]._fields["battery_ids"]
        self.assertEqual(vehicle_batteries.type, "one2many")
        self.assertEqual(vehicle_batteries.comodel_name, "ufs.fleet.battery")
        self.assertEqual(vehicle_batteries.inverse_name, "vehicle_id")
        self.assertEqual(vehicle_batteries.string, "Batteries")

        producer_model = self.env["fleet.vehicle.battery.producer"]
        producer_fields = producer_model._fields
        self.assertEqual(producer_model._description, "Battery Producer")
        self.assertEqual(producer_model._order, "id")
        self.assertEqual(producer_fields["name"].type, "char")
        self.assertEqual(producer_fields["partner_id"].comodel_name, "res.partner")
        self.assertEqual(producer_fields["partner_id"].string, "Partner Link")
        self.assertEqual(producer_fields["partner_id"].ondelete, "set null")

        capacity_model = self.env["ufs.fleet.battery.capacity"]
        capacity_fields = capacity_model._fields
        self.assertEqual(capacity_model._order, "id")
        self.assertTrue(capacity_model.default_get(["active"])["active"])
        self.assertEqual(capacity_fields["name"].type, "char")
        self.assertEqual(capacity_fields["name"].string, "Capacity")

    def test_relations_and_active_defaults(self):
        self.assertEqual(self.battery.vehicle_id, self.vehicle)
        self.assertEqual(self.battery.manufacturer_id, self.producer)
        self.assertEqual(self.battery.capacity_id, self.capacity)
        self.assertIn(self.battery, self.vehicle.battery_ids)
        self.assertTrue(self.battery.active)
        self.assertTrue(self.capacity.active)

    def test_binary_guarantee_and_utilized_records(self):
        guarantee = base64.b64encode(b"guarantee document")
        self.battery.attachment_file = guarantee
        self.assertEqual(
            base64.b64decode(self.battery.attachment_file),
            b"guarantee document",
        )

        utilized = self.env["ufs.fleet.battery"].create(
            {
                "name": "SN-UTILIZED",
                "vehicle_id": self.vehicle.id,
                "installation_date": "2025-01-01",
                "utilization_date": "2026-02-01",
            }
        )
        batteries = self.env["ufs.fleet.battery"].search(
            [
                ("id", "in", (self.battery | utilized).ids),
                ("utilization_date", "!=", False),
            ]
        )

        self.assertEqual(batteries, utilized)
        self.assertEqual(
            utilized.utilization_date,
            fields.Date.to_date("2026-02-01"),
        )

    def test_set_null_relations(self):
        producer = self.env["fleet.vehicle.battery.producer"].create(
            {"name": "Temporary Producer"}
        )
        battery = self.env["ufs.fleet.battery"].create(
            {
                "name": "SN-SET-NULL",
                "vehicle_id": self.vehicle.id,
                "installation_date": "2026-03-01",
                "manufacturer_id": producer.id,
            }
        )
        producer.unlink()
        self.assertFalse(battery.manufacturer_id)

        partner = self.env["res.partner"].create({"name": "Temporary Partner"})
        producer = self.env["fleet.vehicle.battery.producer"].create(
            {
                "name": "Partner Linked Producer",
                "partner_id": partner.id,
            }
        )
        partner.unlink()
        self.assertFalse(producer.partner_id)

    def test_restrict_relations(self):
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(IntegrityError):
                with self.cr.savepoint():
                    self.capacity.unlink()
            with self.assertRaises(IntegrityError):
                with self.cr.savepoint():
                    self.vehicle.unlink()

        self.assertTrue(self.capacity.exists())
        self.assertTrue(self.vehicle.exists())
        self.assertTrue(self.battery.exists())
