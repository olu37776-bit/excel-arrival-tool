from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Iterable

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import (
    BaseRow,
    IssueLog,
    ParsedRow,
    PreviousData,
    SourceData,
)
from revenue_tool.services.normalization import (
    business_key_identity,
    nonblank,
    normalize_lookup,
    normalize_text,
)


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

        legacy_first = _first_contract_rows(
            legacy_rows, source, issues
        )
        monthly_first = _first_contract_rows(
            monthly_rows, source, issues
        )
        demand_first_by_contract = _first_by_contract(demand_rows)
        _log_contract_conflicts(
            demand_rows,
            ("region", "customer_group", "project_name", "bg"),
            source,
            issues,
        )
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
            normalize_lookup(value)
            for value in config.rules["carryover_countries"]
        }
        delimiter = str(config.rules["stock_flag_delimiter"])

        result: list[BaseRow] = []
        for contract in sorted(contracts, key=normalize_lookup):
            contract_demand = demand_by_contract.get(contract, [])
            center_rows = _group_by_supply_center(
                contract,
                contract_demand,
                source,
                issues,
            )
            if not center_rows:
                issues.add(
                    "CONTRACT_WITHOUT_SUPPLY_CENTER",
                    "合同进入全集，但要货明细中没有可用履行供应中心；不生成正常业务行",
                    workbook=source.workbook_for("demand_detail").name,
                    business_key=contract,
                    field="supply_center",
                )
                continue
            multiple_centers = "Y" if len(center_rows) > 1 else "N"
            for center, group in center_rows:
                display_key = (contract, center)
                identity_key = business_key_identity(*display_key)
                business_key = _display_key(display_key)
                _log_group_conflicts(
                    group,
                    ("incoterm",),
                    source,
                    issues,
                    business_key,
                )
                demand_contract = demand_first_by_contract.get(contract)
                legacy = legacy_first.get(contract)
                monthly = monthly_first.get(contract)

                region = _fallback(
                    _value(legacy, "region"),
                    _value(demand_contract, "region"),
                )
                country = _fallback(
                    _value(legacy, "country"),
                    _value(demand_contract, "country"),
                )
                customer_group = _fallback(
                    _value(legacy, "customer_group"),
                    _value(demand_contract, "customer_group"),
                )
                project_name = _fallback(
                    _value(legacy, "project_name"),
                    _value(demand_contract, "project_name"),
                )
                bg = _fallback(
                    _value(legacy, "bg"),
                    _value(monthly, "bg"),
                    _value(demand_contract, "bg"),
                )
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
                    latest_asd,
                    latest_rpd,
                    source,
                    issues,
                    business_key,
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
                )
                arrival_rpd = _arrival_date(
                    mode="RPD",
                    ata=ata,
                    asd=asd,
                    planned=rpd,
                    transit_days=transit_days,
                    source=source,
                    issues=issues,
                    business_key=business_key,
                )
                arrival_cpd = _arrival_date(
                    mode="CPD",
                    ata=ata,
                    asd=asd,
                    planned=cpd,
                    transit_days=transit_days,
                    source=source,
                    issues=issues,
                    business_key=business_key,
                )

                stock_values = [
                    str(row.values["stock_control_flag"])
                    for row in group
                    if nonblank(row.values.get("stock_control_flag"))
                ]
                invalid_date_present = any(
                    bool(
                        {"ata", "asd", "rpd", "cpd"}
                        & set(row.invalid_fields)
                    )
                    for row in group
                )
                multiple_demand = (
                    "Y" if len(set(rpd_values)) > 1 else "N"
                )
                split_supply = "Y" if len(set(cpd_values)) > 1 else "N"
                revenue_segment = _revenue_segment(
                    multiple_demand,
                    ata,
                    asd,
                    rpd,
                    cpd,
                    invalid_date_present,
                )

                previous_row = previous.rows.get(identity_key)
                manual_values = {
                    field: (
                        previous_row.values.get(field)
                        if previous_row is not None
                        else None
                    )
                    for field in (
                        "manual_adjust_flag",
                        "manual_revenue_month",
                        "adjustment_note",
                    )
                }
                legacy_country = _value(legacy, "country")
                values: dict[str, Any] = {
                    "contract_no": contract,
                    "legacy_amount": _value(legacy, "legacy_amount"),
                    "monthly_new_order": _value(
                        monthly, "monthly_new_order"
                    ),
                    "bg": bg,
                    "region": region,
                    "country": country,
                    "carryover_type": (
                        "交付类"
                        if normalize_lookup(legacy_country)
                        in carryover_countries
                        else None
                    ),
                    "customer_group": customer_group,
                    "project_name": project_name,
                    "incoterm": incoterm,
                    "supply_center": center,
                    "multiple_supply_centers": multiple_centers,
                    "stock_unlocked": (
                        delimiter.join(stock_values)
                        if stock_values
                        else None
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
                    **manual_values,
                }
                result.append(BaseRow(values))
        return sorted(
            result,
            key=lambda row: (
                normalize_lookup(row.values["contract_no"]),
                normalize_lookup(row.values["supply_center"]),
            ),
        )


def _valid_contract_rows(rows: list[ParsedRow]) -> list[ParsedRow]:
    return [row for row in rows if nonblank(row.values.get("contract_no"))]


def _first_contract_rows(
    rows: list[ParsedRow],
    source: SourceData,
    issues: IssueLog,
) -> dict[str, ParsedRow]:
    grouped: dict[str, list[ParsedRow]] = defaultdict(list)
    for row in rows:
        grouped[str(row.values["contract_no"])].append(row)
    if not rows:
        return {}
    conflict_fields = tuple(
        field
        for field in rows[0].values
        if field != "contract_no"
    )
    _log_contract_conflicts(
        rows, conflict_fields, source, issues
    )
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


def _log_contract_conflicts(
    rows: list[ParsedRow],
    fields: Iterable[str],
    source: SourceData,
    issues: IssueLog,
) -> None:
    grouped: dict[str, list[ParsedRow]] = defaultdict(list)
    for row in rows:
        contract = row.values.get("contract_no")
        if contract:
            grouped[str(contract)].append(row)
    for contract, group in grouped.items():
        for field in fields:
            entries = _distinct_nonblank_entries(group, field)
            if len(entries) > 1:
                issues.add(
                    "CONFLICTING_CONTRACT_VALUE",
                    "同合同存在多个不同非空值；按源表顺序保留第一条",
                    workbook=group[0].workbook,
                    sheet=group[0].sheet,
                    row_number=group[0].row_number,
                    business_key=contract,
                    field=field,
                    raw_value=" | ".join(
                        _source_value(row, value)
                        for value, row in entries
                    ),
                )


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


def _log_group_conflicts(
    rows: list[ParsedRow],
    fields: Iterable[str],
    source: SourceData,
    issues: IssueLog,
    business_key: str,
) -> None:
    for field in fields:
        entries = _distinct_nonblank_entries(rows, field)
        if len(entries) > 1:
            issues.add(
                "CONFLICTING_GROUP_VALUE",
                "同合同+履行供应中心存在多个不同非空文本值；当前按原顺序保留第一条",
                workbook=rows[0].workbook,
                sheet=rows[0].sheet,
                row_number=rows[0].row_number,
                business_key=business_key,
                field=field,
                raw_value=" | ".join(
                    _source_value(row, value)
                    for value, row in entries
                ),
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
) -> dict[tuple[str, str], int | None]:
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
            (normalize_lookup(country), normalize_lookup(center))
        ].append(row)

    result: dict[tuple[str, str], int | None] = {}
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
        result[key] = group[0].values.get("transit_days")
    return result


