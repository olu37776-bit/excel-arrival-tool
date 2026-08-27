from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any

from revenue_tool.domain.models import ComparisonRow, DEMAND_CENTER, IssueLog
from revenue_tool.domain.revenue_models import (
    MANUAL_AMOUNT_VALUE,
    ContractAllocationSummary,
    ContractFinancialFact,
    DemandRecord,
    FulfillmentProjection,
    MonthlyRevenuePosting,
    MonthlyRevenueSummaryRow,
    PendingRevenueRow,
    RevenueAllocationCandidate,
    RevenueAllocationDecision,
)
from revenue_tool.services.normalization import business_key_identity
from revenue_tool.services.previous_run_state import projection_to_record


class RevenueDatasetBuilder:
    """Map completed domain results to the configured workbook datasets."""

    def build(
        self,
        *,
        facts: list[ContractFinancialFact],
        records: list[DemandRecord],
        projections: list[FulfillmentProjection],
        candidates: list[RevenueAllocationCandidate],
        decisions: list[RevenueAllocationDecision],
        summaries: list[ContractAllocationSummary],
        postings: list[MonthlyRevenuePosting],
        rpd_summary: list[MonthlyRevenueSummaryRow],
        cpd_summary: list[MonthlyRevenueSummaryRow],
        pending: list[PendingRevenueRow],
        rpd_changes: list[ComparisonRow],
        cpd_changes: list[ComparisonRow],
        supply_pull: list[ComparisonRow],
        issues: IssueLog,
    ) -> dict[str, list[dict[str, Any]]]:
        fact_map = {item.contract_no: item for item in facts}
        summary_map = {item.contract_no: item for item in summaries}
        decision_map = {
            item.allocation_candidate_id: item for item in decisions
        }
        candidate_by_key = {
            business_key_identity(item.contract_no, item.supply_center): item
            for item in candidates
        }
        pending_by_candidate: dict[str, list[str]] = defaultdict(list)
        for row in pending:
            if row.allocation_candidate_id:
                pending_by_candidate[row.allocation_candidate_id].append(
                    row.pending_reason
                )

        center_counts: dict[str, int] = defaultdict(int)
        for projection in projections:
            if projection.row_kind == DEMAND_CENTER:
                center_counts[projection.contract_no] += 1

        contract_rows = []
        for fact in facts:
            summary = summary_map[fact.contract_no]
            contract_rows.append(
                {
                    **asdict(fact),
                    "fulfillment_center_count": center_counts[fact.contract_no],
                    **asdict(summary),
                }
            )

        allocation_rows = []
        for candidate in candidates:
            fact = fact_map[candidate.contract_no]
            projection = candidate.fulfillment_projection
            decision = decision_map[candidate.allocation_candidate_id]
            summary = summary_map[candidate.contract_no]
            manual_amount = (
                decision.manual_allocated_amount
                if decision.manual_amount_state == MANUAL_AMOUNT_VALUE
                else None
            )
            issue_codes = tuple(
                dict.fromkeys(
                    projection.issue_codes + decision.diagnostic_codes
                )
            )
            allocation_rows.append(
                {
                    "allocation_candidate_id": candidate.allocation_candidate_id,
                    "contract_no": candidate.contract_no,
                    "contract_revenue_forecast_reference": fact.revenue_forecast,
                    "legacy_amount": fact.legacy_amount,
                    "monthly_new_order": fact.monthly_new_order,
                    "previous_manual_amount": decision.previous_manual_amount,
                    "auto_allocated_amount": decision.auto_allocated_amount,
                    "manual_allocated_amount": manual_amount,
                    "final_allocated_amount": decision.final_allocated_amount,
                    "contract_allocated_amount": summary.allocated_amount,
                    "contract_unallocated_amount": summary.unallocated_amount,
                    "allocation_status": summary.allocation_status,
                    "allocation_source": decision.allocation_source,
                    "review_required": "Y" if decision.review_required else "N",
                    "allocation_note": decision.allocation_note,
                    "inherited_from_run_id": decision.inherited_from_run_id,
                    "bg": fact.bg,
                    "region": fact.region,
                    "country": fact.country,
                    "carryover_type": fact.carryover_type,
                    "customer_group": fact.customer_group,
                    "project_name": fact.project_name,
                    "supply_center": candidate.supply_center,
                    "demand_record_count": projection.demand_record_count,
                    "demand_status_summary": projection.demand_status_summary,
                    "source_row_summary": projection.source_row_summary,
                    "multiple_supply_centers": projection.multiple_supply_centers,
                    "stock_unlocked": projection.stock_unlocked,
                    "split_shipment": projection.split_shipment,
                    "multiple_demand": projection.multiple_demand,
                    "shipment_incomplete": projection.shipment_incomplete,
                    "split_supply": projection.split_supply,
                    "incoterm": projection.incoterm,
                    "transit_days": projection.transit_days,
                    "ata": projection.ata,
                    "asd": projection.asd,
                    "rpd": projection.rpd,
                    "latest_asd": projection.latest_asd,
                    "latest_rpd": projection.latest_rpd,
                    "cpd": projection.cpd,
                    "arrival_date_rpd": projection.arrival_date_rpd,
                    "arrival_date_cpd": projection.arrival_date_cpd,
                    "revenue_month_rpd": projection.revenue_month_rpd,
                    "revenue_month_cpd": projection.revenue_month_cpd,
                    "revenue_segment": projection.revenue_segment,
                    "projection_changed": (
                        "Y" if decision.projection_changed else "N"
                    ),
                    "contract_forecast_changed": (
                        "Y" if decision.contract_forecast_changed else "N"
                    ),
                    "issue_summary": " | ".join(issue_codes) or None,
                    "pending_reason": "；".join(
                        dict.fromkeys(
                            pending_by_candidate.get(
                                candidate.allocation_candidate_id, []
                            )
                        )
                    )
                    or None,
                }
            )

        record_rows = []
        for record in records:
            candidate = candidate_by_key.get(
                business_key_identity(record.contract_no, record.supply_center)
            )
            record_rows.append(
                {
                    **asdict(record),
                    "allocation_candidate_id": (
                        candidate.allocation_candidate_id if candidate else None
                    ),
                    "invalid_fields": " | ".join(record.invalid_fields) or None,
                }
            )

        projection_rows = []
        for projection in projections:
            candidate = candidate_by_key.get(
                business_key_identity(
                    projection.contract_no, projection.supply_center
                )
            )
            projection_rows.append(
                projection_to_record(
                    projection,
                    allocation_candidate_id=(
                        candidate.allocation_candidate_id if candidate else None
                    ),
                    candidate_id_version=(
                        candidate.candidate_id_version if candidate else None
                    ),
                    projection_fingerprint=(
                        candidate.projection_fingerprint if candidate else None
                    ),
                    projection_fingerprint_version=(
                        candidate.projection_fingerprint_version
                        if candidate
                        else None
                    ),
                )
            )

        return {
            "contract_forecast": contract_rows,
            "allocation": allocation_rows,
            "rpd_monthly_summary": [asdict(item) for item in rpd_summary],
            "cpd_monthly_summary": [asdict(item) for item in cpd_summary],
            "pending_revenue": [asdict(item) for item in pending],
            "monthly_posting_detail": [asdict(item) for item in postings],
            "demand_record_detail": record_rows,
            "rpd_changes": [item.values for item in rpd_changes],
            "cpd_changes": [item.values for item in cpd_changes],
            "supply_pull": [item.values for item in supply_pull],
            "issues": [item.as_dict() for item in issues.items],
            "fulfillment_projection": projection_rows,
        }
