from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class PrdRecord:
    po_number: str
    prd: date | None
    original_po_quantity: Decimal | None
    contract_number: str = ""
    shipping_point: str = ""


@dataclass(frozen=True)
class ShipmentRecord:
    po_number: str
    plan_date: date
    plan_quantity: Decimal
    contract_number: str
    shipping_point: str
    trade_type: str
    shipment_id: str = ""
    revenue_amount: Decimal | None = None
    source_row: int = 0


@dataclass(frozen=True)
class TransitRule:
    trade_type: str
    transit_days: int


@dataclass(frozen=True)
class RevenueLine:
    business_key: str
    po_number: str
    contract_number: str
    shipping_point: str
    shipment_id: str
    trade_type: str
    prd: date | None
    original_po_quantity: Decimal | None
    plan_date: date
    plan_quantity: Decimal
    transit_days: int
    arrival_date: date
    revenue_month: str
    revenue_amount: Decimal | None


@dataclass(frozen=True)
class RevenueSummaryLine:
    revenue_month: str
    contract_number: str
    shipping_point: str
    trade_type: str
    plan_quantity: Decimal
    revenue_amount: Decimal | None
    shipment_count: int


@dataclass(frozen=True)
class PreviousRevenueLine:
    business_key: str
    po_number: str
    contract_number: str
    shipping_point: str
    shipment_id: str
    previous_revenue_month: str


@dataclass(frozen=True)
class ComparisonLine:
    business_key: str
    po_number: str
    contract_number: str
    shipping_point: str
    shipment_id: str
    previous_revenue_month: str
    current_revenue_month: str
    delay_months: int
    delayed: bool

