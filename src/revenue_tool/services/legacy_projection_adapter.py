from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from revenue_tool.domain.models import BaseRow
from revenue_tool.domain.revenue_models import (
    ContractFinancialFact,
    FulfillmentProjection,
)
from revenue_tool.services.contract_finance import contract_fact_to_legacy_values
from revenue_tool.services.normalization import business_key_identity, normalize_lookup


GOLDEN_FIELDS = (
    "contract_no",
    "legacy_amount",
    "monthly_new_order",
    "bg",
    "region",
    "country",
    "carryover_type",
    "customer_group",
    "project_name",
    "incoterm",
    "supply_center",
    "multiple_supply_centers",
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
    "row_kind",
)


@dataclass(frozen=True)
class GoldenDifference:
    business_key: tuple[str, str]
    field: str
    legacy_value: Any
    phase1_value: Any


class LegacyProjectionAdapter:
    """Map Phase 1 facts and projections into the v0.8 comparable view."""

    def to_base_rows(
        self,
        contract_facts: list[ContractFinancialFact]
        | tuple[ContractFinancialFact, ...],
        projections: list[FulfillmentProjection]
        | tuple[FulfillmentProjection, ...],
    ) -> list[BaseRow]:
        facts = {fact.contract_no: fact for fact in contract_facts}
        result: list[BaseRow] = []
        for projection in projections:
            fact = facts[projection.contract_no]
            values = {
                **contract_fact_to_legacy_values(fact),
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
                "manual_adjust_flag": None,
                "manual_revenue_month": None,
                "adjustment_note": None,
            }
            result.append(BaseRow(values, row_kind=projection.row_kind))
        return sorted(
            result,
            key=lambda row: (
                normalize_lookup(row.values["contract_no"]),
                normalize_lookup(row.values["supply_center"]),
            ),
        )


def compare_golden_rows(
    legacy_rows: list[BaseRow],
    phase1_rows: list[BaseRow],
) -> list[GoldenDifference]:
    legacy = {_key(row): row for row in legacy_rows}
    phase1 = {_key(row): row for row in phase1_rows}
    differences: list[GoldenDifference] = []
    for key in sorted(set(legacy) | set(phase1)):
        old = legacy.get(key)
        new = phase1.get(key)
        if old is None or new is None:
            differences.append(
                GoldenDifference(key, "__row__", old, new)
            )
            continue
        for field in GOLDEN_FIELDS:
            old_value = old.row_kind if field == "row_kind" else old.values.get(field)
            new_value = new.row_kind if field == "row_kind" else new.values.get(field)
            if old_value != new_value:
                differences.append(
                    GoldenDifference(key, field, old_value, new_value)
                )
    return differences


def _key(row: BaseRow) -> tuple[str, str]:
    return business_key_identity(
        row.values.get("contract_no"),
        row.values.get("supply_center"),
    )
