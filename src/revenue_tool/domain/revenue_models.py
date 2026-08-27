from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping


CANDIDATE_ID_VERSION = "1"
PROJECTION_FINGERPRINT_VERSION = "1"
MANUAL_AMOUNT_UNAVAILABLE = "UNAVAILABLE"
MANUAL_AMOUNT_BLANK = "BLANK"
MANUAL_AMOUNT_VALUE = "VALUE"
PREVIOUS_SOURCE_NATIVE = "NATIVE"
PREVIOUS_SOURCE_V08 = "V08_COMPAT"
PREVIOUS_SOURCE_EMPTY = "EMPTY"
PERSPECTIVE_RPD = "RPD"
PERSPECTIVE_CPD = "CPD"


@dataclass(frozen=True)
class ContractFinancialFact:
    """The single authoritative financial fact for one contract."""

    contract_no: str
    legacy_amount: Decimal
    monthly_new_order: Decimal
    revenue_forecast: Decimal
    bg: str | None
    region: str | None
    country: str | None
    carryover_type: str | None
    customer_group: str | None
    project_name: str | None
    demand_state: str

    def __post_init__(self) -> None:
        expected = self.legacy_amount + self.monthly_new_order
        if self.revenue_forecast != expected:
            raise ValueError(
                "revenue_forecast must equal legacy_amount + monthly_new_order"
            )


@dataclass(frozen=True)
class DemandRecord:
    """One deduplicated demand-detail evidence record for this run only."""

    demand_record_id: str
    contract_no: str
    supply_center: str | None
    demand_status: str | None
    incoterm: str | None
    stock_control_flag: str | None
    shipment_control_flag: str | None
    ata: date | None
    asd: date | None
    rpd: date | None
    cpd: date | None
    bg: str | None
    source_workbook: str
    source_sheet: str
    source_row_number: int
    invalid_fields: tuple[str, ...]


@dataclass(frozen=True)
class FulfillmentProjection:
    """Existing fulfillment rules projected at contract + supply-center grain."""

    contract_no: str
    supply_center: str | None
    row_kind: str
    multiple_supply_centers: str
    demand_record_count: int
    demand_status_summary: str | None
    source_row_summary: str | None
    demand_record_ids: tuple[str, ...]
    ata_values: tuple[date, ...]
    asd_values: tuple[date, ...]
    rpd_values: tuple[date, ...]
    cpd_values: tuple[date, ...]
    incoterm: str | None
    stock_unlocked: str | None
    split_shipment: str
    transit_days: int | None
    ata: date | None
    asd: date | None
    rpd: date | None
    multiple_demand: str
    latest_asd: date | None
    latest_rpd: date | None
    shipment_incomplete: str | None
    cpd: date | None
    split_supply: str
    arrival_date_rpd: date | None
    arrival_date_cpd: date | None
    revenue_month_rpd: str | None
    revenue_month_cpd: str | None
    revenue_segment: str
    issue_codes: tuple[str, ...]


@dataclass(frozen=True)
class RevenuePhase1Models:
    contract_facts: tuple[ContractFinancialFact, ...]
    demand_records: tuple[DemandRecord, ...]
    fulfillment_projections: tuple[FulfillmentProjection, ...]


@dataclass(frozen=True)
class ManualAllocationSnapshot:
    amount_state: str
    amount: Decimal | None = None
    note: str | None = None
    source_run_id: str | None = None

    def __post_init__(self) -> None:
        if self.amount_state not in {
            MANUAL_AMOUNT_UNAVAILABLE,
            MANUAL_AMOUNT_BLANK,
            MANUAL_AMOUNT_VALUE,
        }:
            raise ValueError("unsupported manual amount state")
        if self.amount_state == MANUAL_AMOUNT_VALUE:
            if not isinstance(self.amount, Decimal):
                raise ValueError("VALUE manual amount requires Decimal")
        elif self.amount is not None:
            raise ValueError("non-VALUE manual amount must be None")


@dataclass(frozen=True)
class RevenueAllocationCandidate:
    allocation_candidate_id: str
    candidate_id_version: str
    contract_no: str
    supply_center: str
    row_kind: str
    projection_fingerprint: str
    projection_fingerprint_version: str
    fulfillment_projection: FulfillmentProjection
    previous_manual_allocation: ManualAllocationSnapshot
    manual_allocation: ManualAllocationSnapshot
    inherited_from_run_id: str | None = None
    projection_changed: bool = False
    contract_forecast_changed: bool = False
    review_required: bool = False
    diagnostic_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PreviousRunMetadata:
    metadata_schema: str
    candidate_id_version: str | None
    projection_fingerprint_version: str | None
    run_id: str | None
    source_format: str
    rules_version: str | None = None


@dataclass(frozen=True)
class PreviousContractState:
    contract_no: str
    legacy_amount: Decimal
    monthly_new_order: Decimal
    revenue_forecast: Decimal
    bg: str | None
    region: str | None
    country: str | None
    carryover_type: str | None
    customer_group: str | None
    project_name: str | None
    demand_state: str


