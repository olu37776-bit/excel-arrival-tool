from datetime import date
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpyxl import Workbook
from openpyxl.utils.datetime import CALENDAR_WINDOWS_1900

from revenue_tool.adapters.excel_reader import (
    _parse_date,
    _parse_nonnegative_integer,
    _parse_source_cell,
)
from revenue_tool.domain.models import IssueLog, SourceData
from revenue_tool.services.calculation import _arrival_date


class ResilienceTest(unittest.TestCase):
    def test_nonfinite_transit_is_invalid_without_exception(self) -> None:
        self.assertIsNone(_parse_nonnegative_integer("NaN"))
        self.assertIsNone(_parse_nonnegative_integer("Infinity"))

    def test_displayed_integer_transit_rounds_half_up(self) -> None:
        self.assertEqual(30, _parse_nonnegative_integer(29.6, "#,##0"))
        self.assertEqual(30, _parse_nonnegative_integer(29.5, "#,##0"))
        self.assertIsNone(_parse_nonnegative_integer(29.6, "General"))

    def test_blank_placeholder_is_a_valid_empty_date(self) -> None:
        value, valid = _parse_source_cell(
            "date",
            SimpleNamespace(value="（空白）", data_type="s"),
            CALENDAR_WINDOWS_1900,
        )
        self.assertIsNone(value)
        self.assertTrue(valid)

    def test_blank_placeholder_is_a_valid_empty_text(self) -> None:
        value, valid = _parse_source_cell(
            "text",
            SimpleNamespace(value="（空白）", data_type="s"),
            CALENDAR_WINDOWS_1900,
        )
        self.assertIsNone(value)
        self.assertTrue(valid)

    def test_amount_outside_excel_numeric_range_is_invalid(self) -> None:
        value, valid = _parse_source_cell(
            "amount",
            SimpleNamespace(value="1E10000"),
            CALENDAR_WINDOWS_1900,
        )
        self.assertIsNone(value)
        self.assertFalse(valid)

    def test_excel_serial_zero_is_not_treated_as_valid_date(self) -> None:
        self.assertIsNone(_parse_date(0, CALENDAR_WINDOWS_1900))

    def test_invalid_flag_is_excluded_after_issue_detection(self) -> None:
        value, valid = _parse_source_cell(
            "flag",
            SimpleNamespace(value="YES"),
            CALENDAR_WINDOWS_1900,
        )
        self.assertIsNone(value)
        self.assertFalse(valid)

    def test_excel_error_cell_is_invalid_without_exception(self) -> None:
        workbook = Workbook()
        try:
            cell = workbook.active["A1"]
            cell.value = "#VALUE!"
            self.assertEqual("e", cell.data_type)

            value, valid = _parse_source_cell(
                "text", cell, CALENDAR_WINDOWS_1900
            )

            self.assertIsNone(value)
            self.assertFalse(valid)
        finally:
            workbook.close()

    def test_date_overflow_becomes_nonblocking_issue(self) -> None:
        issues = IssueLog()
        source = SourceData(
            {
                "legacy": Path("legacy.xlsx"),
                "monthly_order": Path("monthly.xlsx"),
                "demand_detail": Path("demand.xlsx"),
                "transit": Path("transit.xlsx"),
            },
            {},
            {},
        )

        result = _arrival_date(
            mode="RPD",
            ata=None,
            asd=None,
            planned=date.max,
            transit_days=1,
            source=source,
            issues=issues,
            business_key="C1 | SC1",
        )

        self.assertIsNone(result)
        self.assertEqual("ARRIVAL_RPD_OVERFLOW", issues.items[0].code)

    def test_asd_route_also_adds_transit_days(self) -> None:
        issues = IssueLog()
        source = SourceData(
            {
                "legacy": Path("legacy.xlsx"),
                "monthly_order": Path("monthly.xlsx"),
                "demand_detail": Path("demand.xlsx"),
                "transit": Path("transit.xlsx"),
            },
            {},
            {},
        )

        result = _arrival_date(
            mode="RPD",
            ata=None,
            asd=date(2026, 8, 1),
            planned=date(2026, 7, 1),
            transit_days=5,
            source=source,
            issues=issues,
            business_key="C1 | SC1",
        )

        self.assertEqual(date(2026, 8, 6), result)
        self.assertEqual([], issues.items)


if __name__ == "__main__":
    unittest.main()
