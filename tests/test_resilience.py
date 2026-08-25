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
            cell.value = "#N/A"
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
        source = SourceData(Path("source.xlsx"), {}, {})

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


if __name__ == "__main__":
    unittest.main()
