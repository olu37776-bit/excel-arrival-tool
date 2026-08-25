from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from decimal import Decimal
from typing import Iterable

from revenue_tool.domain.models import PrdRecord, ShipmentRecord


class ShipmentGroupingRule:
    """Deduplicates only rows that satisfy every configured same-field condition."""

    def __init__(
        self,
        same_fields: list[str],
        quantity_aggregation: str = "max",
        revenue_amount_aggregation: str = "max",
    ) -> None:
        self.same_fields = tuple(same_fields)
        self.quantity_aggregation = quantity_aggregation
        self.revenue_amount_aggregation = revenue_amount_aggregation

    def apply(self, rows: Iterable[ShipmentRecord]) -> list[ShipmentRecord]:
        groups: dict[tuple[object, ...], list[ShipmentRecord]] = defaultdict(list)
        for row in rows:
            key = tuple(getattr(row, field) for field in self.same_fields)
            groups[key].append(row)

        result: list[ShipmentRecord] = []
        for grouped_rows in groups.values():
            first = min(grouped_rows, key=lambda row: row.source_row)
            result.append(
                replace(
                    first,
                    plan_quantity=_aggregate_decimal(
                        [row.plan_quantity for row in grouped_rows],
                        self.quantity_aggregation,
                    )
                    or Decimal("0"),
                    revenue_amount=_aggregate_decimal(
                        [row.revenue_amount for row in grouped_rows],
                        self.revenue_amount_aggregation,
                    ),
                )
            )
        return sorted(result, key=_shipment_sort_key)


class PrdSelectionRule:
    """Selects the earliest PRD and maximum original quantity for a PO scope."""

    def __init__(self, date_aggregation: str = "min", quantity_aggregation: str = "max") -> None:
        self.date_aggregation = date_aggregation
        self.quantity_aggregation = quantity_aggregation

    def select(
        self,
        rows: Iterable[PrdRecord],
        shipment: ShipmentRecord,
    ) -> tuple[object | None, Decimal | None]:
        candidates = [row for row in rows if row.po_number == shipment.po_number]
        scoped = [
            row
            for row in candidates
            if (not row.contract_number or row.contract_number == shipment.contract_number)
            and (not row.shipping_point or row.shipping_point == shipment.shipping_point)
        ]
        if scoped:
            candidates = scoped
        dates = [row.prd for row in candidates if row.prd is not None]
        quantities = [
            row.original_po_quantity
            for row in candidates
            if row.original_po_quantity is not None
        ]
        selected_date = _aggregate_value(dates, self.date_aggregation)
        selected_quantity = _aggregate_decimal(quantities, self.quantity_aggregation)
        return selected_date, selected_quantity


def _aggregate_decimal(
    values: Iterable[Decimal | None], mode: str
) -> Decimal | None:
    present = [value for value in values if value is not None]
    return _aggregate_value(present, mode)


def _aggregate_value(values: list, mode: str):
    if not values:
        return None
    if mode == "min":
        return min(values)
    if mode == "max":
        return max(values)
    if mode == "sum":
        return sum(values)
    raise ValueError(f"Unsupported aggregation mode: {mode}")


def _shipment_sort_key(row: ShipmentRecord) -> tuple[object, ...]:
    return (
        row.po_number,
        row.contract_number,
        row.shipping_point,
        row.plan_date,
        row.plan_quantity,
        row.trade_type,
        row.shipment_id,
    )

