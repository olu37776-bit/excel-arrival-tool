from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
import re
from typing import Any

from revenue_tool.domain.models import (
    BaseRow,
    ComparisonRow,
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    HAS_DEMAND,
    IssueLog,
    NO_DEMAND,
    PreviousData,
)
from revenue_tool.services.normalization import (
    business_key_identity,
    nonblank,
    normalize_lookup,
    normalize_text,
)


_MONTH_PATTERN = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def compare_revenue_months(
    current: list[BaseRow],
    previous: PreviousData,
    mode: str,
    workbook_name: str,
    issues: IssueLog,
) -> list[ComparisonRow]:
    if mode not in {"rpd", "cpd"}:
        raise ValueError("mode 必须为 rpd 或 cpd")
    field = f"revenue_month_{mode}"
    current_by_contract = _group_by_contract(current)
    previous_by_contract = _group_by_contract(previous.rows.values())
    state_handled_contracts: set[str] = set()
    result: list[ComparisonRow] = []

    for contract_identity in sorted(
        set(current_by_contract) | set(previous_by_contract),
        key=normalize_lookup,
    ):
        current_rows = current_by_contract.get(contract_identity, [])
        previous_rows = previous_by_contract.get(contract_identity, [])
        current_state = _contract_state(current_rows)
        previous_state = _contract_state(previous_rows)
        if "CONFLICT" in {current_state, previous_state}:
            _report_state_conflict_once(
                issues,
                workbook_name,
                contract_identity,
                current_state,
                previous_state,
            )
            state_handled_contracts.add(contract_identity)
            continue

        if previous_state == HAS_DEMAND and current_state == NO_DEMAND:
            placeholder = _first_row_of_kind(
                current_rows, CONTRACT_ONLY_NO_DEMAND
            )
            for previous_row in _rows_of_kind(previous_rows, DEMAND_CENTER):
                result.append(
                    _state_change_row(
                        field=field,
                        direction="变为不要货",
                        primary=placeholder,
                        fallback=previous_row,
                        supply_center=previous_row.values.get("supply_center"),
                        previous_row=previous_row,
                        current_row=None,
                        workbook_name=workbook_name,
                        issues=issues,
                    )
                )
            state_handled_contracts.add(contract_identity)
        elif previous_state == NO_DEMAND and current_state == HAS_DEMAND:
            for current_row in _rows_of_kind(current_rows, DEMAND_CENTER):
                result.append(
                    _state_change_row(
                        field=field,
                        direction="恢复要货",
                        primary=current_row,
                        fallback=None,
                        supply_center=current_row.values.get("supply_center"),
                        previous_row=None,
                        current_row=current_row,
                        workbook_name=workbook_name,
                        issues=issues,
                    )
                )
            state_handled_contracts.add(contract_identity)
        elif previous_state == NO_DEMAND and current_state == NO_DEMAND:
            state_handled_contracts.add(contract_identity)

    current_by_key = {
        business_key_identity(
            row.values.get("contract_no"),
            row.values.get("supply_center"),
        ): row
        for row in current
        if row.row_kind == DEMAND_CENTER
        and _contract_identity(row) not in state_handled_contracts
    }
    previous_by_key = {
        key: row
        for key, row in previous.rows.items()
        if row.row_kind == DEMAND_CENTER
        and _contract_identity(row) not in state_handled_contracts
    }
    for key in sorted(
        set(current_by_key) | set(previous_by_key),
        key=lambda item: (
            normalize_lookup(item[0]),
            normalize_lookup(item[1]),
        ),
    ):
        current_row = current_by_key.get(key)
        previous_row = previous_by_key.get(key)
        current_month = _normalize_month(
            current_row.values.get(field) if current_row else None,
            field,
            workbook_name,
            key,
            "本期",
            issues,
        )
        previous_month = _normalize_month(
            previous_row.values.get(field) if previous_row else None,
            field,
            workbook_name,
            key,
            "上期",
            issues,
        )
        if current_month == previous_month:
            continue

        if previous_month is None and current_month is not None:
            direction = "新增"
            change_months = None
        elif previous_month is not None and current_month is None:
            direction = "取消"
            change_months = None
        elif previous_month is not None and current_month is not None:
            delta = _month_index(current_month) - _month_index(previous_month)
            direction = "延后" if delta > 0 else "提前"
            change_months = abs(delta)
        else:
            continue

        attributes = (
            current_row.values
            if current_row is not None
            else previous_row.values
        )
        values = {
            field_id: attributes.get(field_id)
            for field_id in (
                "contract_no",
                "legacy_amount",
                "monthly_new_order",
                "region",
                "country",
                "carryover_type",
                "customer_group",
                "supply_center",
            )
        }
        values.update(
            {
                "previous_month": previous_month,
                "current_month": current_month,
                "direction": direction,
                "change_months": change_months,
            }
        )
        result.append(ComparisonRow(values))
    return result


def _group_by_contract(
    rows: Iterable[BaseRow],
) -> dict[str, list[BaseRow]]:
    result: dict[str, list[BaseRow]] = {}
    for row in rows:
        result.setdefault(_contract_identity(row), []).append(row)
    return result


def _contract_identity(row: BaseRow) -> str:
    return business_key_identity(row.values.get("contract_no"), None)[0]


