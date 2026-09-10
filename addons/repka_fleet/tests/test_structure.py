from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLogisticsCoreStructure(TransactionCase):
    """Verify that clean-room models and key fields are present."""

    def test_models_registered(self):
        """All audited models should be registered in the pool."""
        missing = []
        expected = ['account.move', 'account.move.line', 'fleet.vehicle', 'fleet.vehicle.doc.line', 'fleet.vehicle.odometer', 'fleet.vehicle.tag', 'hr.employee', 'hr.employee.base', 'hr.employee.copy_wizard', 'hr.employee.rate', 'hr.employee.update_rates_wizard', 'ir.attachment', 'product.template', 'res.company', 'res.config.settings', 'ufs.base.order', 'ufs.cadv.request.approval.wizard', 'ufs.cargo_line', 'ufs.employee.doc.line', 'ufs.fleet.add_order.line', 'ufs.fleet.default_trip_exp_line', 'ufs.fleet.disp.board', 'ufs.fleet.downtime', 'ufs.fleet.downtime.reason', 'ufs.fleet.employee.letter_wizard', 'ufs.fleet.lorry', 'ufs.fleet.lorry.state', 'ufs.fleet.maintenance_request', 'ufs.fleet.order', 'ufs.fleet.order.cost', 'ufs.fleet.order.line', 'ufs.fleet.order.partner_info_wizard', 'ufs.fleet.reorder_wizard', 'ufs.fleet.trace', 'ufs.fleet.trip', 'ufs.fleet.trip.add_order_wizard', 'ufs.fleet.trip.docs_inout', 'ufs.fleet.trip.docs_inout.line', 'ufs.fleet.trip.driver_switch_wizard', 'ufs.fleet.trip.partner_info_wizard', 'ufs.fleet.trip.point', 'ufs.fleet.trip.segment', 'ufs.fleet.trip.switch', 'ufs.fleet.trip.switch_wizard', 'ufs.fleet.trip_time.line', 'ufs.fleet.trip_time.wizard', 'ufs.fleet.vehicle.fuel_norm', 'ufs.fleet.vehicle_copy_wizard', 'ufs.fuel.card', 'ufs.fuel.card.history', 'ufs.location', 'ufs.order.service', 'ufs.strict_doc', 'ufs.transport.document', 'ufs.trip.cadv', 'ufs.trip.cost', 'ufs.trip.cost.type', 'ufs.trip.strict_doc.line']
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
