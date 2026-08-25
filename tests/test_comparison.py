from datetime import date
import unittest

from revenue_tool.domain.models import BaseRow, IssueLog, PreviousData
from revenue_tool.services.comparison import (
    build_supply_pull_rows,
    compare_revenue_months,
)
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

    def test_same_period_rpd_cpd_difference_builds_supply_pull_rows(self) -> None:
        rows = [
            self._row("C1", "SC1", "2026-01", "2026-02"),
            self._row("C2", "SC2", "2026-03", "2026-03"),
            self._row("C3", "SC3", None, "2026-04"),
        ]

        result = build_supply_pull_rows(rows, "demand.xlsx", IssueLog())

        self.assertEqual(1, len(result))
        self.assertEqual("C1", result[0].values["contract_no"])
        self.assertEqual("2026-01", result[0].values["revenue_month_rpd"])
        self.assertEqual("2026-02", result[0].values["revenue_month_cpd"])

    @staticmethod
    def _row(
        contract: str,
        center: str,
        month: str | None,
        cpd_month: str | None = None,
    ) -> BaseRow:
        return BaseRow(
            {
                "contract_no": contract,
                "supply_center": center,
                "revenue_month_rpd": month,
                "revenue_month_cpd": month if cpd_month is None else cpd_month,
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
