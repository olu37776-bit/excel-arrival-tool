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
    nonblank,
    normalize_country_identity,
    normalize_lookup,
    normalize_text,
    ZERO_AMOUNT,
)
from revenue_tool.services.stock_unlock import aggregate_stock_unlock


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
                split_supply = "Y" if len(set(cpd_values)) > 1 else "N"
                revenue_segment = _revenue_segment(
                    DEMAND_CENTER,
                    multiple_demand,
                    ata,
                    asd,
                    rpd,
                    cpd,
                    legacy_amount,
                    monthly_new_order,
                )
                display_legacy_amount = legacy_amount
                display_monthly_new_order = monthly_new_order
                if (
                    apply_deep_supply_display
                    and normalize_lookup(center) != _DEEP_SUPPLY_CENTER
                ):
                    display_legacy_amount = ZERO_AMOUNT
                    display_monthly_new_order = ZERO_AMOUNT

                values: dict[str, Any] = {
                    **contract_values,
                    "legacy_amount": display_legacy_amount,
                    "monthly_new_order": display_monthly_new_order,
                    "incoterm": incoterm,
                    "supply_center": center,
                    "multiple_supply_centers": multiple_centers,
                    "stock_unlocked": aggregate_stock_unlock(
                        row.values.get("stock_control_flag")
                        for row in group
                    ),
                    "split_shipment": "Y" if len(group) > 1 else "N",
                    "transit_days": transit_days,
                    "ata": ata,
                    "asd": asd,
                    "rpd": rpd,
                    "multiple_demand": multiple_demand,
                    "latest_asd": latest_asd,
                    "latest_rpd": latest_rpd,
                    "shipment_incomplete": shipment_incomplete,
                    "cpd": cpd,
                    "split_supply": split_supply,
                    "arrival_date_rpd": arrival_rpd,
                    "arrival_date_cpd": arrival_cpd,
                    "revenue_month_rpd": _month(arrival_rpd),
                    "revenue_month_cpd": _month(arrival_cpd),
                    "revenue_segment": revenue_segment,
                    **_manual_values(previous, identity_key),
                }
                result.append(BaseRow(values))
        return sorted(
            result,
            key=lambda row: (
                normalize_lookup(row.values["contract_no"]),
                normalize_lookup(row.values["supply_center"]),
            ),
        )


def _build_contract_values(
    *,
    contract: str,
    legacy: ParsedRow | None,
    monthly: ParsedRow | None,
    demand_contract: ParsedRow | None,
    carryover_countries: set[str],
) -> dict[str, Any]:
    legacy_country = _value(legacy, "country")
    return {
        "contract_no": contract,
        "legacy_amount": _amount_value(legacy, "legacy_amount"),
        "monthly_new_order": _amount_value(
            monthly, "monthly_new_order"
        ),
        "bg": _fallback(
            _value(legacy, "bg"),
            _value(monthly, "bg"),
            _value(demand_contract, "bg"),
        ),
        "region": _fallback(
            _value(legacy, "region"),
            _value(demand_contract, "region"),
        ),
        "country": _fallback(
            legacy_country,
            _value(demand_contract, "country"),
        ),
        "carryover_type": (
            "交付类"
            if normalize_country_identity(legacy_country)
            in carryover_countries
            else None
        ),
        "customer_group": _fallback(
            _value(legacy, "customer_group"),
            _value(demand_contract, "customer_group"),
        ),
        "project_name": _fallback(
            _value(legacy, "project_name"),
            _value(demand_contract, "project_name"),
        ),
    }


def _manual_values(
    previous: PreviousData,
    identity_key: tuple[str, str],
) -> dict[str, Any]:
    previous_row = previous.rows.get(identity_key)
    return {
        field: (
            previous_row.values.get(field)
            if previous_row is not None
            else None
        )
        for field in (
            "revenue_forecast",
            "manual_adjust_flag",
            "manual_revenue_forecast_rpd",
            "manual_revenue_forecast_cpd",
            "manual_revenue_month",
            "adjustment_note",
        )
    }


def _build_no_demand_row(
    contract_values: dict[str, Any],
    manual_values: dict[str, Any],
) -> BaseRow:
    return BaseRow(
        {
            **contract_values,
            "incoterm": None,
            "supply_center": None,
            "multiple_supply_centers": "N",
            "stock_unlocked": None,
            "split_shipment": "N",
            "transit_days": None,
            "ata": None,
            "asd": None,
            "rpd": None,
            "multiple_demand": "N",
            "latest_asd": None,
            "latest_rpd": None,
            "shipment_incomplete": None,
            "cpd": None,
            "split_supply": "N",
            "arrival_date_rpd": None,
            "arrival_date_cpd": None,
            "revenue_month_rpd": None,
            "revenue_month_cpd": None,
            "revenue_segment": _revenue_segment(
                CONTRACT_ONLY_NO_DEMAND,
                "N",
                None,
                None,
                None,
                None,
                contract_values["legacy_amount"],
                contract_values["monthly_new_order"],
            ),
            **manual_values,
        },
        row_kind=CONTRACT_ONLY_NO_DEMAND,
    )


