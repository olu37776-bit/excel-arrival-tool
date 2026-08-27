from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import unittest

from revenue_tool.domain.models import DEMAND_CENTER, IssueLog
from revenue_tool.domain.revenue_models import (
    CANDIDATE_ID_VERSION,
    MANUAL_AMOUNT_VALUE,
    PREVIOUS_SOURCE_NATIVE,
    PROJECTION_FINGERPRINT_VERSION,
    ManualAllocationSnapshot,
    PreviousCandidateState,
    PreviousContractState,
    PreviousRunMetadata,
    PreviousRunState,
)
from revenue_tool.services.allocation_candidates import AllocationCandidateBuilder
from revenue_tool.services.candidate_history import CandidateHistoryService
from revenue_tool.services.candidate_identity import build_projection_fingerprint
from tests.test_allocation_domain import _fact
from tests.test_candidate_identity import _projection


class CandidateHistoryTest(unittest.TestCase):
    def test_exact_zero_inherits_and_changes_require_review(self) -> None:
        issues = IssueLog()
        current = AllocationCandidateBuilder().build([_projection()], issues)[0]
        previous_projection = replace(
            _projection(), revenue_month_rpd="2026-01"
        )
        previous_candidate = PreviousCandidateState(
            allocation_candidate_id=current.allocation_candidate_id,
            candidate_id_version=CANDIDATE_ID_VERSION,
            contract_no="C001",
            supply_center="SC-A",
            row_kind=DEMAND_CENTER,
            projection=previous_projection,
            projection_fingerprint=build_projection_fingerprint(
                previous_projection
            ),
            revenue_month_rpd=previous_projection.revenue_month_rpd,
            revenue_month_cpd=previous_projection.revenue_month_cpd,
            revenue_segment=previous_projection.revenue_segment,
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("0.00"), "keep zero"
            ),
        )
        fact = _fact("100.00")
        previous = _previous_state(
            [previous_candidate], forecast=Decimal("90.00")
        )

        result = CandidateHistoryService().apply(
            [current], [fact], previous, issues
        )

        inherited = result.candidates[0]
        self.assertEqual(MANUAL_AMOUNT_VALUE, inherited.manual_allocation.amount_state)
        self.assertEqual(Decimal("0.00"), inherited.manual_allocation.amount)
        self.assertEqual("keep zero", inherited.manual_allocation.note)
        self.assertEqual("run-previous", inherited.inherited_from_run_id)
        self.assertTrue(inherited.projection_changed)
        self.assertTrue(inherited.contract_forecast_changed)
        self.assertTrue(inherited.review_required)
        self.assertIn("PROJECTION_CHANGED", inherited.diagnostic_codes)
        self.assertIn(
            "CONTRACT_REVENUE_FORECAST_CHANGED", inherited.diagnostic_codes
        )

    def test_removed_explicit_zero_becomes_orphan(self) -> None:
        issues = IssueLog()
        current = AllocationCandidateBuilder().build([_projection()], issues)[0]
        removed_projection = replace(_projection(), supply_center="SC-Z")
        removed = AllocationCandidateBuilder().build(
            [removed_projection], issues
        )[0]
        previous_removed = PreviousCandidateState(
            allocation_candidate_id=removed.allocation_candidate_id,
            candidate_id_version=CANDIDATE_ID_VERSION,
            contract_no="C001",
            supply_center="SC-Z",
            row_kind=DEMAND_CENTER,
            projection=removed_projection,
            projection_fingerprint=removed.projection_fingerprint,
            revenue_month_rpd=removed_projection.revenue_month_rpd,
            revenue_month_cpd=removed_projection.revenue_month_cpd,
            revenue_segment=removed_projection.revenue_segment,
            manual_allocation=ManualAllocationSnapshot(
                MANUAL_AMOUNT_VALUE, Decimal("0.00"), "explicit zero"
            ),
        )
        previous = _previous_state([previous_removed])

        result = CandidateHistoryService().apply(
            [current], [_fact("100.00")], previous, issues
        )

        self.assertIn("CANDIDATE_ADDED", result.candidates[0].diagnostic_codes)
        self.assertEqual(1, len(result.orphaned_allocations))
        self.assertEqual(
            Decimal("0.00"),
            result.orphaned_allocations[0].previous_manual_amount,
        )
        self.assertIn(
            "ORPHANED_PREVIOUS_ALLOCATION",
            {item.code for item in issues.items},
        )


def _previous_state(
    candidates: list[PreviousCandidateState],
    *,
    forecast: Decimal = Decimal("100.00"),
) -> PreviousRunState:
    contract = PreviousContractState(
        contract_no="C001",
        legacy_amount=forecast,
        monthly_new_order=Decimal("0.00"),
        revenue_forecast=forecast,
        bg="BG",
        region="Region",
        country="Country",
        carryover_type="Delivery",
        customer_group="Customer",
        project_name="Project",
        demand_state="HAS_DEMAND",
    )
    return PreviousRunState(
        metadata=PreviousRunMetadata(
            metadata_schema="4",
            candidate_id_version=CANDIDATE_ID_VERSION,
            projection_fingerprint_version=PROJECTION_FINGERPRINT_VERSION,
            run_id="run-previous",
            source_format=PREVIOUS_SOURCE_NATIVE,
        ),
        fulfillment_projections=tuple(
            item.projection for item in candidates
        ),
        candidates_by_id={
            item.allocation_candidate_id: item for item in candidates
        },
        contracts_by_no={"C001": contract},
        usable_for_projection_comparison=True,
        usable_for_allocation_inheritance=True,
    )


if __name__ == "__main__":
    unittest.main()
