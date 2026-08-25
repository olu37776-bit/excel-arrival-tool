from datetime import date
from decimal import Decimal
import unittest

from revenue_tool.domain.models import PreviousRevenueLine, RevenueLine
from revenue_tool.services.comparison import compare_revenue_months


class ComparisonTest(unittest.TestCase):
    def test_only_one_month_or_more_delays_are_returned(self) -> None:
        previous = [self._previous("REV-1", "2026-07"), self._previous("REV-2", "2026-08")]
        current = [self._current("REV-1", "2026-08"), self._current("REV-2", "2026-08")]

        result = compare_revenue_months(current, previous, 1, only_delayed=True)

        self.assertEqual(1, len(result))
        self.assertEqual("REV-1", result[0].business_key)
        self.assertEqual(1, result[0].delay_months)
        self.assertTrue(result[0].delayed)

    @staticmethod
    def _previous(key: str, month: str) -> PreviousRevenueLine:
        return PreviousRevenueLine(key, "PO-1", "C-1", "SP-1", key, month)

    @staticmethod
    def _current(key: str, month: str) -> RevenueLine:
        return RevenueLine(
            business_key=key,
            po_number="PO-1",
            contract_number="C-1",
            shipping_point="SP-1",
            shipment_id=key,
            trade_type="SEA",
            prd=date(2026, 1, 1),
            original_po_quantity=Decimal("100"),
            plan_date=date(2026, 1, 1),
            plan_quantity=Decimal("100"),
            transit_days=0,
            arrival_date=date(2026, 1, 1),
            revenue_month=month,
            revenue_amount=Decimal("5000"),
        )


if __name__ == "__main__":
    unittest.main()

