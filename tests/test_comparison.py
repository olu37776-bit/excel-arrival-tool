from datetime import date
import unittest

from revenue_tool.domain.models import BaseRow, IssueLog, PreviousData
from revenue_tool.services.comparison import compare_revenue_months
from revenue_tool.services.normalization import business_key_identity


class ComparisonTest(unittest.TestCase):
    def test_cross_year_month_difference_and_empty_states(self) -> None:
        previous = PreviousData(
            {
                business_key_identity("C1", "SC1"): self._row(
                    "C1", "SC1", "2025-12"
                ),
                business_key_identity("C2", "SC2"): self._row(
                    "C2", "SC2", "2026-02"
                ),
                business_key_identity("C3", "SC3"): self._row(
                    "C3", "SC3", None
                ),
            }
        )
        current = [
            self._row("C1", "SC1", "2026-02"),
            self._row("C2", "SC2", None),
            self._row("C3", "SC3", "2026-01"),
        ]
        issues = IssueLog()

        result = compare_revenue_months(
            current, previous, "rpd", "current.xlsx", issues
        )

        by_contract = {
            row.values["contract_no"]: row.values for row in result
        }
        self.assertEqual("延后", by_contract["C1"]["direction"])
        self.assertEqual(2, by_contract["C1"]["change_months"])
        self.assertEqual("取消", by_contract["C2"]["direction"])
        self.assertIsNone(by_contract["C2"]["change_months"])
        self.assertEqual("新增", by_contract["C3"]["direction"])

    @staticmethod
    def _row(contract: str, center: str, month: str | None) -> BaseRow:
        return BaseRow(
            {
                "contract_no": contract,
                "supply_center": center,
                "revenue_month_rpd": month,
                "revenue_month_cpd": month,
                "legacy_amount": None,
                "monthly_new_order": None,
                "region": "R",
                "country": "Country",
                "customer_group": "G",
                "ata": date(2026, 1, 1),
            }
        )


if __name__ == "__main__":
    unittest.main()
