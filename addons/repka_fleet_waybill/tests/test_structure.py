from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLogisticsCoreStructure(TransactionCase):
    """Verify that clean-room models and key fields are present."""

    def test_models_registered(self):
        """All audited models should be registered in the pool."""
        missing = []
        expected = ['res.company', 'res.config.settings', 'ufs.fleet.trip', 'ufs.trip.cadv', 'ufs.waybill']
        for name in expected:
            try:
                self.env[name]
            except KeyError:
                missing.append(name)
        self.assertFalse(missing, f"Missing models: {missing}")

    def test_key_fields_present(self):
        """Spot-check key fields on core models."""
        # ufs.base.order must have partner_id and state_id
        order = self.env["ufs.base.order"]._fields
        self.assertIn("partner_id", order)
        self.assertIn("state_id", order)
        # ufs.cargo_line must have cargo_id
        cargo_line = self.env["ufs.cargo_line"]._fields
        self.assertIn("cargo_id", cargo_line)
        # ufs.contract must have partner_id and number
        contract = self.env["ufs.contract"]._fields
        self.assertIn("partner_id", contract)
        self.assertIn("number", contract)
