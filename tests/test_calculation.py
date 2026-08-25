from datetime import date
from decimal import Decimal
import unittest

from revenue_tool.domain.models import PrdRecord, ShipmentRecord, TransitRule
from revenue_tool.rules.grouping import PrdSelectionRule, ShipmentGroupingRule
from revenue_tool.rules.transit import TransitDaysResolver
from revenue_tool.services.calculation import RevenueCalculator


class RevenueCalculatorTest(unittest.TestCase):
    def test_earliest_prd_max_quantity_and_adjusted_transit(self) -> None:
        calculator = RevenueCalculator(
            ShipmentGroupingRule(
                [
                    "po_number",
                    "contract_number",
                    "shipping_point",
                    "plan_date",
                    "plan_quantity",
                    "trade_type",
                    "shipment_id",
                ]
            ),
            PrdSelectionRule(date_aggregation="min", quantity_aggregation="max"),
            TransitDaysResolver(
                [TransitRule("SEA", 40)],
                {"SEA": {"extra_days": 5}},
            ),
        )
        prds = [
            PrdRecord("PO-1", date(2026, 1, 10), Decimal("90")),
            PrdRecord("PO-1", date(2026, 1, 5), Decimal("100")),
        ]
        shipments = [
            ShipmentRecord(
                po_number="PO-1",
                plan_date=date(2026, 1, 20),
                plan_quantity=Decimal("90"),
                contract_number="C-1",
                shipping_point="SP-1",
                trade_type="SEA",
                shipment_id="S-1",
            )
        ]

        result = calculator.calculate(prds, shipments)

        self.assertEqual(1, len(result))
        self.assertEqual(date(2026, 1, 5), result[0].prd)
        self.assertEqual(Decimal("100"), result[0].original_po_quantity)
        self.assertEqual(45, result[0].transit_days)
        self.assertEqual(date(2026, 3, 6), result[0].arrival_date)
        self.assertEqual("2026-03", result[0].revenue_month)


if __name__ == "__main__":
    unittest.main()

