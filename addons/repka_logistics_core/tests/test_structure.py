from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLogisticsCoreStructure(TransactionCase):
    """Verify that clean-room models and key fields are present."""

    def test_models_registered(self):
        """All audited models should be registered in the pool."""
        missing = []
        expected = [
            "account.move", "account.move.act", "account.move.line",
            "fleet.vehicle", "fleet.vehicle.model", "fleet.vehicle.odometer",
            "fleet.vehicle.power_type", "fleet.vehicle.trailer_type",
            "hr.employee", "product.product",
            "res.bank", "res.company", "res.partner", "res.partner.bank",
            "res.partner.credit_limit", "res.partner.doc.preference", "res.users",
            "ufs.base.equipment", "ufs.base.equipment.line", "ufs.base.equipment.log",
            "ufs.base.order", "ufs.base.trace",
            "ufs.cargo", "ufs.cargo_line",
            "ufs.contract", "ufs.contract.doc.preference",
            "ufs.doc", "ufs.doc.type",
            "ufs.driver",
            "ufs.location",
            "ufs.order.category", "ufs.order.service", "ufs.order.state",
            "ufs.partner.doc.line",
            "ufs.payment.term",
            "ufs.strict_doc", "ufs.strict_doc.subtype",
            "ufs.tracking.system", "ufs.tracking.system.refill",
            "ufs.transport.document", "ufs.transport.document.type",
            "ufs.u_guid",
            "ufs.vehicle",
        ]
        for name in expected:
            try:
                self.env[name]
            except KeyError:
                missing.append(name)
        self.assertFalse(missing, f"Missing models: {missing}")

    def test_key_fields_present(self):
        """Spot-check key fields on core models."""
        order = self.env["ufs.base.order"]._fields
        self.assertIn("partner_id", order)
        self.assertIn("state_id", order)
        cargo_line = self.env["ufs.cargo_line"]._fields
        self.assertIn("cargo_id", cargo_line)
        contract = self.env["ufs.contract"]._fields
        self.assertIn("partner_id", contract)
        self.assertIn("number", contract)
