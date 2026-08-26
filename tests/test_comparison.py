from datetime import date
from decimal import Decimal
import unittest

from revenue_tool.domain.models import (
    BaseRow,
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    IssueLog,
    PreviousData,
)
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

    def test_demand_to_no_demand_emits_each_previous_center_even_when_blank(self) -> None:
        previous = PreviousData(
            {
                business_key_identity("C1", "SC-A"): self._row(
                    "C1", "SC-A", None
                ),
                business_key_identity("C1", "SC-B"): self._row(
                    "C1", "SC-B", "2026-02"
                ),
            }
        )
        current = [self._placeholder("C1", legacy=Decimal("99.00"))]

        result = compare_revenue_months(
            current, previous, "rpd", "current.xlsx", IssueLog()
        )

        self.assertEqual(
            ["SC-A", "SC-B"],
            [r.values["supply_center"] for r in result],
        )
        self.assertTrue(
            all(r.values["direction"] == "变为不要货" for r in result)
        )
        self.assertIsNone(result[0].values["previous_month"])
        self.assertIsNone(result[0].values["current_month"])
        self.assertEqual(Decimal("99.00"), result[0].values["legacy_amount"])

    def test_no_demand_to_demand_emits_each_current_center_even_when_blank(self) -> None:
        previous = PreviousData(
            {
                business_key_identity("C1", None): self._placeholder("C1")
            }
        )
        current = [
            self._row("C1", "SC-A", None),
            self._row("C1", "SC-B", "2026-03"),
        ]

        result = compare_revenue_months(
            current, previous, "rpd", "current.xlsx", IssueLog()
        )

        self.assertEqual(
            ["SC-A", "SC-B"],
            [r.values["supply_center"] for r in result],
        )
        self.assertTrue(
            all(r.values["direction"] == "恢复要货" for r in result)
        )
        self.assertIsNone(result[0].values["previous_month"])
        self.assertIsNone(result[0].values["current_month"])

    def test_two_no_demand_periods_do_not_emit_changes_or_supply_pull(self) -> None:
        placeholder = self._placeholder("C1")
        previous = PreviousData(
            {business_key_identity("C1", None): placeholder}
        )

        self.assertEqual(
            [],
            compare_revenue_months(
                [placeholder], previous, "rpd", "current.xlsx", IssueLog()
            ),
        )
        self.assertEqual(
            [], build_supply_pull_rows([placeholder], "current.xlsx", IssueLog())
        )

    def test_conflicting_contract_state_reports_once_across_both_modes(self) -> None:
        rows = [self._row("C1", "SC-A", "2026-01"), self._placeholder("C1")]
        issues = IssueLog()

        rpd = compare_revenue_months(
            rows, PreviousData({}), "rpd", "current.xlsx", issues
        )
        cpd = compare_revenue_months(
            rows, PreviousData({}), "cpd", "current.xlsx", issues
        )

        self.assertEqual([], rpd)
        self.assertEqual([], cpd)
        matching = [
            issue
            for issue in issues.items
            if issue.code == "CONTRACT_DEMAND_STATE_CONFLICT"
        ]
        self.assertEqual(1, len(matching))

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
                "legacy_amount": Decimal("0.00"),
                "monthly_new_order": Decimal("0.00"),
                "region": "R",
                "country": "Country",
                "customer_group": "G",
                "ata": date(2026, 1, 1),
            },
            row_kind=DEMAND_CENTER,
        )

    @staticmethod
    def _placeholder(
        contract: str, *, legacy: Decimal = Decimal("0.00")
    ) -> BaseRow:
        return BaseRow(
            {
                "contract_no": contract,
                "supply_center": None,
                "revenue_month_rpd": None,
                "revenue_month_cpd": None,
                "revenue_segment": "不要货",
                "legacy_amount": legacy,
                "monthly_new_order": Decimal("0.00"),
                "region": "R-current",
                "country": None,
                "customer_group": "G-current",
            },
            row_kind=CONTRACT_ONLY_NO_DEMAND,
        )


if __name__ == "__main__":
    unittest.main()
