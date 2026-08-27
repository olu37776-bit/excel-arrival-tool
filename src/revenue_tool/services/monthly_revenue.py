from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from decimal import Decimal

from revenue_tool.domain.revenue_models import (
    PERSPECTIVE_CPD,
    PERSPECTIVE_RPD,
    ContractAllocationSummary,
    ContractFinancialFact,
    MonthlyRevenuePosting,
    MonthlyRevenueSummaryRow,
    OrphanedPreviousAllocation,
    PendingRevenueRow,
    RevenueAllocationCandidate,
    RevenueAllocationDecision,
)
from revenue_tool.services.normalization import ZERO_AMOUNT, normalize_lookup


FORMAL_SEGMENTS = {"订未发", "发未收"}


class MonthlyRevenueService:
    def build(
        self,
        contract_facts: list[ContractFinancialFact],
        candidates: list[RevenueAllocationCandidate]
        | tuple[RevenueAllocationCandidate, ...],
        decisions: list[RevenueAllocationDecision],
        summaries: list[ContractAllocationSummary],
        orphaned: list[OrphanedPreviousAllocation]
        | tuple[OrphanedPreviousAllocation, ...],
    ) -> tuple[
        list[MonthlyRevenuePosting],
        list[MonthlyRevenueSummaryRow],
        list[MonthlyRevenueSummaryRow],
        list[PendingRevenueRow],
        list[ContractAllocationSummary],
    ]:
        facts = {item.contract_no: item for item in contract_facts}
        candidate_map = {
            item.allocation_candidate_id: item for item in candidates
        }
        summary_map = {item.contract_no: item for item in summaries}
        postings: list[MonthlyRevenuePosting] = []

        for decision in decisions:
            if decision.final_allocated_amount is None:
                continue
            candidate = candidate_map[decision.allocation_candidate_id]
            projection = candidate.fulfillment_projection
            contract_summary = summary_map[decision.contract_no]
            fact = facts[decision.contract_no]
            for perspective, month in (
                (PERSPECTIVE_RPD, projection.revenue_month_rpd),
                (PERSPECTIVE_CPD, projection.revenue_month_cpd),
            ):
                reason = _pending_reason(
                    contract_summary,
                    candidate,
                    projection.revenue_segment,
                    month,
                )
                if reason is None:
                    posted = decision.final_allocated_amount
                    pending = ZERO_AMOUNT
                    status = "已归月"
                else:
                    posted = ZERO_AMOUNT
                    pending = decision.final_allocated_amount
                    status = "待处理"
                postings.append(
                    MonthlyRevenuePosting(
                        perspective=perspective,
                        allocation_candidate_id=decision.allocation_candidate_id,
                        contract_no=decision.contract_no,
                        supply_center=decision.supply_center,
                        revenue_month=month,
                        revenue_segment=projection.revenue_segment,
                        final_allocated_amount=decision.final_allocated_amount,
                        posted_amount=posted,
                        pending_amount=pending,
                        posting_status=status,
                        pending_reason=reason,
                        bg=fact.bg,
                        region=fact.region,
                        country=fact.country,
                        carryover_type=fact.carryover_type,
                        customer_group=fact.customer_group,
                        project_name=fact.project_name,
                    )
                )

        updated_summaries: list[ContractAllocationSummary] = []
        postings_by_contract: dict[str, list[MonthlyRevenuePosting]] = defaultdict(list)
        for posting in postings:
            postings_by_contract[posting.contract_no].append(posting)
        for summary in summaries:
            contract_postings = postings_by_contract.get(summary.contract_no, [])
            rpd_posted = _sum_posting(contract_postings, PERSPECTIVE_RPD, "posted")
            rpd_pending = _sum_posting(contract_postings, PERSPECTIVE_RPD, "pending")
            cpd_posted = _sum_posting(contract_postings, PERSPECTIVE_CPD, "posted")
            cpd_pending = _sum_posting(contract_postings, PERSPECTIVE_CPD, "pending")
            if (
                rpd_posted + rpd_pending + summary.unallocated_amount
                != summary.revenue_forecast
            ):
                raise AssertionError("RPD contract conservation failed")
            if (
                cpd_posted + cpd_pending + summary.unallocated_amount
                != summary.revenue_forecast
            ):
                raise AssertionError("CPD contract conservation failed")
            updated_summaries.append(
                replace(
                    summary,
                    rpd_posted_amount=rpd_posted,
                    rpd_pending_amount=rpd_pending,
                    cpd_posted_amount=cpd_posted,
                    cpd_pending_amount=cpd_pending,
                )
            )

        pending_rows = _pending_rows(
            facts,
            candidate_map,
            {item.contract_no: item for item in updated_summaries},
            decisions,
            postings,
            orphaned,
        )
        rpd_summary = _summarize(
            PERSPECTIVE_RPD, postings, candidates, facts
        )
        cpd_summary = _summarize(
            PERSPECTIVE_CPD, postings, candidates, facts
        )
        return (
            postings,
            rpd_summary,
            cpd_summary,
            pending_rows,
            updated_summaries,
        )


