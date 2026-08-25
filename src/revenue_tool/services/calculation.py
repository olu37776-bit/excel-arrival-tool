from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from typing import Iterable

from revenue_tool.domain.models import (
    PrdRecord,
    RevenueLine,
    RevenueSummaryLine,
    ShipmentRecord,
)
from revenue_tool.rules.grouping import PrdSelectionRule, ShipmentGroupingRule
from revenue_tool.rules.transit import TransitDaysResolver


class RevenueCalculator:
    def __init__(
        self,
        grouping_rule: ShipmentGroupingRule,
        prd_rule: PrdSelectionRule,
        transit_resolver: TransitDaysResolver,
    ) -> None:
        self._grouping_rule = grouping_rule
        self._prd_rule = prd_rule
        self._transit_resolver = transit_resolver

    def calculate(
        self,
        prd_rows: Iterable[PrdRecord],
        shipment_rows: Iterable[ShipmentRecord],
    ) -> list[RevenueLine]:
        prd_rows = list(prd_rows)
        shipments = self._grouping_rule.apply(shipment_rows)
        result: list[RevenueLine] = []
        for shipment in shipments:
            prd, original_quantity = self._prd_rule.select(prd_rows, shipment)
            transit_days = self._transit_resolver.resolve(shipment.trade_type)
            arrival_date = shipment.plan_date + timedelta(days=transit_days)
            result.append(
                RevenueLine(
                    business_key=_business_key(shipment),
                    po_number=shipment.po_number,
                    contract_number=shipment.contract_number,
                    shipping_point=shipment.shipping_point,
                    shipment_id=shipment.shipment_id,
                    trade_type=shipment.trade_type,
                    prd=prd,
                    original_po_quantity=original_quantity,
                    plan_date=shipment.plan_date,
                    plan_quantity=shipment.plan_quantity,
                    transit_days=transit_days,
                    arrival_date=arrival_date,
                    revenue_month=arrival_date.strftime("%Y-%m"),
                    revenue_amount=shipment.revenue_amount,
                )
            )
        return sorted(
            result,
            key=lambda row: (
                row.revenue_month,
                row.contract_number,
                row.shipping_point,
                row.po_number,
                row.business_key,
            ),
        )


def summarise(rows: Iterable[RevenueLine]) -> list[RevenueSummaryLine]:
    grouped: dict[tuple[str, str, str, str], list[RevenueLine]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                row.revenue_month,
                row.contract_number,
                row.shipping_point,
                row.trade_type,
            )
        ].append(row)

    summary: list[RevenueSummaryLine] = []
    for key, values in sorted(grouped.items()):
        amounts = [value.revenue_amount for value in values]
        has_amount = any(value is not None for value in amounts)
        summary.append(
            RevenueSummaryLine(
                revenue_month=key[0],
                contract_number=key[1],
                shipping_point=key[2],
                trade_type=key[3],
                plan_quantity=sum(
                    (value.plan_quantity for value in values), Decimal("0")
                ),
                revenue_amount=(
                    sum(
                        (value or Decimal("0") for value in amounts), Decimal("0")
                    )
                    if has_amount
                    else None
                ),
                shipment_count=len(values),
            )
        )
    return summary


def _business_key(shipment: ShipmentRecord) -> str:
    if shipment.shipment_id:
        raw = f"shipment:{shipment.shipment_id}"
    else:
        raw = "|".join(
            (
                shipment.po_number,
                shipment.contract_number,
                shipment.shipping_point,
                shipment.trade_type,
                format(shipment.plan_quantity, "f"),
            )
        )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"REV-{digest}"

