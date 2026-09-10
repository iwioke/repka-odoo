from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLogisticsCoreStructure(TransactionCase):
    """Verify that clean-room models and key fields are present."""

    def test_models_registered(self):
        """All audited models should be registered in the pool."""
        missing = []
        expected = ['product.product', 'product.template', 'ufs.fleet.refuel', 'ufs.fleet.refuel.update.wizard', 'ufs.fleet.refuel.v_update_wizard', 'ufs.fleet.trip', 'ufs.fuel.api.cards', 'ufs.fuel.api.interface', 'ufs.fuel.api.parser', 'ufs.fuel.api.parser.bl', 'ufs.fuel.api.parser.bn', 'ufs.fuel.api.parser.bp_pl', 'ufs.fuel.api.parser.diesel24', 'ufs.fuel.api.parser.dkv', 'ufs.fuel.api.parser.dornet', 'ufs.fuel.api.parser.e100', 'ufs.fuel.api.parser.e100pro', 'ufs.fuel.api.parser.gp', 'ufs.fuel.api.parser.gpncard', 'ufs.fuel.api.parser.okko', 'ufs.fuel.api.parser.rosneft', 'ufs.fuel.api.parser.shell', 'ufs.fuel.api.parser.ukrnafta', 'ufs.fuel.api.parser.wog', 'ufs.fuel.api.parser.zap_online', 'ufs.fuel.api.provider', 'ufs.fuel.card', 'ufs.trip.cost']
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