def _pending_reason(
    summary: ContractAllocationSummary,
    candidate: RevenueAllocationCandidate,
    segment: str,
    month: str | None,
) -> str | None:
    if summary.allocation_status == "分配超额":
        return "分配超额"
    if summary.allocation_status == "需复核" or candidate.review_required:
        return "履行投影或合同收入预测变化，需复核"
    if segment not in FORMAL_SEGMENTS:
        return f"收入分段为{segment}，不可正式归月"
    if not month:
        return "收入年月为空"
    return None


def _sum_posting(
    postings: list[MonthlyRevenuePosting], perspective: str, field: str
) -> Decimal:
    return sum(
        (
            item.posted_amount if field == "posted" else item.pending_amount
            for item in postings
            if item.perspective == perspective
        ),
        ZERO_AMOUNT,
    )


def _pending_rows(
    facts: dict[str, ContractFinancialFact],
    candidates: dict[str, RevenueAllocationCandidate],
    summaries: dict[str, ContractAllocationSummary],
    decisions: list[RevenueAllocationDecision],
    postings: list[MonthlyRevenuePosting],
    orphaned: list[OrphanedPreviousAllocation]
    | tuple[OrphanedPreviousAllocation, ...],
) -> list[PendingRevenueRow]:
    result: list[PendingRevenueRow] = []
    postings_by_candidate: dict[str, list[MonthlyRevenuePosting]] = defaultdict(list)
    for posting in postings:
        postings_by_candidate[posting.allocation_candidate_id].append(posting)
    decisions_by_contract: dict[
        str, list[RevenueAllocationDecision]
    ] = defaultdict(list)
    for decision in decisions:
        decisions_by_contract[decision.contract_no].append(decision)

    for contract_no, summary in summaries.items():
        fact = facts[contract_no]
        if (
            summary.unallocated_amount != ZERO_AMOUNT
            or not decisions_by_contract.get(contract_no)
        ):
            if fact.demand_state == "NO_DEMAND":
                reason = "不要货，无履行和收入年月依据"
                action = "补充要货依据后重新运行"
            elif summary.allocation_status == "分配超额":
                reason = "分配超额形成合同未分配差额"
                action = "修正手工分配金额"
            else:
                reason = (
                    "未分配" if summary.allocated_amount == ZERO_AMOUNT else "部分分配"
                )
                action = "在收入分配Sheet填写或调整手工分配金额"
            result.append(
                PendingRevenueRow(
                    contract_no=contract_no,
                    allocation_candidate_id=None,
                    supply_center=None,
                    contract_revenue_forecast=summary.revenue_forecast,
                    allocated_amount=summary.allocated_amount,
                    pending_amount=summary.unallocated_amount,
                    rpd_pending_amount=ZERO_AMOUNT,
                    cpd_pending_amount=ZERO_AMOUNT,
                    revenue_segment=(
                        "不要货" if fact.demand_state == "NO_DEMAND" else None
                    ),
                    processing_status=summary.allocation_status,
                    pending_reason=reason,
                    suggested_action=action,
                )
            )

    decision_map = {item.allocation_candidate_id: item for item in decisions}
    for candidate_id, candidate_postings in postings_by_candidate.items():
        rpd_pending = _sum_posting(candidate_postings, PERSPECTIVE_RPD, "pending")
        cpd_pending = _sum_posting(candidate_postings, PERSPECTIVE_CPD, "pending")
        if rpd_pending == ZERO_AMOUNT and cpd_pending == ZERO_AMOUNT:
            continue
        decision = decision_map[candidate_id]
        candidate = candidates[candidate_id]
        reasons = "；".join(
            dict.fromkeys(
                item.pending_reason
                for item in candidate_postings
                if item.pending_reason
            )
        )
        final_amount = (
            decision.final_allocated_amount
            if decision.final_allocated_amount is not None
            else ZERO_AMOUNT
        )
        result.append(
            PendingRevenueRow(
                contract_no=decision.contract_no,
                allocation_candidate_id=candidate_id,
                supply_center=decision.supply_center,
                contract_revenue_forecast=summaries[
                    decision.contract_no
                ].revenue_forecast,
                allocated_amount=final_amount,
                pending_amount=final_amount,
                rpd_pending_amount=rpd_pending,
                cpd_pending_amount=cpd_pending,
                revenue_segment=(
                    candidate.fulfillment_projection.revenue_segment
                ),
                processing_status="待处理",
                pending_reason=reasons,
                suggested_action="复核履行依据、月份或分配金额后重新运行",
                previous_manual_amount=decision.previous_manual_amount,
                previous_allocation_note=decision.allocation_note,
            )
        )

    for item in orphaned:
        fact = facts.get(item.contract_no)
        result.append(
            PendingRevenueRow(
                contract_no=item.contract_no,
                allocation_candidate_id=item.allocation_candidate_id,
                supply_center=item.supply_center,
                contract_revenue_forecast=(
                    fact.revenue_forecast if fact else ZERO_AMOUNT
                ),
                allocated_amount=ZERO_AMOUNT,
                pending_amount=item.previous_manual_amount,
                rpd_pending_amount=item.previous_manual_amount,
                cpd_pending_amount=item.previous_manual_amount,
                revenue_segment=item.previous_revenue_segment,
                processing_status="上期候选消失",
                pending_reason="ORPHANED_PREVIOUS_ALLOCATION",
                suggested_action="确认历史金额应转移、冲销或取消",
                previous_manual_amount=item.previous_manual_amount,
                previous_allocation_note=item.previous_allocation_note,
            )
        )
    return sorted(
        result,
        key=lambda item: (
            normalize_lookup(item.contract_no),
            normalize_lookup(item.supply_center),
            item.pending_reason,
        ),
    )


