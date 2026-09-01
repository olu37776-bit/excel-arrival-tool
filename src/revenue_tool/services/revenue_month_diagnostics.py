from __future__ import annotations

from datetime import date, datetime
from typing import Any

from revenue_tool.domain.models import BaseRow, DEMAND_CENTER, IssueLog
from revenue_tool.services.normalization import nonblank, normalize_text


ISSUE_CODE = "REVENUE_MONTH_ONE_SIDE_MISSING"
ISSUE_MESSAGE = (
    "RPD/CPD收入年月仅一侧可用，请核对对应计划日期、"
    "到货日期及海运周期"
)


class RevenueMonthDiagnostics:
    """Add result-level diagnostics after both revenue months are calculated."""

    def analyze(
        self,
        rows: list[BaseRow],
        *,
        workbook: str,
        sheet: str,
        issues: IssueLog,
    ) -> None:
        emitted_keys = {
            issue.business_key
            for issue in issues.items
            if issue.code == ISSUE_CODE
        }
        for row in rows:
            if row.row_kind != DEMAND_CENTER:
                continue

            values = row.values
            rpd_month = values.get("revenue_month_rpd")
            cpd_month = values.get("revenue_month_cpd")
            if nonblank(rpd_month) == nonblank(cpd_month):
                continue

            business_key = _business_key(values)
            if business_key in emitted_keys:
                continue
            emitted_keys.add(business_key)
            issues.add(
                ISSUE_CODE,
                ISSUE_MESSAGE,
                severity="WARNING",
                workbook=workbook,
                sheet=sheet,
                business_key=business_key,
                field="revenue_month_rpd+revenue_month_cpd",
                raw_value=(
                    f"RPD={_display(rpd_month)}; "
                    f"CPD={_display(cpd_month)}; "
                    "到货日期（按RPD）="
                    f"{_display(values.get('arrival_date_rpd'))}; "
                    "到货日期（按CPD）="
                    f"{_display(values.get('arrival_date_cpd'))}"
                ),
            )


def _business_key(values: dict[str, Any]) -> str:
    return (
        f"{normalize_text(values.get('contract_no'))} | "
        f"{normalize_text(values.get('supply_center'))}"
    )


def _display(value: Any) -> str:
    if not nonblank(value):
        return "空"
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return normalize_text(value)
