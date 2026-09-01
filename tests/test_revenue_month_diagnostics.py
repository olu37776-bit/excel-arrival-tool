from datetime import date
import unittest

from revenue_tool.domain.models import (
    BaseRow,
    CONTRACT_ONLY_NO_DEMAND,
    IssueLog,
)
from revenue_tool.services.revenue_month_diagnostics import (
    ISSUE_CODE,
    RevenueMonthDiagnostics,
)


class RevenueMonthDiagnosticsTest(unittest.TestCase):
    def test_rpd_present_and_cpd_blank_adds_one_traceable_warning(self) -> None:
        issues = self._analyze(
            self._row(
                rpd_month="2026-09",
                cpd_month=None,
                arrival_rpd=date(2026, 9, 20),
            )
        )

        self.assertEqual(1, len(issues.items))
        issue = issues.items[0]
        self.assertEqual(ISSUE_CODE, issue.code)
        self.assertEqual("WARNING", issue.severity)
        self.assertEqual("demand.xlsx", issue.workbook)
        self.assertEqual("要货明细", issue.sheet)
        self.assertEqual("C001 | SC-A", issue.business_key)
        self.assertEqual(
            "revenue_month_rpd+revenue_month_cpd", issue.field
        )
        self.assertIn("RPD=2026-09; CPD=空", issue.raw_value)
        self.assertIn("到货日期（按RPD）=2026-09-20", issue.raw_value)

    def test_cpd_present_and_rpd_blank_adds_one_warning(self) -> None:
        issues = self._analyze(
            self._row(rpd_month=None, cpd_month="2026-10")
        )

        self.assertEqual([ISSUE_CODE], [issue.code for issue in issues.items])

    def test_both_present_or_both_blank_adds_no_warning(self) -> None:
        for rpd_month, cpd_month in (
            ("2026-09", "2026-10"),
            (None, None),
            ("(空白)", "VALUE"),
        ):
            with self.subTest(rpd=rpd_month, cpd=cpd_month):
                issues = self._analyze(
                    self._row(
                        rpd_month=rpd_month,
                        cpd_month=cpd_month,
                    )
                )
                self.assertEqual([], issues.items)

    def test_contract_only_no_demand_is_excluded(self) -> None:
        row = self._row(rpd_month="2026-09", cpd_month=None)
        row.row_kind = CONTRACT_ONLY_NO_DEMAND

        self.assertEqual([], self._analyze(row).items)

    def test_root_cause_issue_coexists_and_result_warning_is_idempotent(
        self,
    ) -> None:
        row = self._row(rpd_month="2026-09", cpd_month=None)
        issues = IssueLog()
        issues.add(
            "TRANSIT_NOT_FOUND",
            "国家运输周期表无对应组合",
            business_key="C001 | SC-A",
        )
        analyzer = RevenueMonthDiagnostics()

        for _ in range(2):
            analyzer.analyze(
                [row, row],
                workbook="demand.xlsx",
                sheet="要货明细",
                issues=issues,
            )

        self.assertEqual(
            ["TRANSIT_NOT_FOUND", ISSUE_CODE],
            [issue.code for issue in issues.items],
        )

    def _analyze(self, row: BaseRow) -> IssueLog:
        issues = IssueLog()
        RevenueMonthDiagnostics().analyze(
            [row],
            workbook="demand.xlsx",
            sheet="要货明细",
            issues=issues,
        )
        return issues

    @staticmethod
    def _row(
        *,
        rpd_month: str | None,
        cpd_month: str | None,
        arrival_rpd: date | None = None,
        arrival_cpd: date | None = None,
    ) -> BaseRow:
        return BaseRow(
            {
                "contract_no": "C001",
                "supply_center": "SC-A",
                "revenue_month_rpd": rpd_month,
                "revenue_month_cpd": cpd_month,
                "arrival_date_rpd": arrival_rpd,
                "arrival_date_cpd": arrival_cpd,
            }
        )


if __name__ == "__main__":
    unittest.main()