@dataclass(frozen=True)
class PreviousCandidateState:
    allocation_candidate_id: str
    candidate_id_version: str
    contract_no: str
    supply_center: str
    row_kind: str
    projection: FulfillmentProjection
    projection_fingerprint: str | None
    revenue_month_rpd: str | None
    revenue_month_cpd: str | None
    revenue_segment: str
    manual_allocation: ManualAllocationSnapshot


@dataclass(frozen=True)
class PreviousRunState:
    metadata: PreviousRunMetadata
    fulfillment_projections: tuple[FulfillmentProjection, ...]
    candidates_by_id: Mapping[str, PreviousCandidateState]
    contracts_by_no: Mapping[str, PreviousContractState]
    usable_for_projection_comparison: bool
    usable_for_allocation_inheritance: bool
    diagnostic_codes: tuple[str, ...] = ()

    @classmethod
    def empty(cls) -> "PreviousRunState":
        return cls(
            metadata=PreviousRunMetadata(
                metadata_schema="",
                candidate_id_version=None,
                projection_fingerprint_version=None,
                run_id=None,
                source_format=PREVIOUS_SOURCE_EMPTY,
            ),
            fulfillment_projections=(),
            candidates_by_id={},
            contracts_by_no={},
            usable_for_projection_comparison=False,
            usable_for_allocation_inheritance=False,
        )


@dataclass(frozen=True)
class OrphanedPreviousAllocation:
    diagnostic_code: str
    previous_run_id: str | None
    allocation_candidate_id: str
    candidate_id_version: str
    contract_no: str
    supply_center: str
    row_kind: str
    previous_manual_amount: Decimal
    previous_allocation_note: str | None
    previous_revenue_month_rpd: str | None
    previous_revenue_month_cpd: str | None
    previous_revenue_segment: str
    previous_projection_fingerprint: str | None


@dataclass(frozen=True)
class CandidateHistoryResult:
    candidates: tuple[RevenueAllocationCandidate, ...]
    orphaned_allocations: tuple[OrphanedPreviousAllocation, ...]
    diagnostic_codes: tuple[str, ...]


@dataclass(frozen=True)
class RevenueAllocationDecision:
    allocation_candidate_id: str
    contract_no: str
    supply_center: str
    previous_manual_amount: Decimal | None
    auto_allocated_amount: Decimal | None
    manual_amount_state: str
    manual_allocated_amount: Decimal | None
    final_allocated_amount: Decimal | None
    allocation_source: str
    allocation_note: str | None
    inherited_from_run_id: str | None
    projection_changed: bool
    contract_forecast_changed: bool
    review_required: bool
    diagnostic_codes: tuple[str, ...]


@dataclass(frozen=True)
class ContractAllocationSummary:
    contract_no: str
    revenue_forecast: Decimal
    candidate_count: int
    allocated_amount: Decimal
    unallocated_amount: Decimal
    allocation_status: str
    rpd_posted_amount: Decimal = Decimal("0.00")
    rpd_pending_amount: Decimal = Decimal("0.00")
    cpd_posted_amount: Decimal = Decimal("0.00")
    cpd_pending_amount: Decimal = Decimal("0.00")
    diagnostic_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MonthlyRevenuePosting:
    perspective: str
    allocation_candidate_id: str
    contract_no: str
    supply_center: str
    revenue_month: str | None
    revenue_segment: str
    final_allocated_amount: Decimal
    posted_amount: Decimal
    pending_amount: Decimal
    posting_status: str
    pending_reason: str | None
    bg: str | None
    region: str | None
    country: str | None
    carryover_type: str | None
    customer_group: str | None
    project_name: str | None


@dataclass(frozen=True)
class MonthlyRevenueSummaryRow:
    revenue_month: str
    bg: str | None
    region: str | None
    country: str | None
    carryover_type: str | None
    customer_group: str | None
    monthly_forecast: Decimal
    order_not_shipped: Decimal
    shipped_not_received: Decimal
    unrecorded_order_contract_count: int


@dataclass(frozen=True)
class PendingRevenueRow:
    contract_no: str
    allocation_candidate_id: str | None
    supply_center: str | None
    contract_revenue_forecast: Decimal
    allocated_amount: Decimal
    pending_amount: Decimal
    rpd_pending_amount: Decimal
    cpd_pending_amount: Decimal
    revenue_segment: str | None
    processing_status: str
    pending_reason: str
    suggested_action: str
    previous_manual_amount: Decimal | None = None
    previous_allocation_note: str | None = None


@dataclass(frozen=True)
class RevenueE2EModels:
    run_id: str
    contract_facts: tuple[ContractFinancialFact, ...]
    demand_records: tuple[DemandRecord, ...]
    fulfillment_projections: tuple[FulfillmentProjection, ...]
    allocation_candidates: tuple[RevenueAllocationCandidate, ...]
    allocation_decisions: tuple[RevenueAllocationDecision, ...]
    allocation_summaries: tuple[ContractAllocationSummary, ...]
    monthly_postings: tuple[MonthlyRevenuePosting, ...]
    rpd_monthly_summary: tuple[MonthlyRevenueSummaryRow, ...]
    cpd_monthly_summary: tuple[MonthlyRevenueSummaryRow, ...]
    pending_revenue: tuple[PendingRevenueRow, ...]
    orphaned_allocations: tuple[OrphanedPreviousAllocation, ...]
