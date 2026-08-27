from dataclasses import fields
from datetime import date
from decimal import Decimal
import unittest

from revenue_tool.domain.models import ParsedRow
from revenue_tool.domain.revenue_models import DemandRecord
from revenue_tool.services.demand_records import DemandRecordService


class DemandRecordServiceTest(unittest.TestCase):
    def test_preserves_run_trace_and_invalid_field_evidence(self) -> None:
        parsed = _row(
            7,
            contract_no="C001",
            supply_center="SC-A",
            demand_status="已审核",
            incoterm="CIF",
            stock_control_flag="Y",
            shipment_control_flag="N",
            ata=date(2026, 1, 1),
            asd=date(2026, 1, 2),
            rpd=date(2026, 1, 3),
            cpd=date(2026, 1, 4),
            bg="BG-1",
            invalid_fields=frozenset({"shipment_control_flag"}),
        )

        record = DemandRecordService().build([parsed])[0]

        self.assertEqual("C001", record.contract_no)
        self.assertEqual("SC-A", record.supply_center)
        self.assertEqual("demand.xlsx", record.source_workbook)
        self.assertEqual("Demand", record.source_sheet)
        self.assertEqual(7, record.source_row_number)
        self.assertEqual(("shipment_control_flag",), record.invalid_fields)
        self.assertTrue(record.demand_record_id.startswith("DR-"))

    def test_same_input_has_same_run_trace_id_but_row_move_changes_it(self) -> None:
        service = DemandRecordService()
        original = _row(3, contract_no="C001", supply_center="SC-A")
        moved = _row(4, contract_no="C001", supply_center="SC-A")

        first = service.build([original])[0]
        second = service.build([original])[0]
        after_move = service.build([moved])[0]

        self.assertEqual(first.demand_record_id, second.demand_record_id)
        self.assertNotEqual(first.demand_record_id, after_move.demand_record_id)

    def test_same_center_multiple_status_records_remain_distinct_evidence(self) -> None:
        records = DemandRecordService().build(
            [
                _row(
                    3,
                    contract_no="C001",
                    supply_center="SC-A",
                    demand_status="待发货",
                ),
                _row(
                    4,
                    contract_no="C001",
                    supply_center="SC-A",
                    demand_status="运输中",
                ),
            ]
        )

        self.assertEqual(2, len(records))
        self.assertEqual(
            ["待发货", "运输中"],
            [item.demand_status for item in records],
        )

    def test_demand_record_has_no_contract_or_manual_amount_fields(self) -> None:
        names = {item.name for item in fields(DemandRecord)}

        self.assertFalse(
            {
                "legacy_amount",
                "monthly_new_order",
                "revenue_forecast",
                "manual_allocated_amount",
                "final_allocated_amount",
            }
            & names
        )

        parsed = _row(
            3,
            contract_no="C001",
            supply_center="SC-A",
            legacy_amount=Decimal("999.00"),
        )
        record = DemandRecordService().build([parsed])[0]
        self.assertFalse(hasattr(record, "legacy_amount"))


def _row(
    row_number: int,
    *,
    invalid_fields: frozenset[str] = frozenset(),
    **overrides,
) -> ParsedRow:
    values = {
        "contract_no": None,
        "supply_center": None,
        "demand_status": None,
        "incoterm": None,
        "stock_control_flag": None,
        "shipment_control_flag": None,
        "ata": None,
        "asd": None,
        "rpd": None,
        "cpd": None,
        "bg": None,
    }
    values.update(overrides)
    return ParsedRow(
        role="demand_detail",
        workbook="demand.xlsx",
        sheet="Demand",
        row_number=row_number,
        values=values,
        raw_values=dict(values),
        invalid_fields=invalid_fields,
    )


if __name__ == "__main__":
    unittest.main()
