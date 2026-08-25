from __future__ import annotations

from revenue_tool.domain.models import (
    ComparisonLine,
    PreviousRevenueLine,
    RevenueLine,
)


def compare_revenue_months(
    current: list[RevenueLine],
    previous: list[PreviousRevenueLine],
    delay_threshold_months: int = 1,
    only_delayed: bool = True,
) -> list[ComparisonLine]:
    previous_by_key = {row.business_key: row for row in previous}
    result: list[ComparisonLine] = []
    for row in current:
        old = previous_by_key.get(row.business_key)
        if old is None:
            continue
        delay = _month_index(row.revenue_month) - _month_index(
            old.previous_revenue_month
        )
        delayed = delay >= delay_threshold_months
        if only_delayed and not delayed:
            continue
        result.append(
            ComparisonLine(
                business_key=row.business_key,
                po_number=row.po_number,
                contract_number=row.contract_number,
                shipping_point=row.shipping_point,
                shipment_id=row.shipment_id,
                previous_revenue_month=old.previous_revenue_month,
                current_revenue_month=row.revenue_month,
                delay_months=delay,
                delayed=delayed,
            )
        )
    return sorted(
        result,
        key=lambda row: (-row.delay_months, row.po_number, row.business_key),
    )


def _month_index(value: str) -> int:
    year_text, month_text = value.split("-", maxsplit=1)
    return int(year_text) * 12 + int(month_text)

