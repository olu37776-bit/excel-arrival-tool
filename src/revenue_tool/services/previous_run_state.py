from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import json
from typing import Any

from revenue_tool.domain.models import (
    BaseRow,
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    HAS_DEMAND,
    NO_DEMAND,
    PreviousData,
)
from revenue_tool.domain.revenue_models import (
    FulfillmentProjection,
    PreviousContractState,
    PreviousRunState,
)
from revenue_tool.services.normalization import business_key_identity


PROJECTION_FIELDS = (
    "contract_no",
    "supply_center",
    "row_kind",
    "multiple_supply_centers",
    "demand_record_count",
    "demand_status_summary",
    "source_row_summary",
    "demand_record_ids",
    "ata_values",
    "asd_values",
    "rpd_values",
    "cpd_values",
    "incoterm",
    "stock_unlocked",
    "split_shipment",
    "transit_days",
    "ata",
    "asd",
    "rpd",
    "multiple_demand",
    "latest_asd",
    "latest_rpd",
    "shipment_incomplete",
    "cpd",
    "split_supply",
    "arrival_date_rpd",
    "arrival_date_cpd",
    "revenue_month_rpd",
    "revenue_month_cpd",
    "revenue_segment",
    "issue_codes",
)


def projection_to_record(
    projection: FulfillmentProjection,
    *,
    allocation_candidate_id: str | None,
    candidate_id_version: str | None,
    projection_fingerprint: str | None,
    projection_fingerprint_version: str | None,
) -> dict[str, Any]:
    result = {
        field: getattr(projection, field) for field in PROJECTION_FIELDS
    }
    for field in (
        "demand_record_ids",
        "ata_values",
        "asd_values",
        "rpd_values",
        "cpd_values",
        "issue_codes",
    ):
        values = result[field]
        result[field] = json.dumps(
            [
                value.isoformat() if isinstance(value, date) else value
                for value in values
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        )
    result.update(
        {
            "allocation_candidate_id": allocation_candidate_id,
            "candidate_id_version": candidate_id_version,
            "projection_fingerprint": projection_fingerprint,
            "projection_fingerprint_version": (
                projection_fingerprint_version
            ),
        }
    )
    return result


def projection_from_record(values: dict[str, Any]) -> FulfillmentProjection:
    return FulfillmentProjection(
        contract_no=str(values.get("contract_no") or ""),
        supply_center=_text_or_none(values.get("supply_center")),
        row_kind=str(values.get("row_kind") or DEMAND_CENTER),
        multiple_supply_centers=str(
            values.get("multiple_supply_centers") or "N"
        ),
        demand_record_count=int(values.get("demand_record_count") or 0),
        demand_status_summary=_text_or_none(
            values.get("demand_status_summary")
        ),
        source_row_summary=_text_or_none(values.get("source_row_summary")),
        demand_record_ids=tuple(_json_list(values.get("demand_record_ids"))),
        ata_values=_date_tuple(values.get("ata_values")),
        asd_values=_date_tuple(values.get("asd_values")),
        rpd_values=_date_tuple(values.get("rpd_values")),
        cpd_values=_date_tuple(values.get("cpd_values")),
        incoterm=_text_or_none(values.get("incoterm")),
        stock_unlocked=_text_or_none(values.get("stock_unlocked")),
        split_shipment=str(values.get("split_shipment") or "N"),
        transit_days=(
            int(values["transit_days"])
            if values.get("transit_days") is not None
            else None
        ),
        ata=_date_or_none(values.get("ata")),
        asd=_date_or_none(values.get("asd")),
        rpd=_date_or_none(values.get("rpd")),
        multiple_demand=str(values.get("multiple_demand") or "N"),
        latest_asd=_date_or_none(values.get("latest_asd")),
        latest_rpd=_date_or_none(values.get("latest_rpd")),
        shipment_incomplete=_text_or_none(
            values.get("shipment_incomplete")
        ),
        cpd=_date_or_none(values.get("cpd")),
        split_supply=str(values.get("split_supply") or "N"),
        arrival_date_rpd=_date_or_none(values.get("arrival_date_rpd")),
        arrival_date_cpd=_date_or_none(values.get("arrival_date_cpd")),
        revenue_month_rpd=_text_or_none(values.get("revenue_month_rpd")),
        revenue_month_cpd=_text_or_none(values.get("revenue_month_cpd")),
        revenue_segment=str(values.get("revenue_segment") or "需判断"),
        issue_codes=tuple(_json_list(values.get("issue_codes"))),
    )


def previous_state_to_previous_data(state: PreviousRunState) -> PreviousData:
    rows: dict[tuple[str, str], BaseRow] = {}
    for projection in state.fulfillment_projections:
        contract = state.contracts_by_no.get(projection.contract_no)
        if contract is None:
            continue
        values = {
            "contract_no": contract.contract_no,
            "legacy_amount": contract.legacy_amount,
            "monthly_new_order": contract.monthly_new_order,
            "bg": contract.bg,
            "region": contract.region,
            "country": contract.country,
            "carryover_type": contract.carryover_type,
            "customer_group": contract.customer_group,
            "project_name": contract.project_name,
            "incoterm": projection.incoterm,
            "supply_center": projection.supply_center,
            "multiple_supply_centers": projection.multiple_supply_centers,
            "stock_unlocked": projection.stock_unlocked,
            "split_shipment": projection.split_shipment,
            "transit_days": projection.transit_days,
            "ata": projection.ata,
            "asd": projection.asd,
            "rpd": projection.rpd,
            "multiple_demand": projection.multiple_demand,
            "latest_asd": projection.latest_asd,
            "latest_rpd": projection.latest_rpd,
            "shipment_incomplete": projection.shipment_incomplete,
            "cpd": projection.cpd,
            "split_supply": projection.split_supply,
            "arrival_date_rpd": projection.arrival_date_rpd,
            "arrival_date_cpd": projection.arrival_date_cpd,
            "revenue_month_rpd": projection.revenue_month_rpd,
            "revenue_month_cpd": projection.revenue_month_cpd,
            "revenue_segment": projection.revenue_segment,
        }
        key = business_key_identity(
            projection.contract_no, projection.supply_center
        )
        rows[key] = BaseRow(values, row_kind=projection.row_kind)
    return PreviousData(rows, usable=state.usable_for_projection_comparison)


def projection_from_v08_row(row: BaseRow) -> FulfillmentProjection:
    values = row.values
    return FulfillmentProjection(
        contract_no=str(values.get("contract_no") or ""),
        supply_center=_text_or_none(values.get("supply_center")),
        row_kind=row.row_kind,
        multiple_supply_centers=str(
            values.get("multiple_supply_centers") or "N"
        ),
        demand_record_count=(1 if row.row_kind == DEMAND_CENTER else 0),
        demand_status_summary=None,
        source_row_summary=None,
        demand_record_ids=(),
        ata_values=_single_date_tuple(values.get("ata")),
        asd_values=_single_date_tuple(values.get("asd")),
        rpd_values=_single_date_tuple(values.get("rpd")),
        cpd_values=_single_date_tuple(values.get("cpd")),
        incoterm=_text_or_none(values.get("incoterm")),
        stock_unlocked=_text_or_none(values.get("stock_unlocked")),
        split_shipment=str(values.get("split_shipment") or "N"),
        transit_days=values.get("transit_days"),
        ata=_date_or_none(values.get("ata")),
        asd=_date_or_none(values.get("asd")),
        rpd=_date_or_none(values.get("rpd")),
        multiple_demand=str(values.get("multiple_demand") or "N"),
        latest_asd=_date_or_none(values.get("latest_asd")),
        latest_rpd=_date_or_none(values.get("latest_rpd")),
        shipment_incomplete=_text_or_none(
            values.get("shipment_incomplete")
        ),
        cpd=_date_or_none(values.get("cpd")),
        split_supply=str(values.get("split_supply") or "N"),
        arrival_date_rpd=_date_or_none(values.get("arrival_date_rpd")),
        arrival_date_cpd=_date_or_none(values.get("arrival_date_cpd")),
        revenue_month_rpd=_text_or_none(values.get("revenue_month_rpd")),
        revenue_month_cpd=_text_or_none(values.get("revenue_month_cpd")),
        revenue_segment=str(values.get("revenue_segment") or "需判断"),
        issue_codes=(),
    )


def contract_from_v08_row(row: BaseRow) -> PreviousContractState:
    values = row.values
    legacy = _decimal_or_zero(values.get("legacy_amount"))
    monthly = _decimal_or_zero(values.get("monthly_new_order"))
    return PreviousContractState(
        contract_no=str(values.get("contract_no") or ""),
        legacy_amount=legacy,
        monthly_new_order=monthly,
        revenue_forecast=legacy + monthly,
        bg=_text_or_none(values.get("bg")),
        region=_text_or_none(values.get("region")),
        country=_text_or_none(values.get("country")),
        carryover_type=_text_or_none(values.get("carryover_type")),
        customer_group=_text_or_none(values.get("customer_group")),
        project_name=_text_or_none(values.get("project_name")),
        demand_state=(
            NO_DEMAND
            if row.row_kind == CONTRACT_ONLY_NO_DEMAND
            else HAS_DEMAND
        ),
    )


def _json_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    parsed = json.loads(str(value))
    if not isinstance(parsed, list):
        raise ValueError("expected JSON list")
    return parsed


def _date_tuple(value: Any) -> tuple[date, ...]:
    result = []
    for item in _json_list(value):
        parsed = _date_or_none(item)
        if parsed is not None:
            result.append(parsed)
    return tuple(result)


def _single_date_tuple(value: Any) -> tuple[date, ...]:
    parsed = _date_or_none(value)
    return (parsed,) if parsed else ()


def _date_or_none(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _decimal_or_zero(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"))