def _valid_contract_rows(rows: list[ParsedRow]) -> list[ParsedRow]:
    return [row for row in rows if nonblank(row.values.get("contract_no"))]


def _first_contract_rows(
    rows: list[ParsedRow],
) -> dict[str, ParsedRow]:
    grouped: dict[str, list[ParsedRow]] = defaultdict(list)
    for row in rows:
        grouped[str(row.values["contract_no"])].append(row)
    return {contract: values[0] for contract, values in grouped.items()}


def _first_by_contract(
    rows: list[ParsedRow],
) -> dict[str, ParsedRow]:
    result: dict[str, ParsedRow] = {}
    for row in rows:
        contract = row.values.get("contract_no")
        if contract and str(contract) not in result:
            result[str(contract)] = row
    return result


def _group_by_supply_center(
    contract: str,
    rows: list[ParsedRow],
    source: SourceData,
    issues: IssueLog,
) -> list[tuple[str, list[ParsedRow]]]:
    grouped: dict[str, tuple[str, list[ParsedRow]]] = {}
    for row in rows:
        center = row.values.get("supply_center")
        if not nonblank(center):
            issues.add(
                "MISSING_SUPPLY_CENTER",
                "要货明细履行供应中心为空，该行不能生成业务粒度",
                workbook=row.workbook,
                sheet=row.sheet,
                row_number=row.row_number,
                business_key=contract,
                field="supply_center",
                raw_value=row.raw_values.get("supply_center"),
            )
            continue
        identity = normalize_lookup(center)
        if identity not in grouped:
            grouped[identity] = (str(center), [])
        grouped[identity][1].append(row)
    return sorted(
        grouped.values(),
        key=lambda item: normalize_lookup(item[0]),
    )


def _distinct_nonblank_entries(
    rows: list[ParsedRow], field: str
) -> list[tuple[Any, ParsedRow]]:
    result: list[tuple[Any, ParsedRow]] = []
    identities: set[tuple[str, str]] = set()
    for row in rows:
        value = row.values.get(field)
        if not nonblank(value):
            continue
        identity = _value_identity(value, field)
        if identity in identities:
            continue
        identities.add(identity)
        result.append((value, row))
    return result


def _value_identity(value: Any, field: str) -> tuple[str, str]:
    if isinstance(value, date):
        return ("date", value.isoformat())
    if isinstance(value, Decimal):
        return ("number", format(value.normalize(), "f"))
    text = normalize_text(value)
    if field == "incoterm":
        text = text.casefold()
    return ("text", text)


def _build_transit_index(
    rows: list[ParsedRow],
    source: SourceData,
    issues: IssueLog,
) -> dict[tuple[str, str], TransitLookupEntry]:
    grouped: dict[tuple[str, str], list[ParsedRow]] = defaultdict(list)
    for row in rows:
        country = row.values.get("country")
        center = row.values.get("supply_center")
        if not nonblank(country) or not nonblank(center):
            issues.add(
                "INVALID_TRANSIT_KEY",
                "国家运输周期行缺少国家或供应中心，无法建立查找键",
                workbook=row.workbook,
                sheet=row.sheet,
                row_number=row.row_number,
                field="country+supply_center",
                raw_value=(
                    f"{row.raw_values.get('country')} | "
                    f"{row.raw_values.get('supply_center')}"
                ),
            )
            continue
        grouped[
            (normalize_country_identity(country), normalize_lookup(center))
        ].append(row)

    result: dict[tuple[str, str], TransitLookupEntry] = {}
    for key, group in grouped.items():
        entries = _distinct_nonblank_entries(group, "transit_days")
        if len(entries) > 1:
            issues.add(
                "CONFLICTING_TRANSIT_DAYS",
                "同一国家+供应中心存在不同运输周期；按原顺序保留第一条",
                workbook=group[0].workbook,
                sheet=group[0].sheet,
                row_number=group[0].row_number,
                business_key=f"{key[0]} | {key[1]}",
                field="transit_days",
                raw_value=" | ".join(
                    _source_value(row, value)
                    for value, row in entries
                ),
            )
        first = group[0]
        value = first.values.get("transit_days")
        if "transit_days" in first.invalid_fields:
            status = "invalid"
        elif value is None:
            status = "unavailable"
        else:
            status = "valid"
        result[key] = TransitLookupEntry(first, value, status)
    return result


