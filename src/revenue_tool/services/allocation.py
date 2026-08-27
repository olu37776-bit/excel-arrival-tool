from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from revenue_tool.domain.models import IssueLog
from revenue_tool.domain.revenue_models import (
    MANUAL_AMOUNT_VALUE,
    ContractAllocationSummary,
    ContractFinancialFact,
    RevenueAllocationCandidate,
    RevenueAllocationDecision,
)
from revenue_tool.services.normalization import ZERO_AMOUNT, normalize_lookup


class AllocationService:
    def allocate(
        self,
        contract_facts: list[ContractFinancialFact],
        candidates: list[RevenueAllocationCandidate]
        | tuple[RevenueAllocationCandidate, ...],
        issues: IssueLog,
    ) -> tuple[list[RevenueAllocationDecision], list[ContractAllocationSummary]]:
        candidates_by_contract: dict[
            str, list[RevenueAllocationCandidate]
        ] = defaultdict(list)
        for candidate in candidates:
            candidates_by_contract[candidate.contract_no].append(candidate)

        decisions: list[RevenueAllocationDecision] = []
        summaries: list[ContractAllocationSummary] = []
        for fact in contract_facts:
            contract_candidates = sorted(
                candidates_by_contract.get(fact.contract_no, []),
                key=lambda item: normalize_lookup(item.supply_center),
            )
            unique_auto = (
                fact.revenue_forecast != ZERO_AMOUNT
                and len(contract_candidates) == 1
                and contract_candidates[0].fulfillment_projection.revenue_segment
                not in {"需判断", "不要货"}
            )
            contract_decisions: list[RevenueAllocationDecision] = []
            for candidate in contract_candidates:
                manual = candidate.manual_allocation
                auto_amount = fact.revenue_forecast if unique_auto else None
                if manual.amount_state == MANUAL_AMOUNT_VALUE:
                    final_amount = manual.amount
                    source = "手工"
                elif auto_amount is not None:
                    final_amount = auto_amount
                    source = "自动"
                else:
                    final_amount = None
                    source = "未分配"
                previous_amount = (
                    candidate.previous_manual_allocation.amount
                    if candidate.previous_manual_allocation.amount_state
                    == MANUAL_AMOUNT_VALUE
                    else None
                )
                decision = RevenueAllocationDecision(
                    allocation_candidate_id=candidate.allocation_candidate_id,
                    contract_no=candidate.contract_no,
                    supply_center=candidate.supply_center,
                    previous_manual_amount=previous_amount,
                    auto_allocated_amount=auto_amount,
                    manual_amount_state=manual.amount_state,
                    manual_allocated_amount=manual.amount,
                    final_allocated_amount=final_amount,
                    allocation_source=source,
                    allocation_note=manual.note,
                    inherited_from_run_id=candidate.inherited_from_run_id,
                    projection_changed=candidate.projection_changed,
                    contract_forecast_changed=(
                        candidate.contract_forecast_changed
                    ),
                    review_required=candidate.review_required,
                    diagnostic_codes=candidate.diagnostic_codes,
                )
                decisions.append(decision)
                contract_decisions.append(decision)

            allocated = sum(
                (
                    item.final_allocated_amount
                    for item in contract_decisions
                    if item.final_allocated_amount is not None
                ),
                ZERO_AMOUNT,
            )
            unallocated = fact.revenue_forecast - allocated
            direction_invalid = _direction_invalid(
                fact.revenue_forecast, contract_decisions
            )
            over = _is_overallocated(fact.revenue_forecast, allocated)
            diagnostic_codes: list[str] = []
            if direction_invalid:
                diagnostic_codes.append("ALLOCATION_DIRECTION_INVALID")
                issues.add(
                    "ALLOCATION_DIRECTION_INVALID",
                    "分配金额方向与合同收入预测不一致，未自动修正",
                    severity="ERROR",
                    business_key=fact.contract_no,
                    field="final_allocated_amount",
                    raw_value=str(allocated),
                )
            if over:
                diagnostic_codes.append("ALLOCATION_EXCEEDS_FORECAST")
                issues.add(
                    "ALLOCATION_EXCEEDS_FORECAST",
                    "合同最终分配合计超过收入预测，未自动截断",
                    severity="ERROR",
                    business_key=fact.contract_no,
                    field="final_allocated_amount",
                    raw_value=(
                        f"forecast={fact.revenue_forecast}; allocated={allocated}"
                    ),
                )

            if not contract_candidates and fact.demand_state == "NO_DEMAND":
                status = "不要货"
            elif fact.revenue_forecast == ZERO_AMOUNT and allocated == ZERO_AMOUNT:
                status = "无需分配"
            elif direction_invalid:
                status = "需复核"
            elif over:
                status = "分配超额"
            elif any(item.review_required for item in contract_decisions):
                status = "需复核"
            elif allocated == fact.revenue_forecast:
                status = "分配完成"
            elif allocated == ZERO_AMOUNT:
                status = "未分配"
            else:
                status = "部分分配"

            if allocated + unallocated != fact.revenue_forecast:
                raise AssertionError("contract allocation conservation failed")
            summaries.append(
                ContractAllocationSummary(
                    contract_no=fact.contract_no,
                    revenue_forecast=fact.revenue_forecast,
                    candidate_count=len(contract_candidates),
                    allocated_amount=allocated,
                    unallocated_amount=unallocated,
                    allocation_status=status,
                    diagnostic_codes=tuple(diagnostic_codes),
                )
            )
        return decisions, summaries


def _direction_invalid(
    forecast: Decimal,
    decisions: list[RevenueAllocationDecision],
) -> bool:
    values = [
        item.final_allocated_amount
        for item in decisions
        if item.final_allocated_amount not in {None, ZERO_AMOUNT}
    ]
    if not values:
        return False
    if forecast == ZERO_AMOUNT:
        return True
    expected_positive = forecast > ZERO_AMOUNT
    return any((value > ZERO_AMOUNT) != expected_positive for value in values)


def _is_overallocated(forecast: Decimal, allocated: Decimal) -> bool:
    if forecast == ZERO_AMOUNT:
        return allocated != ZERO_AMOUNT
    if (
        (allocated > ZERO_AMOUNT) != (forecast > ZERO_AMOUNT)
        and allocated != ZERO_AMOUNT
    ):
        return False
    return abs(allocated) > abs(forecast)
