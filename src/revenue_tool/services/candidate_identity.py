from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from typing import Any

from revenue_tool.domain.models import DEMAND_CENTER
from revenue_tool.domain.revenue_models import (
    CANDIDATE_ID_VERSION,
    PROJECTION_FINGERPRINT_VERSION,
    FulfillmentProjection,
)
from revenue_tool.services.normalization import normalize_lookup, normalize_text


def build_candidate_id(
    contract_no: str,
    supply_center: str,
    row_kind: str,
    *,
    version: str = CANDIDATE_ID_VERSION,
) -> str:
    normalized_kind = normalize_text(row_kind).upper()
    if normalized_kind != DEMAND_CENTER:
        raise ValueError("candidate ID v1 only supports DEMAND_CENTER")
    payload = [
        version,
        normalize_text(contract_no),
        normalize_lookup(supply_center),
        normalized_kind,
    ]
    canonical = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    )
    return f"RAC-v1-{sha256(canonical.encode('utf-8')).hexdigest()}"


def build_projection_fingerprint(
    projection: FulfillmentProjection,
    *,
    version: str = PROJECTION_FINGERPRINT_VERSION,
) -> str:
    payload = {
        "projection_fingerprint_version": version,
        "normalized_contract_no": normalize_text(projection.contract_no),
        "normalized_supply_center": normalize_lookup(projection.supply_center),
        "row_kind": normalize_text(projection.row_kind).upper(),
        "multiple_supply_centers": _text_or_none(
            projection.multiple_supply_centers
        ),
        "demand_record_count": projection.demand_record_count,
        "demand_status_set": _summary_set(projection.demand_status_summary),
        "incoterm": (
            normalize_text(projection.incoterm).upper()
            if projection.incoterm
            else None
        ),
        "stock_unlocked": _text_or_none(projection.stock_unlocked),
        "split_shipment": _text_or_none(projection.split_shipment),
        "transit_days": projection.transit_days,
        "ata_values": _date_list(projection.ata_values),
        "asd_values": _date_list(projection.asd_values),
        "rpd_values": _date_list(projection.rpd_values),
        "cpd_values": _date_list(projection.cpd_values),
        "ata": _date_value(projection.ata),
        "asd": _date_value(projection.asd),
        "rpd": _date_value(projection.rpd),
        "multiple_demand": _text_or_none(projection.multiple_demand),
        "latest_asd": _date_value(projection.latest_asd),
        "latest_rpd": _date_value(projection.latest_rpd),
        "shipment_incomplete": _text_or_none(
            projection.shipment_incomplete
        ),
        "cpd": _date_value(projection.cpd),
        "split_supply": _text_or_none(projection.split_supply),
        "arrival_date_rpd": _date_value(projection.arrival_date_rpd),
        "arrival_date_cpd": _date_value(projection.arrival_date_cpd),
        "revenue_month_rpd": _text_or_none(projection.revenue_month_rpd),
        "revenue_month_cpd": _text_or_none(projection.revenue_month_cpd),
        "revenue_segment": _text_or_none(projection.revenue_segment),
        "issue_codes": sorted(set(projection.issue_codes)),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"FP-v1-{sha256(canonical.encode('utf-8')).hexdigest()}"


def _summary_set(value: str | None) -> list[str]:
    if not value:
        return []
    return sorted(
        {
            normalized
            for item in value.split(" | ")
            if (normalized := normalize_lookup(item))
        }
    )


def _date_list(values: tuple[date, ...]) -> list[str]:
    return sorted({item.isoformat() for item in values})


def _date_value(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _text_or_none(value: Any) -> str | None:
    normalized = normalize_text(value)
    return normalized or None
