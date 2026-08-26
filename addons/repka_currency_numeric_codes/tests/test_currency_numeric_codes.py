from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCurrencyNumericCodes(TransactionCase):
    def test_numeric_code_field_matches_source_metadata(self):
        field = self.env["res.currency"]._fields["numeric_code"]

        self.assertEqual(field.type, "char")
        self.assertEqual(field.string, "ISO 4217 Code")
        self.assertFalse(field.required)
        self.assertFalse(field.readonly)
        self.assertTrue(field.store)
        self.assertFalse(field.index)
        self.assertFalse(field.translate)

    def test_numeric_code_round_trip(self):
        currency = self.env["res.currency"].create({
            "name": "XZZ",
            "symbol": "T",
            "rounding": 0.01,
            "numeric_code": "963",
        })

        self.assertEqual(currency.numeric_code, "963")
