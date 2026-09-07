"""Reporting projection; automatic and final business facts remain untouched."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import re

from revenue_tool.domain.models import BaseRow
from revenue_tool.services.normalization import normalize_amount

MONTH_PATTERN = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])\Z")
SEGMENTS = ("订未发", "发未收", "交未验", "其他")
EXCLUDED = "未纳入汇总"
EMPTY_REGION = "（地区未填写）"


def report_month(value: str | None = None) -> str:
    if value is None:
        return date.today().strftime("%Y-%m")
    if not isinstance(value, str) or not MONTH_PATTERN.fullmatch(value) or value[:4] == "0000":
        raise ValueError("统计月份必须填写完整年月 YYYY-MM，例如2026-09")
    return value


def report_months(value=None) -> tuple[str, ...]:
    """One shared selection contract for the GUI, CLI and workbook writer."""
    if value is None or isinstance(value, str):
        return (report_month(value),)
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("请至少选择一个汇总月份")
    if any(not isinstance(item, str) for item in value):
        raise ValueError("每个汇总月份必须为完整年月YYYY-MM")
    months = tuple(sorted({report_month(item) for item in value}))
    if len(months) > 12:
        raise ValueError("一次最多选择12个汇总月份")
    return months


def summary_labels(month: str) -> tuple[str, ...]:
    # Stable cache members: month changes must never reorder/drop pivot columns.
    return ("前期累计", *SEGMENTS, "小计")


def cumulative_caption(month: str) -> str:
    number = int(report_month(month)[-2:])
    return f"1—{number - 1}月累计" if number > 1 else "前期累计（无）"


def region_label(value) -> str:
    return EMPTY_REGION if value is None or str(value).strip() == "" else str(value)


@dataclass(frozen=True)
class SummaryEntry:
    base_row: int
    region: str
    bucket: str
    amount: Decimal | None
    subtotal_copy: bool


@dataclass
class RegionalSummary:
    month: str
    mode: str
    labels: tuple[str, ...]
    regions: list[str]
    entries: list[SummaryEntry]
    totals: dict[str, list[Decimal]]
    excluded_count: int


def build_regional_summary(rows: list[BaseRow], month: str, mode: str) -> RegionalSummary:
    month = report_month(month)
    if mode not in ("rpd", "cpd"):
        raise ValueError("收入口径必须为rpd或cpd")
    labels = summary_labels(month)
    regions = sorted({region_label(row.values.get("region")) for row in rows})
    totals = {region: [Decimal("0.00") for _ in labels] for region in regions}
    entries = []
    excluded_count = 0
    for number, row in enumerate(rows, 2):
        values = row.values
        region = region_label(values.get("region"))
        raw_month = values.get(f"final_revenue_month_{mode}")
        amount = normalize_amount(values.get("final_revenue_forecast"))
        bucket = EXCLUDED
        if (amount is not None and isinstance(raw_month, str)
                and MONTH_PATTERN.fullmatch(raw_month)):
            if month[:4] + "-01" <= raw_month < month:
                bucket = labels[0]
            elif raw_month == month:
                segment = values.get("final_revenue_segment")
                category = segment if segment in SEGMENTS[:3] else "其他"
                bucket = labels[1 + SEGMENTS.index(category)]
        current = bucket in labels[1:5]
        excluded_count += bucket == EXCLUDED
        # A separate subtotal bucket makes native Show Details return each
        # current-period business row exactly once, without YTD records.
        for is_subtotal, category in ((False, bucket), (True, labels[5] if current else EXCLUDED)):
            entries.append(SummaryEntry(number, region, category, amount, is_subtotal))
            if category != EXCLUDED:
                totals[region][labels.index(category)] += amount
    return RegionalSummary(month, mode, labels, regions, entries, totals, excluded_count)