def _resolve_transit_days(
    *,
    incoterm: Any,
    country: Any,
    supply_center: str,
    fixed_transit: dict[str, int],
    transit_index: dict[tuple[str, str], int | None],
    source: SourceData,
    issues: IssueLog,
    business_key: str,
) -> int | None:
    term = normalize_text(incoterm).upper()
    if term in fixed_transit:
        return fixed_transit[term]
    if not nonblank(country):
        issues.add(
            "TRANSIT_COUNTRY_MISSING",
            "非 FCA/FOB/EXW 行缺少国家，无法匹配运输周期",
            workbook=source.workbook_for("demand_detail").name,
            business_key=business_key,
            field="country",
        )
        return None
    key = (normalize_lookup(country), normalize_lookup(supply_center))
    if key not in transit_index:
        issues.add(
            "TRANSIT_NOT_FOUND",
            "国家+履行供应中心在国家运输周期表中未找到",
            workbook=source.workbook_for("demand_detail").name,
            business_key=business_key,
            field="country+supply_center",
            raw_value=f"{country} | {supply_center}",
        )
        return None
    value = transit_index[key]
    if value is None:
        issues.add(
            "TRANSIT_VALUE_UNAVAILABLE",
            "运输周期键已找到，但第一条周期值非法或为空",
            workbook=source.workbook_for("transit").name,
            business_key=business_key,
            field="transit_days",
            raw_value=f"{country} | {supply_center}",
        )
    return value


def _arrival_date(
    *,
    mode: str,
    ata: date | None,
    asd: date | None,
    planned: date | None,
    transit_days: int | None,
    source: SourceData,
    issues: IssueLog,
    business_key: str,
) -> date | None:
    if ata is not None:
        return ata
    basis = asd if asd is not None else planned
    basis_name = "ASD" if asd is not None else mode
    if basis is not None and transit_days is not None:
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
    missing = []
    if basis is None:
        missing.append(basis_name)
    if transit_days is None:
        missing.append("海运周期")
    issues.add(
        f"ARRIVAL_{mode}_UNAVAILABLE",
        f"到货日期（按{mode}）缺少必要输入: {', '.join(missing)}",
        workbook=source.workbook_for("demand_detail").name,
        business_key=business_key,
        field=f"arrival_date_{mode.lower()}",
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
    source: SourceData,
    issues: IssueLog,
    business_key: str,
) -> str | None:
    if latest_asd is not None and latest_rpd is not None:
        return "Y" if latest_rpd > latest_asd else "N"
    missing = []
    if latest_asd is None:
        missing.append("最晚ASD")
    if latest_rpd is None:
        missing.append("最晚RPD")
    issues.add(
        "SHIPMENT_STATUS_UNAVAILABLE",
        f"货未发完无法判断，缺少有效字段: {', '.join(missing)}",
        workbook=source.workbook_for("demand_detail").name,
        business_key=business_key,
        field="shipment_incomplete",
    )
    return None


def _revenue_segment(
    multiple_demand: str,
    ata: date | None,
    asd: date | None,
    rpd: date | None,
    cpd: date | None,
    invalid_date_present: bool,
) -> str:
    if multiple_demand == "Y":
        return "需判断"
    if ata is not None or asd is not None:
        return "发未收"
    if rpd is not None or cpd is not None:
        return "订未发"
    if invalid_date_present:
        return "需判断"
    return "不要货"


def _fallback(*values: Any) -> Any:
    for value in values:
        if nonblank(value):
            return value
    return None


def _value(row: ParsedRow | None, field: str) -> Any:
    return row.values.get(field) if row is not None else None


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
