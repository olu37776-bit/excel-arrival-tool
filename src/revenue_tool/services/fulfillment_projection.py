from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Callable

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import (
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    IssueLog,
    SourceData,
)
from revenue_tool.domain.revenue_models import (
    ContractFinancialFact,
    DemandRecord,
    FulfillmentProjection,
)
from revenue_tool.services.calculation import (
    _arrival_date,
    _build_transit_index,
    _month,
    _resolve_transit_days,
    _revenue_segment,
    _shipment_incomplete,
    _transit_is_required,
)
from revenue_tool.services.normalization import nonblank, normalize_lookup, normalize_text
from revenue_tool.services.stock_unlock import aggregate_stock_unlock


class FulfillmentProjectionService:
    """Apply the existing fulfillment rules at contract + center grain."""

    def build(
        self,
        contract_facts: list[ContractFinancialFact],
        demand_records: list[DemandRecord],
        source: SourceData,
        config: ToolConfig,
        issues: IssueLog,
    ) -> list[FulfillmentProjection]:
        records_by_contract: dict[str, list[DemandRecord]] = defaultdict(list)
        for record in demand_records:
            records_by_contract[record.contract_no].append(record)

        transit_index = _build_transit_index(
            source.rows["transit"], source, issues
        )
        fixed_transit = {
            normalize_text(key).upper(): int(value)
            for key, value in config.rules["fixed_transit_days"].items()
        }
        result: list[FulfillmentProjection] = []
        for fact in contract_facts:
            contract_records = records_by_contract.get(fact.contract_no, [])
            if not contract_records:
                result.append(_no_demand_projection(fact, issues))
                continue
            center_groups = _group_by_supply_center(
                fact.contract_no,
                contract_records,
                issues,
            )
            multiple_centers = "Y" if len(center_groups) > 1 else "N"
            for center, group in center_groups:
                business_key = f"{fact.contract_no} | {center}"
                ata_values = _date_values(group, lambda item: item.ata)
                asd_values = _date_values(group, lambda item: item.asd)
                rpd_values = _date_values(group, lambda item: item.rpd)
                cpd_values = _date_values(group, lambda item: item.cpd)
                ata = max(ata_values) if ata_values else None
                asd = max(asd_values) if asd_values else None
                rpd = min(rpd_values) if rpd_values else None
                latest_asd = max(asd_values) if asd_values else None
                latest_rpd = max(rpd_values) if rpd_values else None
                cpd = max(cpd_values) if cpd_values else None
                shipment_incomplete = _shipment_incomplete(
                    latest_asd, latest_rpd
                )
                transit_required = _transit_is_required(
                    shipment_incomplete=shipment_incomplete,
                    ata=ata,
                    asd=asd,
                    rpd=latest_rpd,
                    cpd=cpd,
                )
                incoterm = _first_nonblank(
                    record.incoterm for record in group
                )
                transit_days = _resolve_transit_days(
                    incoterm=incoterm,
                    country=fact.country,
                    supply_center=center,
                    fixed_transit=fixed_transit,
                    transit_index=transit_index,
                    source=source,
                    issues=issues,
                    business_key=business_key,
                    required=transit_required,
                )
                arrival_rpd = _arrival_date(
                    mode="RPD",
                    shipment_incomplete=shipment_incomplete,
                    ata=ata,
                    asd=asd,
                    planned=latest_rpd,
                    transit_days=transit_days,
                    source=source,
                    issues=issues,
                    business_key=business_key,
                )
                arrival_cpd = _arrival_date(
                    mode="CPD",
                    shipment_incomplete=shipment_incomplete,
                    ata=ata,
                    asd=asd,
                    planned=cpd,
                    transit_days=transit_days,
                    source=source,
                    issues=issues,
                    business_key=business_key,
                )
                multiple_demand = "Y" if len(rpd_values) > 1 else "N"
                split_supply = "Y" if len(cpd_values) > 1 else "N"
                result.append(
                    FulfillmentProjection(
                        contract_no=fact.contract_no,
                        supply_center=center,
                        row_kind=DEMAND_CENTER,
                        multiple_supply_centers=multiple_centers,
                        demand_record_count=len(group),
                        demand_status_summary=_summary(
                            record.demand_status for record in group
                        ),
                        source_row_summary=" | ".join(
                            _source_reference(record) for record in group
                        ),
                        demand_record_ids=tuple(
                            record.demand_record_id for record in group
                        ),
                        ata_values=ata_values,
                        asd_values=asd_values,
                        rpd_values=rpd_values,
                        cpd_values=cpd_values,
                        incoterm=incoterm,
                        stock_unlocked=aggregate_stock_unlock(
                            record.stock_control_flag for record in group
                        ),
                        split_shipment="Y" if len(group) > 1 else "N",
                        transit_days=transit_days,
                        ata=ata,
                        asd=asd,
                        rpd=rpd,
                        multiple_demand=multiple_demand,
                        latest_asd=latest_asd,
                        latest_rpd=latest_rpd,
                        shipment_incomplete=shipment_incomplete,
                        cpd=cpd,
                        split_supply=split_supply,
                        arrival_date_rpd=arrival_rpd,
                        arrival_date_cpd=arrival_cpd,
                        revenue_month_rpd=_month(arrival_rpd),
                        revenue_month_cpd=_month(arrival_cpd),
                        revenue_segment=_revenue_segment(
                            DEMAND_CENTER,
                            multiple_demand,
                            ata,
                            asd,
                            rpd,
                            cpd,
                            fact.legacy_amount,
                            fact.monthly_new_order,
                        ),
                        issue_codes=_issue_codes(
                            issues,
                            fact.contract_no,
                            business_key,
                            group,
                        ),
                    )
                )
        return sorted(
            result,
            key=lambda item: (
                normalize_lookup(item.contract_no),
                normalize_lookup(item.supply_center),
            ),
        )