def _contract_state(rows: list[BaseRow]) -> str | None:
    kinds = {row.row_kind for row in rows}
    has_demand = DEMAND_CENTER in kinds
    no_demand = CONTRACT_ONLY_NO_DEMAND in kinds
    if has_demand and no_demand:
        return "CONFLICT"
    if has_demand:
        return HAS_DEMAND
    if no_demand:
        return NO_DEMAND
    return None


def _rows_of_kind(rows: list[BaseRow], row_kind: str) -> list[BaseRow]:
    return sorted(
        (row for row in rows if row.row_kind == row_kind),
        key=lambda row: normalize_lookup(row.values.get("supply_center")),
    )


def _first_row_of_kind(
    rows: list[BaseRow], row_kind: str
) -> BaseRow | None:
    return next((row for row in rows if row.row_kind == row_kind), None)


def _state_change_row(
    *,
    field: str,
    direction: str,
    primary: BaseRow | None,
    fallback: BaseRow | None,
    supply_center: Any,
    previous_row: BaseRow | None,
    current_row: BaseRow | None,
    workbook_name: str,
    issues: IssueLog,
) -> ComparisonRow:
    contract_no = None
    if primary is not None:
        contract_no = primary.values.get("contract_no")
    elif fallback is not None:
        contract_no = fallback.values.get("contract_no")
    key = business_key_identity(contract_no, supply_center)
    previous_month = _normalize_month(
        previous_row.values.get(field) if previous_row else None,
        field,
        workbook_name,
        key,
        "上期",
        issues,
    )
    current_month = _normalize_month(
        current_row.values.get(field) if current_row else None,
        field,
        workbook_name,
        key,
        "本期",
        issues,
    )
    values = {
        field_id: _preferred_value(primary, fallback, field_id)
        for field_id in (
            "contract_no",
            "legacy_amount",
            "monthly_new_order",
            "region",
            "country",
            "carryover_type",
            "customer_group",
        )
    }
    values["supply_center"] = supply_center
    values.update(
        {
            "previous_month": previous_month,
            "current_month": current_month,
            "direction": direction,
            "change_months": None,
        }
    )
    return ComparisonRow(values)


def _preferred_value(
    primary: BaseRow | None,
    fallback: BaseRow | None,
    field: str,
) -> Any:
    value = primary.values.get(field) if primary is not None else None
    if nonblank(value):
        return value
    return fallback.values.get(field) if fallback is not None else value


def _report_state_conflict_once(
    issues: IssueLog,
    workbook_name: str,
    contract_identity: str,
    current_state: str | None,
    previous_state: str | None,
) -> None:
    if any(
        issue.code == "CONTRACT_DEMAND_STATE_CONFLICT"
        and issue.business_key == contract_identity
        for issue in issues.items
    ):
        return
    issues.add(
        "CONTRACT_DEMAND_STATE_CONFLICT",
        "同一期同一合同同时存在有要货和不要货状态，已排除跨期比较",
        workbook=workbook_name,
        business_key=contract_identity,
        field="row_kind",
        raw_value=f"上期={previous_state or '无'} | 本期={current_state or '无'}",
    )


def build_supply_pull_rows(
    current: list[BaseRow],
    workbook_name: str,
    issues: IssueLog,
) -> list[ComparisonRow]:
    result: list[ComparisonRow] = []
    for row in current:
        if row.row_kind == CONTRACT_ONLY_NO_DEMAND:
            continue
        key = business_key_identity(
            row.values.get("contract_no"),
            row.values.get("supply_center"),
        )
        rpd_month = _normalize_month(
            row.values.get("revenue_month_rpd"),
            "revenue_month_rpd",
            workbook_name,
            key,
            "本期",
            issues,
        )
        cpd_month = _normalize_month(
            row.values.get("revenue_month_cpd"),
            "revenue_month_cpd",
            workbook_name,
            key,
            "本期",
            issues,
        )
        if (
            rpd_month is None
            or cpd_month is None
            or abs(_month_index(rpd_month) - _month_index(cpd_month)) < 1
        ):
            continue
        values = {
            field: row.values.get(field)
            for field in (
                "contract_no",
                "legacy_amount",
                "monthly_new_order",
                "region",
                "country",
                "carryover_type",
                "customer_group",
                "supply_center",
            )
        }
        values.update(
            {
                "revenue_month_rpd": rpd_month,
                "revenue_month_cpd": cpd_month,
            }
        )
        result.append(ComparisonRow(values))
    return result


def _normalize_month(
    value: Any,
    field: str,
    workbook_name: str,
    key: tuple[str, str],
    period: str,
    issues: IssueLog,
) -> str | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m")
    text = normalize_text(value)
    if _MONTH_PATTERN.fullmatch(text):
        return text
    issues.add(
        "INVALID_REVENUE_MONTH",
        f"{period}自动收入年月格式无效，本次比较按空值处理",
        workbook=workbook_name,
        business_key=f"{key[0]} | {key[1]}",
        field=field,
        raw_value=value,
    )
    return None


def _month_index(value: str) -> int:
    year, month = (int(part) for part in value.split("-", maxsplit=1))
    return year * 12 + month
