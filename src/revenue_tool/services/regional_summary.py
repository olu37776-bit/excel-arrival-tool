"""All actual revenue months, displayed horizontally without a YTD bucket."""
from dataclasses import dataclass
from decimal import Decimal
import re

from revenue_tool.services.final_revenue import calculate_final_values
from revenue_tool.services.normalization import normalize_amount

MONTH_PATTERN = re.compile(r'[0-9]{4}-(0[1-9]|1[0-2])\Z')
SEGMENTS = ('订未发', '发未收', '交未验', '其他')
LABELS = (*SEGMENTS, '小计')
EXCLUDED = '未纳入汇总'
EMPTY_REGION = '（地区未填写）'


def valid_month(value):
    return isinstance(value, str) and bool(MONTH_PATTERN.fullmatch(value)) and value[:4] != '0000'


def region_label(value):
    return EMPTY_REGION if value is None or str(value).strip() == '' else str(value)


def discover_months(rows):
    return tuple(sorted({month for row in rows
        for field, month in calculate_final_values(row.values).items()
        if field in ('final_revenue_month_rpd', 'final_revenue_month_cpd') and valid_month(month)}))


@dataclass(frozen=True)
class SummaryEntry:
    base_row: int
    region: str
    month: str
    bucket: str
    amount: Decimal | None
    subtotal_copy: bool


@dataclass
class RegionalSummary:
    mode: str
    months: tuple[str, ...]
    regions: list[str]
    entries: list[SummaryEntry]
    totals: dict[str, dict[str, list[Decimal]]]


def build_regional_summary(rows, mode, months=None):
    if mode not in ('rpd', 'cpd'):
        raise ValueError('收入口径必须为rpd或cpd')
    months = discover_months(rows) if months is None else tuple(months)
    regions = sorted({region_label(row.values.get('region')) for row in rows})
    totals = {region: {month: [Decimal('0.00')] * 5 for month in months} for region in regions}
    entries = []
    for number, row in enumerate(rows, 2):
        final = calculate_final_values(row.values)
        raw_month = final[f'final_revenue_month_{mode}']
        month = raw_month if valid_month(raw_month) else EXCLUDED
        region = region_label(row.values.get('region'))
        amount = normalize_amount(final['final_revenue_forecast'])
        segment = final['final_revenue_segment']
        bucket = segment if segment in SEGMENTS[:3] else '其他'
        if amount is None or month not in months:
            bucket = EXCLUDED
        for subtotal, category in ((False, bucket), (True, '小计' if bucket != EXCLUDED else EXCLUDED)):
            entries.append(SummaryEntry(number, region, month, category, amount, subtotal))
            if category != EXCLUDED:
                totals[region][month][LABELS.index(category)] += amount
    return RegionalSummary(mode, months, regions, entries, totals)
