from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import (
    BaseRow,
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    IssueLog,
    ParsedRow,
    PreviousData,
    SourceData,
)
from revenue_tool.services.normalization import (
    business_key_identity,
    canonical_country_identity,
    nonblank,
    normalize_country_identity,
    normalize_lookup,
    normalize_text,
    ZERO_AMOUNT,
)
from revenue_tool.services.stock_unlock import aggregate_stock_unlock
from revenue_tool.services.final_revenue import calculate_final_values


_DEEP_SUPPLY_CENTER = normalize_lookup("深供")


@dataclass(frozen=True)
class TransitLookupEntry:
    row: ParsedRow
    value: int | None
    status: str


class RevenueEngine:
    def calculate(
        self,
        source: SourceData,
        previous: PreviousData,
        config: ToolConfig,
        issues: IssueLog,
    ) -> list[BaseRow]:
        legacy_rows = _valid_contract_rows(source.rows["legacy"])
        monthly_rows = _valid_contract_rows(source.rows["monthly_order"])
        demand_rows = _valid_contract_rows(source.rows["demand_detail"])

        legacy_first = _first_contract_rows(legacy_rows)
        monthly_first = _first_contract_rows(monthly_rows)
        demand_first_by_contract = _first_by_contract(demand_rows)
        contracts = {
            row.values["contract_no"]
            for row in legacy_rows + monthly_rows + demand_rows
        }
        demand_by_contract: dict[str, list[ParsedRow]] = defaultdict(list)
        for row in demand_rows:
            demand_by_contract[row.values["contract_no"]].append(row)

        transit_index = _build_transit_index(
            source.rows["transit"], source, issues
        )
        fixed_transit = {
            normalize_text(key).upper(): int(value)
            for key, value in config.rules["fixed_transit_days"].items()
        }
        carryover_countries = {
            normalize_country_identity(value)
            for value in config.rules["carryover_countries"]
        }
        country_aliases = {
            normalize_country_identity(alias): normalize_country_identity(
                canonical
            )
            for alias, canonical in config.rules["country_aliases"].items()
        }
        result: list[BaseRow] = []
        for contract in sorted(contracts, key=normalize_lookup):
            demand_contract = demand_first_by_contract.get(contract)
            legacy = legacy_first.get(contract)
            monthly = monthly_first.get(contract)
            contract_values = _build_contract_values(
                contract=contract,
                legacy=legacy,
                monthly=monthly,
                demand_contract=demand_contract,
                carryover_countries=carryover_countries,
                country_aliases=country_aliases,
            )
            contract_demand = demand_by_contract.get(contract, [])
            if not contract_demand:
                identity_key = business_key_identity(contract, None)
                result.append(
                    _build_no_demand_row(
                        contract_values,
                        _manual_values(previous, identity_key),
                    )
                )
                continue
            center_rows = _group_by_supply_center(
                contract,
                contract_demand,
                source,
                issues,
            )
            if not center_rows:
                continue
            multiple_centers = "Y" if len(center_rows) > 1 else "N"
            deep_supply_found = any(
                normalize_lookup(center) == _DEEP_SUPPLY_CENTER
                for center, _group in center_rows
            )
            apply_deep_supply_display = (
                len(center_rows) > 1 and deep_supply_found
            )
            if len(center_rows) > 1 and not deep_supply_found:
                issues.add(
                    "MULTI_CENTER_DEEP_SUPPLY_NOT_FOUND",
                    (
                        "多中心合同未找到“深供”金额承载行，"
                        "为避免金额丢失，未执行展示归零"
                    ),
                    workbook=source.workbook_for("demand_detail").name,
                    sheet=source.sheet_names.get("demand_detail", ""),
                    business_key=contract,
                    field="supply_center",
                    raw_value=" | ".join(
                        center for center, _group in center_rows
                    ),
                )
            for center, group in center_rows:
                display_key = (contract, center)
                identity_key = business_key_identity(*display_key)
                business_key = _display_key(display_key)
                legacy_amount = contract_values["legacy_amount"]
                monthly_new_order = contract_values["monthly_new_order"]
                country = contract_values["country"]
                incoterm = _first_nonblank_value(group, "incoterm")

                ata_values = _valid_dates(group, "ata")
                asd_values = _valid_dates(group, "asd")
                rpd_values = _valid_dates(group, "rpd")
                cpd_values = _valid_dates(group, "cpd")
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

                transit_days = _resolve_transit_days(
                    incoterm=incoterm,
                    country=country,
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

                multiple_demand = (
                    "Y" if len(set(rpd_values)) > 1 else "N"
                )
                split_supply = "Y" if le…4173 tokens truncated…发"
    return "不要货"


def _fallback(*values: Any) -> Any:
    for value in values:
        if nonblank(value):
            return value
    return None


def _value(row: ParsedRow | None, field: str) -> Any:
    return row.values.get(field) if row is not None else None


def _amount_value(row: ParsedRow | None, field: str) -> Decimal:
    value = _value(row, field)
    return value if isinstance(value, Decimal) else ZERO_AMOUNT


def _first_nonblank_value(rows: list[ParsedRow], field: str) -> Any:
    for row in rows:
        value = row.values.get(field)
        if nonblank(value):
            return value
    return None


def _month(value: date | None) -> str | None:
    return value.strftime("%Y-%m") if value is not None else None


def _display_key(key: tuple[str, str]) -> str:
    return f"{key[0]} | {key[1]}"


def _display_value(value: Any) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _source_value(row: ParsedRow, value: Any) -> str:
    return (
        f"{row.workbook}/{row.sheet}!{row.row_number}="
        f"{_display_value(value)}"
    )