def _summarize(
    perspective: str,
    postings: list[MonthlyRevenuePosting],
    candidates: list[RevenueAllocationCandidate]
    | tuple[RevenueAllocationCandidate, ...],
    facts: dict[str, ContractFinancialFact],
) -> list[MonthlyRevenueSummaryRow]:
    amounts: dict[tuple, list[Decimal]] = defaultdict(
        lambda: [ZERO_AMOUNT, ZERO_AMOUNT]
    )
    unrecorded: dict[tuple, set[str]] = defaultdict(set)
    for posting in postings:
        if (
            posting.perspective != perspective
            or posting.posting_status != "已归月"
            or not posting.revenue_month
            or posting.revenue_segment not in FORMAL_SEGMENTS
        ):
            continue
        key = _summary_key(
            posting.revenue_month,
            posting.bg,
            posting.region,
            posting.country,
            posting.carryover_type,
            posting.customer_group,
        )
        index = 0 if posting.revenue_segment == "订未发" else 1
        amounts[key][index] += posting.posted_amount

    for candidate in candidates:
        projection = candidate.fulfillment_projection
        if projection.revenue_segment != "未录入订货":
            continue
        month = (
            projection.revenue_month_rpd
            if perspective == PERSPECTIVE_RPD
            else projection.revenue_month_cpd
        )
        if not month:
            continue
        fact = facts[candidate.contract_no]
        key = _summary_key(
            month,
            fact.bg,
            fact.region,
            fact.country,
            fact.carryover_type,
            fact.customer_group,
        )
        unrecorded[key].add(candidate.contract_no)

    rows: list[MonthlyRevenueSummaryRow] = []
    for key in sorted(set(amounts) | set(unrecorded)):
        order_not_shipped, shipped_not_received = amounts[key]
        monthly_forecast = order_not_shipped + shipped_not_received
        if monthly_forecast != order_not_shipped + shipped_not_received:
            raise AssertionError("monthly summary conservation failed")
        rows.append(
            MonthlyRevenueSummaryRow(
                revenue_month=key[0],
                bg=key[1],
                region=key[2],
                country=key[3],
                carryover_type=key[4],
                customer_group=key[5],
                monthly_forecast=monthly_forecast,
                order_not_shipped=order_not_shipped,
                shipped_not_received=shipped_not_received,
                unrecorded_order_contract_count=len(unrecorded[key]),
            )
        )
    return rows


def _summary_key(
    month: str,
    bg: str | None,
    region: str | None,
    country: str | None,
    carryover_type: str | None,
    customer_group: str | None,
) -> tuple:
    return (
        month,
        bg,
        region,
        country,
        carryover_type,
        customer_group,
    )
