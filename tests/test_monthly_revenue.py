from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import unittest

from revenue_tool.domain.models import HAS_DEMAND, NO_DEMAND, IssueLog
from revenue_tool.domain.revenue_models import (
    MANUAL_AMOUNT_VALUE,
    ContractFinancialFact,
    ManualAllocationSnapshot,
)
from revenue_tool.services.allocation import AllocationService
from revenue_tool.services.allocation_candidates import AllocationCandidateBuilder
from revenue_tool.services.monthly_revenue import MonthlyRevenueService
from tests.test_candidate_identity import _projection


class MonthlyRevenueTest(unittest.TestCase):
    def test_partial_amount_posts_independently_by_rpd_and_cpd(self) -> None:
        issues = IssueLog()
        projections = [
            replace(
                _projection(),
                supply_center="SC-A",
                revenue_segment="发未收",
                revenue_month_rpd="2026-02",
                revenue_month_cpd=None,
            ),
            replace(
                _projection(),
                supply_center="SC-B",
                revenue_segment="订未发",
                revenue_month_rpd="2026-03",
                revenue_month_cpd="2026-03",
            ),
        ]
        candidates = AllocationCandidateBuilder().build(projections, issues)
        candidates[0] = replace(
            candidates[0],
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("40.00")
            ),
        )
        facts = [_fact("C001", "100.00")]
        decisions, summaries = AllocationService().allocate(
            facts, candidates, issues
        )

        postings, rpd, cpd, pending, summaries = MonthlyRevenueService().build(
            facts, candidates, decisions, summaries, []
        )

        self.assertEqual(2, len(postings))
        rpd_posting = next(item for item in postings if item.perspective == "RPD")
        cpd_posting = next(item for item in postings if item.perspective == "CPD")
        self.assertEqual(Decimal("40.00"), rpd_posting.final_allocated_amount)
        self.assertEqual(Decimal("40.00"), cpd_posting.final_allocated_amount)
        self.assertEqual(Decimal("40.00"), rpd_posting.posted_amount)
        self.assertEqual(Decimal("40.00"), cpd_posting.pending_amount)
        self.assertEqual(Decimal("40.00"), rpd[0].monthly_forecast)
        self.assertEqual([], cpd)
        summary = summaries[0]
        self.assertEqual(
            summary.revenue_forecast,
            summary.rpd_posted_amount
            + summary.rpd_pending_amount
            + summary.unallocated_amount,
        )
        self.assertEqual(
            summary.revenue_forecast,
            summary.cpd_posted_amount
            + summary.cpd_pending_amount
            + summary.unallocated_amount,
        )
        self.assertTrue(
            any(row.rpd_pending_amount == Decimal("0.00") for row in pending)
        )
        self.assertTrue(
            any(row.cpd_pending_amount == Decimal("40.00") for row in pending)
        )

    def test_unrecorded_order_is_a_distinct_contract_count(self) -> None:
        issues = IssueLog()
        projection = replace(
            _projection(),
            contract_no="C002",
            revenue_segment="未录入订货",
            revenue_month_rpd="2026-05",
            revenue_month_cpd="2026-05",
        )
        candidates = AllocationCandidateBuilder().build([projection], issues)
        facts = [_fact("C002", "0.00")]
        decisions, summaries = AllocationService().allocate(
            facts, candidates, issues
        )

        _postings, rpd, cpd, _pending, _summaries = MonthlyRevenueService().build(
            facts, candidates, decisions, summaries, []
        )

        self.assertEqual(1, rpd[0].unrecorded_order_contract_count)
        self.assertEqual(Decimal("0.00"), rpd[0].monthly_forecast)
        self.assertEqual(1, cpd[0].unrecorded_order_contract_count)

    def test_no_demand_forecast_enters_pending_without_candidate(self) -> None:
        fact = replace(_fact("C003", "50.00"), demand_state=NO_DEMAND)
        decisions, summaries = AllocationService().allocate(
            [fact], [], IssueLog()
        )

        postings, _rpd, _cpd, pending, summaries = MonthlyRevenueService().build(
            [fact], [], decisions, summaries, []
        )

        self.assertEqual([], postings)
        self.assertEqual(Decimal("50.00"), summaries[0].unallocated_amount)
        self.assertEqual(1, len(pending))
        self.assertEqual(Decimal("50.00"), pending[0].pending_amount)
        self.assertIn("不要货", pending[0].pending_reason)

    def test_overallocation_never_enters_formal_monthly_summary(self) -> None:
        issues = IssueLog()
        candidates = AllocationCandidateBuilder().build(
            [
                replace(_projection(), supply_center="SC-A", revenue_segment="发未收"),
                replace(_projection(), supply_center="SC-B", revenue_segment="订未发"),
            ],
            issues,
        )
        candidates[0] = replace(
            candidates[0],
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("120.00")
            ),
        )
        facts = [_fact("C001", "100.00")]
        decisions, summaries = AllocationService().allocate(
            facts, candidates, issues
        )

        postings, rpd, cpd, _pending, _summaries = MonthlyRevenueService().build(
            facts, candidates, decisions, summaries, []
        )

        self.assertEqual([], rpd)
        self.assertEqual([], cpd)
        self.assertTrue(all(item.posted_amount == 0 for item in postings))
        self.assertTrue(all(item.posting_status == "待处理" for item in postings))


def _fact(contract_no: str, forecast: str) -> ContractFinancialFact:
    amount = Decimal(forecast)
    return ContractFinancialFact(
        contract_no=contract_no,
        legacy_amount=amount,
        monthly_new_order=Decimal("0.00"),
        revenue_forecast=amount,
        bg="BG",
        region="Region",
        country="Country",
        carryover_type="Delivery",
        customer_group="Customer",
        project_name="Project",
        demand_state=HAS_DEMAND,
    )


if __name__ == "__main__":
    unittest.main()
