from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any

from revenue_tool.domain.models import (
    BaseRow,
    ComparisonRow,
    CONTRACT_ONLY_NO_DEMAND,
    IssueLog,
    PreviousData,
)
from revenue_tool.services.normalization import (
    business_key_identity,
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
    current_by_key = {
        business_key_identity(
            row.values.get("contract_no"),
            row.values.get("supply_center"),
        ): row
        for row in current
        if row.row_kind != CONTRACT_ONLY_NO_DEMAND
    }
    result: list[ComparisonRow] = []
    for key in sorted(
        set(current_by_key) | set(previous.rows),
        key=lambda item: (
            normalize_lookup(item[0]),
            normalize_lookup(item[1]),
        ),
    ):
        current_row = current_by_key.get(key)
        previous_row = previous.rows.get(key)
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
