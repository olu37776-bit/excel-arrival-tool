from __future__ import annotations

from dataclasses import replace

from revenue_tool.domain.models import IssueLog
from revenue_tool.domain.revenue_models import (
    CANDIDATE_ID_VERSION,
    MANUAL_AMOUNT_VALUE,
    PREVIOUS_SOURCE_EMPTY,
    CandidateHistoryResult,
    ContractFinancialFact,
    OrphanedPreviousAllocation,
    PreviousRunState,
    RevenueAllocationCandidate,
)


class CandidateHistoryService:
    def apply(
        self,
        candidates: list[RevenueAllocationCandidate],
        contract_facts: list[ContractFinancialFact],
        previous: PreviousRunState,
        issues: IssueLog,
    ) -> CandidateHistoryResult:
        current_ids = {item.allocation_candidate_id for item in candidates}
        facts = {item.contract_no: item for item in contract_facts}
        result: list[RevenueAllocationCandidate] = []
        diagnostics: list[str] = []

        for candidate in candidates:
            codes: list[str] = list(candidate.diagnostic_codes)
            previous_candidate = previous.candidates_by_id.get(
                candidate.allocation_candidate_id
            )
            previous_contract = previous.contracts_by_no.get(
                candidate.contract_no
            )
            projection_changed = False
            forecast_changed = False
            review_required = False
            inherited = candidate.manual_allocation
            previous_manual = candidate.previous_manual_allocation
            inherited_run_id = None

            version_compatible = (
                previous.metadata.candidate_id_version
                in {None, CANDIDATE_ID_VERSION}
            )
            if previous_candidate is not None and not version_compatible:
                codes.append("CANDIDATE_ID_VERSION_MISMATCH")
                review_required = True
            elif previous_candidate is not None:
                previous_manual = previous_candidate.manual_allocation
                if previous.usable_for_allocation_inheritance:
                    inherited = replace(
                        previous_candidate.manual_allocation,
                        source_run_id=previous.metadata.run_id,
                    )
                    inherited_run_id = previous.metadata.run_id
                if previous_candidate.projection_fingerprint is not None:
                    projection_changed = (
                        previous_candidate.projection_fingerprint
                        != candidate.projection_fingerprint
                    )
                    if projection_changed:
                        codes.append("PROJECTION_CHANGED")
                        review_required = True
            elif previous.metadata.source_format != PREVIOUS_SOURCE_EMPTY:
                codes.append("CANDIDATE_ADDED")
                review_required = True

            fact = facts[candidate.contract_no]
            if previous_contract is not None:
                forecast_changed = (
                    previous_contract.revenue_forecast
                    != fact.revenue_forecast
                )
                if forecast_changed:
                    codes.append("CONTRACT_REVENUE_FORECAST_CHANGED")
                    review_required = True

            unique_codes = tuple(dict.fromkeys(codes))
            diagnostics.extend(unique_codes)
            result.append(
                replace(
                    candidate,
                    previous_manual_allocation=previous_manual,
                    manual_allocation=inherited,
                    inherited_from_run_id=inherited_run_id,
                    projection_changed=projection_changed,
                    contract_forecast_changed=forecast_changed,
                    review_required=review_required,
                    diagnostic_codes=unique_codes,
                )
            )

        orphaned: list[OrphanedPreviousAllocation] = []
        for candidate_id, previous_candidate in sorted(
            previous.candidates_by_id.items()
        ):
            if candidate_id in current_ids:
                continue
            diagnostics.append("CANDIDATE_REMOVED")
            issues.add(
                "CANDIDATE_REMOVED",
                "上期分配候选本期已消失",
                business_key=(
                    f"{previous_candidate.contract_no} | "
                    f"{previous_candidate.supply_center}"
                ),
                field="allocation_candidate_id",
                raw_value=candidate_id,
            )
            manual = previous_candidate.manual_allocation
            if manual.amount_state != MANUAL_AMOUNT_VALUE:
                continue
            assert manual.amount is not None
            orphan = OrphanedPreviousAllocation(
                diagnostic_code="ORPHANED_PREVIOUS_ALLOCATION",
                previous_run_id=previous.metadata.run_id,
                allocation_candidate_id=candidate_id,
                candidate_id_version=previous_candidate.candidate_id_version,
                contract_no=previous_candidate.contract_no,
                supply_center=previous_candidate.supply_center,
                row_kind=previous_candidate.row_kind,
                previous_manual_amount=manual.amount,
                previous_allocation_note=manual.note,
                previous_revenue_month_rpd=(
                    previous_candidate.revenue_month_rpd
                ),
                previous_revenue_month_cpd=(
                    previous_candidate.revenue_month_cpd
                ),
                previous_revenue_segment=previous_candidate.revenue_segment,
                previous_projection_fingerprint=(
                    previous_candidate.projection_fingerprint
                ),
            )
            orphaned.append(orphan)
            diagnostics.append("ORPHANED_PREVIOUS_ALLOCATION")
            issues.add(
                "ORPHANED_PREVIOUS_ALLOCATION",
                "上期候选已消失，历史手工金额和备注已转入待处理",
                severity="WARNING",
                business_key=(
                    f"{previous_candidate.contract_no} | "
                    f"{previous_candidate.supply_center}"
                ),
                field="manual_allocated_amount",
                raw_value=str(manual.amount),
            )

        return CandidateHistoryResult(
            candidates=tuple(result),
            orphaned_allocations=tuple(orphaned),
            diagnostic_codes=tuple(dict.fromkeys(diagnostics)),
        )