def _group_by_supply_center(
    contract_no: str,
    records: list[DemandRecord],
    issues: IssueLog,
) -> list[tuple[str, list[DemandRecord]]]:
    grouped: dict[str, tuple[str, list[DemandRecord]]] = {}
    for record in records:
        if not nonblank(record.supply_center):
            issues.add(
                "MISSING_SUPPLY_CENTER",
                "要货明细履行供应中心为空，该行不能生成业务粒度",
                workbook=record.source_workbook,
                sheet=record.source_sheet,
                row_number=record.source_row_number,
                business_key=contract_no,
                field="supply_center",
                raw_value=record.supply_center,
            )
            continue
        center = str(record.supply_center)
        identity = normalize_lookup(center)
        if identity not in grouped:
            grouped[identity] = (center, [])
        grouped[identity][1].append(record)
    return sorted(grouped.values(), key=lambda item: normalize_lookup(item[0]))


def _no_demand_projection(
    fact: ContractFinancialFact,
    issues: IssueLog,
) -> FulfillmentProjection:
    return FulfillmentProjection(
        contract_no=fact.contract_no,
        supply_center=None,
        row_kind=CONTRACT_ONLY_NO_DEMAND,
        multiple_supply_centers="N",
        demand_record_count=0,
        demand_status_summary=None,
        source_row_summary=None,
        demand_record_ids=(),
        ata_values=(),
        asd_values=(),
        rpd_values=(),
        cpd_values=(),
        incoterm=None,
        stock_unlocked=None,
        split_shipment="N",
        transit_days=None,
        ata=None,
        asd=None,
        rpd=None,
        multiple_demand="N",
        latest_asd=None,
        latest_rpd=None,
        shipment_incomplete=None,
        cpd=None,
        split_supply="N",
        arrival_date_rpd=None,
        arrival_date_cpd=None,
        revenue_month_rpd=None,
        revenue_month_cpd=None,
        revenue_segment="不要货",
        issue_codes=_issue_codes(issues, fact.contract_no),
    )


def _date_values(
    records: list[DemandRecord],
    getter: Callable[[DemandRecord], date | None],
) -> tuple[date, ...]:
    return tuple(sorted({value for record in records if (value := getter(record))}))


def _summary(values) -> str | None:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not nonblank(value):
            continue
        text = normalize_text(value)
        identity = normalize_lookup(text)
        if identity in seen:
            continue
        seen.add(identity)
        ordered.append(text)
    return " | ".join(ordered) if ordered else None


def _first_nonblank(values) -> str | None:
    for value in values:
        if nonblank(value):
            return normalize_text(value)
    return None


def _source_reference(record: DemandRecord) -> str:
    return (
        f"{record.source_workbook}/{record.source_sheet}!"
        f"{record.source_row_number}"
    )


def _issue_codes(
    issues: IssueLog,
    contract_no: str,
    business_key: str | None = None,
    records: list[DemandRecord] | None = None,
) -> tuple[str, ...]:
    keys = {contract_no}
    if business_key:
        keys.add(business_key)
    source_rows = {
        (
            record.source_workbook,
            record.source_sheet,
            record.source_row_number,
        )
        for record in records or []
    }
    return tuple(
        dict.fromkeys(
            issue.code
            for issue in issues.items
            if issue.business_key in keys
            or (issue.workbook, issue.sheet, issue.row_number) in source_rows
        )
    )
