from datetime import date
from decimal import Decimal
import unittest

from revenue_tool.domain.models import ShipmentRecord
from revenue_tool.rules.grouping import ShipmentGroupingRule


class ShipmentGroupingRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = ShipmentGroupingRule(
            same_fields=[
                "po_number",
                "contract_number",
                "shipping_point",
                "plan_date",
                "plan_quantity",
                "trade_type",
                "shipment_id",
            ]
        )

    def test_exact_duplicate_is_counted_once(self) -> None:
        row = self._shipment(source_row=2)
        duplicate = self._shipment(source_row=3)

        result = self.rule.apply([row, duplicate])

        self.assertEqual(1, len(result))
        self.assertEqual(Decimal("100"), result[0].plan_quantity)

    def test_different_contract_or_shipping_point_stays_separate(self) -> None:
        rows = [
            self._shipment(source_row=2),
            self._shipment(source_row=3, contract_number="C-2"),
            self._shipment(source_row=4, shipping_point="SP-2"),
        ]

        result = self.rule.apply(rows)

        self.assertEqual(3, len(result))

    def test_different_quantity_stays_separate(self) -> None:
        rows = [
            self._shipment(source_row=2, plan_quantity=Decimal("100")),
            self._shipment(source_row=3, plan_quantity=Decimal("80")),
        ]

        result = self.rule.apply(rows)

        self.assertEqual(2, len(result))

    @staticmethod
    def _shipment(**changes) -> ShipmentRecord:
        values = {
            "po_number": "PO-1",
            "plan_date": date(2026, 1, 20),
            "plan_quantity": Decimal("100"),
            "contract_number": "C-1",
            "shipping_point": "SP-1",
            "trade_type": "SEA",
            "shipment_id": "S-1",
            "revenue_amount": Decimal("2500"),
            "source_row": 2,
        }
        values.update(changes)
        return ShipmentRecord(**values)


if __name__ == "__main__":
    unittest.main()

