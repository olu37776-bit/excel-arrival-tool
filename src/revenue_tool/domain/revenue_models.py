from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


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
