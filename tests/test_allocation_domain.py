from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import unittest

from revenue_tool.domain.models import DEMAND_CENTER, HAS_DEMAND, IssueLog
from revenue_tool.domain.revenue_models import (
    MANUAL_AMOUNT_VALUE,
    ContractFinancialFact,
    ManualAllocationSnapshot,
)
from revenue_tool.services.allocation import AllocationService
from revenue_tool.services.allocation_candidates import AllocationCandidateBuilder
from tests.test_candidate_identity import _projection


class AllocationDomainTest(unittest.TestCase):
    def test_single_eligible_candidate_is_auto_allocated_in_full(self) -> None:
        issues = IssueLog()
        candidate = AllocationCandidateBuilder().build(
            [replace(_projection(), revenue_segment="发未收")], issues
        )[0]

        decisions, summaries = AllocationService().allocate(
            [_fact("100.00")], [candidate], issues
        )

        self.assertEqual(Decimal("100.00"), decisions[0].auto_allocated_amount)
        self.assertEqual(Decimal("100.00"), decisions[0].final_allocated_amount)
        self.assertEqual("自动", decisions[0].allocation_source)
        self.assertEqual("分配完成", summaries[0].allocation_status)
        self.assertEqual(Decimal("0.00"), summaries[0].unallocated_amount)

    def test_partial_allocation_preserves_blank_and_explicit_zero(self) -> None:
        issues = IssueLog()
        candidates = AllocationCandidateBuilder().build(
            [
                replace(_projection(), supply_center="SC-A", revenue_segment="发未收"),
                replace(_projection(), supply_center="SC-B", revenue_segment="订未发"),
            ],
            issues,
        )
        candidates = [
            replace(
                candidates[0],
                manual_allocation=ManualAllocationSnapshot(
                    MANUAL_AMOUNT_VALUE, Decimal("40.00"), "partial"
                ),
            ),
            replace(
                candidates[1],
                manual_allocation=ManualAllocationSnapshot(
                    MANUAL_AMOUNT_VALUE, Decimal("0.00"), "explicit zero"
                ),
            ),
        ]

        decisions, summaries = AllocationService().allocate(
            [_fact("100.00")], candidates, issues
        )

        self.assertEqual(
            [Decimal("40.00"), Decimal("0.00")],
            [item.final_allocated_amount for item in decisions],
        )
        self.assertEqual("手工", decisions[1].allocation_source)
        self.assertEqual(Decimal("40.00"), summaries[0].allocated_amount)
        self.assertEqual(Decimal("60.00"), summaries[0].unallocated_amount)
        self.assertEqual("部分分配", summaries[0].allocation_status)
        self.assertEqual(
            summaries[0].revenue_forecast,
            summaries[0].allocated_amount + summaries[0].unallocated_amount,
        )

    def test_negative_partial_allocation_conserves_exactly(self) -> None:
        issues = IssueLog()
        candidates = AllocationCandidateBuilder().build(
            [
                replace(_projection(), supply_center="SC-A", revenue_segment="发未收"),
                replace(_projection(), supply_center="SC-B", revenue_segment="发未收"),
            ],
            issues,
        )
        candidates[0] = replace(
            candidates[0],
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("-40.00")
            ),
        )

        _decisions, summaries = AllocationService().allocate(
            [_fact("-100.00")], candidates, issues
        )

        self.assertEqual(Decimal("-40.00"), summaries[0].allocated_amount)
        self.assertEqual(Decimal("-60.00"), summaries[0].unallocated_amount)
        self.assertEqual("部分分配", summaries[0].allocation_status)

    def test_overallocation_is_not_truncated_and_blocks_formal_status(self) -> None:
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

        decisions, summaries = AllocationService().allocate(
            [_fact("100.00")], candidates, issues
        )

        self.assertEqual(Decimal("120.00"), decisions[0].final_allocated_amount)
        self.assertEqual(Decimal("-20.00"), summaries[0].unallocated_amount)
        self.assertEqual("分配超额", summaries[0].allocation_status)
        self.assertIn(
            "ALLOCATION_EXCEEDS_FORECAST",
            {item.code for item in issues.items},
        )

    def test_mixed_direction_requires_review_without_guessing(self) -> None:
        issues = IssueLog()
        candidate = AllocationCandidateBuilder().build(
            [replace(_projection(), revenue_segment="发未收")], issues
        )[0]
        candidate = replace(
            candidate,
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("-10.00")
            ),
        )

        decisions, summaries = AllocationService().allocate(
            [_fact("100.00")], [candidate], issues
        )

        self.assertEqual(Decimal("-10.00"), decisions[0].final_allocated_amount)
        self.assertEqual("需复核", summaries[0].allocation_status)
        self.assertIn(
            "ALLOCATION_DIRECTION_INVALID",
            {item.code for item in issues.items},
        )


def _fact(forecast: str) -> ContractFinancialFact:
    amount = Decimal(forecast)
    return ContractFinancialFact(
        contract_no="C001",
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
