from datetime import date
from dataclasses import fields
from decimal import Decimal
from pathlib import Path
import unittest

from revenue_tool.config import load_config
from revenue_tool.domain.models import (
    CONTRACT_ONLY_NO_DEMAND,
    DEMAND_CENTER,
    HAS_DEMAND,
    NO_DEMAND,
    IssueLog,
    ParsedRow,
    SourceData,
)
from revenue_tool.domain.revenue_models import (
    ContractFinancialFact,
    DemandRecord,
    FulfillmentProjection,
)
from revenue_tool.services.fulfillment_projection import (
    FulfillmentProjectionService,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config(ROOT / "config" / "default.json")


class FulfillmentProjectionServiceTest(unittest.TestCase):
    def test_projection_does_not_own_contract_financial_amounts(self) -> None:
        names = {item.name for item in fields(FulfillmentProjection)}

        self.assertFalse(
            {"legacy_amount", "monthly_new_order", "revenue_forecast"}
            & names
        )

    def test_multi_center_and_same_center_records_use_existing_rules(self) -> None:
        fact = _fact("C001", Decimal("100.00"), Decimal("50.00"))
        records = [
            _record(
                "D1",
                "C001",
                "SC-A",
                row=3,
                status="待发货",
                incoterm="CIF",
                stock="Y",
                rpd=date(2026, 1, 10),
                cpd=date(2026, 1, 20),
            ),
            _record(
                "D2",
                "C001",
                "SC-A",
                row=4,
                status="运输中",
                incoterm="CIF",
                stock="N",
                rpd=date(2026, 1, 5),
                cpd=date(2026, 2, 1),
            ),
            _record(
                "D3",
                "C001",
                "SC-B",
                row=5,
                status="已到货",
                incoterm="EXW",
                stock="Y",
                ata=date(2026, 3, 10),
            ),
        ]
        issues = IssueLog()

        projections = FulfillmentProjectionService().build(
            [fact],
            records,
            _source([_transit_row("阿拉伯联合酋长国", "SC-A", 30)]),
            CONFIG,
            issues,
        )
        by_center = {item.supply_center: item for item in projections}

        self.assertEqual({"SC-A", "SC-B"}, set(by_center))
        sc_a = by_center["SC-A"]
        self.assertEqual(DEMAND_CENTER, sc_a.row_kind)
        self.assertEqual("Y", sc_a.multiple_supply_centers)
        self.assertEqual(2, sc_a.demand_record_count)
        self.assertEqual("待发货 | 运输中", sc_a.demand_status_summary)
        self.assertEqual("部分解锁", sc_a.stock_unlocked)
        self.assertEqual("Y", sc_a.split_shipment)
        self.assertEqual("Y", sc_a.multiple_demand)
        self.assertEqual("Y", sc_a.split_supply)
        self.assertEqual(date(2026, 1, 5), sc_a.rpd)
        self.assertEqual(date(2026, 1, 10), sc_a.latest_rpd)
        self.assertEqual("Y", sc_a.shipment_incomplete)
        self.assertEqual(date(2026, 2, 9), sc_a.arrival_date_rpd)
        self.assertEqual(date(2026, 3, 3), sc_a.arrival_date_cpd)
        self.assertEqual("2026-02", sc_a.revenue_month_rpd)
        self.assertEqual("2026-03", sc_a.revenue_month_cpd)
        self.assertEqual("需判断", sc_a.revenue_segment)
        self.assertEqual(("D1", "D2"), sc_a.demand_record_ids)
        self.assertIn("demand.xlsx/Demand!3", sc_a.source_row_summary)

        sc_b = by_center["SC-B"]
        self.assertEqual(1, sc_b.demand_record_count)
        self.assertEqual(5, sc_b.transit_days)
        self.assertEqual(date(2026, 3, 10), sc_b.arrival_date_rpd)
        self.assertEqual("发未收", sc_b.revenue_segment)

    def test_no_demand_contract_builds_controlled_placeholder(self) -> None:
        fact = _fact(
            "C002",
            Decimal("10.00"),
            Decimal("2.00"),
            demand_state=NO_DEMAND,
        )

        projection = FulfillmentProjectionService().build(
            [fact], [], _source([]), CONFIG, IssueLog()
        )[0]

        self.assertEqual(CONTRACT_ONLY_NO_DEMAND, projection.row_kind)
        self.assertIsNone(projection.supply_center)
        self.assertEqual(0, projection.demand_record_count)
        self.assertEqual("N", projection.multiple_supply_centers)
        self.assertEqual("N", projection.split_shipment)
        self.assertEqual("N", projection.multiple_demand)
        self.assertEqual("N", projection.split_supply)
        self.assertIsNone(projection.stock_unlocked)
        self.assertIsNone(projection.transit_days)
        self.assertIsNone(projection.arrival_date_rpd)
        self.assertIsNone(projection.arrival_date_cpd)
        self.assertEqual("不要货", projection.revenue_segment)

    def test_existing_demand_with_blank_center_is_not_placeholder(self) -> None:
        issues = IssueLog()

        projections = FulfillmentProjectionService().build(
            [_fact("C003", Decimal("1.00"), Decimal("0.00"))],
            [_record("D1", "C003", None, row=3, rpd=date(2026, 1, 1))],
            _source([]),
            CONFIG,
            issues,
        )

        self.assertEqual([], projections)
        self.assertEqual(["MISSING_SUPPLY_CENTER"], [item.code for item in issues.items])

    def test_zero_amount_with_planned_date_is_unrecorded_order(self) -> None:
        projection = FulfillmentProjectionService().build(
            [_fact("C004", Decimal("0.00"), Decimal("0.00"))],
            [
                _record(
                    "D1",
                    "C004",
                    "SC-A",
                    row=3,
                    incoterm="EXW",
                    rpd=date(2026, 1, 1),
                    cpd=date(2026, 1, 2),
                )
            ],
            _source([]),
            CONFIG,
            IssueLog(),
        )[0]

        self.assertEqual("未录入订货", projection.revenue_segment)


def _fact(
    contract: str,
    legacy: Decimal,
    monthly: Decimal,
    *,
    demand_state: str = HAS_DEMAND,
) -> ContractFinancialFact:
    return ContractFinancialFact(
        contract_no=contract,
        legacy_amount=legacy,
        monthly_new_order=monthly,
        revenue_forecast=legacy + monthly,
        bg="BG",
        region="地区",
        country="阿拉伯联合酋长国",
        carryover_type="交付类",
        customer_group="客户",
        project_name="项目",
        demand_state=demand_state,
    )


def _record(
    record_id: str,
    contract: str,
    center: str | None,
    *,
    row: int,
    status: str | None = None,
    incoterm: str | None = None,
    stock: str | None = None,
    ata: date | None = None,
    asd: date | None = None,
    rpd: date | None = None,
    cpd: date | None = None,
) -> DemandRecord:
    return DemandRecord(
        demand_record_id=record_id,
        contract_no=contract,
        supply_center=center,
        demand_status=status,
        incoterm=incoterm,
        stock_control_flag=stock,
        shipment_control_flag=stock,
        ata=ata,
        asd=asd,
        rpd=rpd,
        cpd=cpd,
        bg="BG",
        source_workbook="demand.xlsx",
        source_sheet="Demand",
        source_row_number=row,
        invalid_fields=(),
    )


def _source(transit_rows: list[ParsedRow]) -> SourceData:
    return SourceData(
        {
            "legacy": Path("legacy.xlsx"),
            "demand_detail": Path("demand.xlsx"),
            "transit": Path("transit.xlsx"),
        },
        {
            "legacy": [],
            "monthly_order": [],
            "demand_detail": [],
            "transit": transit_rows,
        },
        {
            "legacy": "Legacy",
            "demand_detail": "Demand",
            "transit": "Transit",
        },
    )


def _transit_row(country: str, center: str, days: int) -> ParsedRow:
    values = {
        "country": country,
        "supply_center": center,
        "transit_days": days,
    }
    return ParsedRow(
        role="transit",
        workbook="transit.xlsx",
        sheet="Transit",
        row_number=2,
        values=values,
        raw_values=dict(values),
    )


if __name__ == "__main__":
    unittest.main()
