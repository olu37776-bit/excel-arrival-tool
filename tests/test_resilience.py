from datetime import date
from decimal import Decimal
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
from revenue_tool.services.calculation import (
    _arrival_date,
    _shipment_incomplete,
)


class ResilienceTest(unittest.TestCase):
    def test_shipment_incomplete_closes_missing_date_cases(self) -> None:
        self.assertIsNone(_shipment_incomplete(None, None))
        self.assertEqual("Y", _shipment_incomplete(None, date(2026, 8, 1)))
        self.assertEqual(
            "Y",
            _shipment_incomplete(date(2026, 7, 1), date(2026, 8, 1)),
        )
        self.assertEqual(
            "N",
            _shipment_incomplete(date(2026, 8, 1), date(2026, 8, 1)),
        )

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
        self.assertEqual(Decimal("0.00"), value)
        self.assertFalse(valid)

    def test_amounts_use_two_decimal_half_up_business_precision(self) -> None:
        cases = [
            (0, "0.00"),
            (0.0, "0.00"),
            (-0.0, "0.00"),
            (1e-12, "0.00"),
            (-4.440892098500626e-16, "0.00"),
            (0.0049, "0.00"),
            (0.005, "0.01"),
            (-0.0049, "0.00"),
            (-0.005, "-0.01"),
            (123.456, "123.46"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                value, valid = _parse_source_cell(
                    "amount",
                    SimpleNamespace(value=raw, data_type="n"),
                    CALENDAR_WINDOWS_1900,
                )
                self.assertTrue(valid)
                self.assertEqual(Decimal(expected), value)

    def test_invalid_nonblank_amount_degrades_to_numeric_zero(self) -> None:
        value, valid = _parse_source_cell(
            "amount",
            SimpleNamespace(value="not-an-amount", data_type="s"),
            CALENDAR_WINDOWS_1900,
        )
        self.assertEqual(Decimal("0.00"), value)
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

    def test_excel_value_error_is_a_valid_business_blank(self) -> None:
        workbook = Workbook()
        try:
            cell = workbook.active["A1"]
            cell.value = "#VALUE!"
            self.assertEqual("e", cell.data_type)

            value, valid = _parse_source_cell(
                "text", cell, CALENDAR_WINDOWS_1900
            )

            self.assertIsNone(value)
            self.assertTrue(valid)
        finally:
            workbook.close()

    def test_value_text_markers_are_business_blanks(self) -> None:
        for marker in ("VALUE", "#VALUE", "#VALUE!", " value "):
            with self.subTest(marker=marker):
                value, valid = _parse_source_cell(
                    "amount",
                    SimpleNamespace(value=marker, data_type="s"),
                    CALENDAR_WINDOWS_1900,
                )
                self.assertEqual(Decimal("0.00"), value)
                self.assertTrue(valid)

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
            shipment_incomplete="Y",
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
            shipment_incomplete="N",
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

    def test_unfinished_shipment_ignores_ata_and_asd(self) -> None:
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
            shipment_incomplete="Y",
            ata=date(2026, 9, 1),
            asd=date(2026, 8, 1),
            planned=date(2026, 7, 1),
            transit_days=5,
            source=source,
            issues=issues,
            business_key="C1 | SC1",
        )

        self.assertEqual(date(2026, 7, 6), result)
        self.assertEqual([], issues.items)

    def test_all_candidate_dates_blank_returns_no_arrival_issue(self) -> None:
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
            mode="CPD",
            shipment_incomplete=None,
            ata=None,
            asd=None,
            planned=None,
            transit_days=None,
            source=source,
            issues=issues,
            business_key="C1 | SC1",
        )

        self.assertIsNone(result)
        self.assertEqual([], issues.items)


if __name__ == "__main__":
    unittest.main()