def _resolve_transit_days(
    *,
    incoterm: Any,
    country: Any,
    supply_center: str,
    fixed_transit: dict[str, int],
    transit_index: dict[tuple[str, str], TransitLookupEntry],
    source: SourceData,
    issues: IssueLog,
    business_key: str,
    required: bool = True,
) -> int | None:
    term = normalize_text(incoterm).upper()
    if term in fixed_transit:
        return fixed_transit[term]
    if not nonblank(country):
        if not required:
            return None
        issues.add(
            "TRANSIT_COUNTRY_MISSING",
            "缺少国家，无法匹配国家运输周期表",
            workbook=source.workbook_for("demand_detail").name,
            sheet=source.sheet_names.get("demand_detail", ""),
            business_key=business_key,
            field="country",
            raw_value=f"country={country}; supply_center={supply_center}",
        )
        return None
    key = (
        normalize_country_identity(country),
        normalize_lookup(supply_center),
    )
    if key not in transit_index:
        if not required:
            return None
        issues.add(
            "TRANSIT_NOT_FOUND",
            f"国家运输周期表无对应组合：{country} + {supply_center}",
            workbook=source.workbook_for("transit").name,
            sheet=source.sheet_names.get("transit", ""),
            business_key=business_key,
            field="country+supply_center",
            raw_value=f"country={country}; supply_center={supply_center}",
        )
        return None
    entry = transit_index[key]
    raw_value = entry.row.raw_values.get("transit_days")
    if entry.status == "invalid":
        if not required:
            return None
        issues.add(
            "INVALID_TRANSIT_DAYS",
            "运输周期为非空值但无法解析为合法非负整数自然日",
            workbook=entry.row.workbook,
            sheet=entry.row.sheet,
            row_number=entry.row.row_number,
            business_key=business_key,
            field="transit_days",
            raw_value=(
                f"country={country}; supply_center={supply_center}; "
                f"transit_days={raw_value}"
            ),
        )
        return None
    if entry.status == "unavailable":
        if not required:
            return None
        issues.add(
            "TRANSIT_VALUE_UNAVAILABLE",
            "已找到国家+供应中心组合，但运输周期无可用值",
            workbook=entry.row.workbook,
            sheet=entry.row.sheet,
            row_number=entry.row.row_number,
            business_key=business_key,
            field="transit_days",
            raw_value=(
                f"country={country}; supply_center={supply_center}; "
                f"transit_days={raw_value}"
            ),
        )
        return None
    return entry.value


def _transit_is_required(
    *,
    shipment_incomplete: str | None,
    ata: date | None,
    asd: date | None,
    rpd: date | None,
    cpd: date | None,
) -> bool:
    if shipment_incomplete == "Y":
        return rpd is not None or cpd is not None
    return ata is None and asd is not None


def _arrival_date(
    *,
    mode: str,
    shipment_incomplete: str | None,
    ata: date | None,
    asd: date | None,
    planned: date | None,
    transit_days: int | None,
    source: SourceData,
    issues: IssueLog,
    business_key: str,
) -> date | None:
    if shipment_incomplete != "Y":
        if ata is not None:
            return ata
        basis = asd
    else:
        basis = planned
    if basis is None or transit_days is None:
        return None
    try:
        return basis + timedelta(days=transit_days)
    except OverflowError:
        issues.add(
            f"ARRIVAL_{mode}_OVERFLOW",
            f"到货日期（按{mode}）计算超出日期范围，结果留空",
            workbook=source.workbook_for("demand_detail").name,
            business_key=business_key,
            field=f"arrival_date_{mode.lower()}",
            raw_value=f"{basis.isoformat()} + {transit_days}",
        )
        return None


def _valid_dates(rows: list[ParsedRow], field: str) -> list[date]:
    return [
        row.values[field]
        for row in rows
        if isinstance(row.values.get(field), date)
    ]


def _shipment_incomplete(
    latest_asd: date | None,
    latest_rpd: date | None,
) -> str | None:
    if latest_rpd is None:
        return None
    if latest_asd is None:
        return "Y"
    return "Y" if latest_rpd > latest_asd else "N"


def _revenue_segment(
    row_kind: str,
    multiple_demand: str,
    ata: date | None,
    asd: date | None,
    rpd: date | None,
    cpd: date | None,
    legacy_amount: Decimal,
    monthly_new_order: Decimal,
) -> str:
    if row_kind == CONTRACT_ONLY_NO_DEMAND:
        return "不要货"
    if multiple_demand == "Y":
        return "需判断"
    if ata is not None or asd is not None:
        return "发未收"
    if rpd is not None or cpd is not None:
        if legacy_amount == ZERO_AMOUNT and monthly_new_order == ZERO_AMOUNT:
            return "未录入订货"
        return "订未发"
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
