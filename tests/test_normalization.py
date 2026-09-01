from datetime import date, datetime
from decimal import Decimal
import unittest

from revenue_tool.services.normalization import (
    MANUAL_MONTH_BLANK,
    MANUAL_MONTH_INVALID,
    MANUAL_MONTH_NORMALIZED,
    MANUAL_MONTH_YEAR_REQUIRED,
    normalize_manual_revenue_month,
)


class ManualRevenueMonthNormalizationTest(unittest.TestCase):
    def test_complete_year_month_formats_are_normalized(self) -> None:
        values = (
            "2026-09",
            "2026-9",
            "2026/09",
            "2026/9",
            "2026.09",
            "2026.9",
            "2026年09月",
            "2026年9月",
            "202609",
            "２０２６ 年 ９ 月",
            202609,
            202609.0,
            Decimal("202609"),
        )
        for raw in values:
            with self.subTest(raw=raw):
                result = normalize_manual_revenue_month(raw)
                self.assertEqual(MANUAL_MONTH_NORMALIZED, result.status)
                self.assertEqual("2026-09", result.value)

    def test_dates_and_legacy_english_months_are_normalized(self) -> None:
        values = (
            date(2026, 9, 1),
            datetime(2026, 9, 15, 12, 30),
            "2026-09-01",
            "2026/9/1",
            "2026.09.01",
            "2026年9月1日",
            "Sep-26",
            "Sep-2026",
            "sep-26",
        )
        for raw in values:
            with self.subTest(raw=raw):
                result = normalize_manual_revenue_month(raw)
                self.assertEqual(MANUAL_MONTH_NORMALIZED, result.status)
                self.assertEqual("2026-09", result.value)

    def test_month_only_formats_use_the_unique_nearest_year(self) -> None:
        values = ("9", "09", "9月", "09月", "9月份", 9, 9.0)
        for raw in values:
            with self.subTest(raw=raw):
                result = normalize_manual_revenue_month(
                    raw,
                    primary_reference_month="2026-06",
                )
                self.assertEqual("2026-09", result.value)
                self.assertEqual("2026-06", result.reference_month)

    def test_nearest_year_inference_handles_year_boundaries(self) -> None:
        cases = (
            ("2026-12", "1月", "2027-01"),
            ("2026-01", "12月", "2025-12"),
            ("2026-11", "2月", "2027-02"),
        )
        for reference, raw, expected in cases:
            with self.subTest(reference=reference, raw=raw):
                result = normalize_manual_revenue_month(
                    raw,
                    primary_reference_month=reference,
                )
                self.assertEqual(expected, result.value)

    def test_primary_reference_wins_and_secondary_is_fallback(self) -> None:
        primary = normalize_manual_revenue_month(
            "1月",
            primary_reference_month="2026-12",
            secondary_reference_month="2024-12",
        )
        fallback = normalize_manual_revenue_month(
            "1月",
            primary_reference_month="invalid",
            secondary_reference_month=date(2026, 12, 15),
        )

        self.assertEqual("2027-01", primary.value)
        self.assertEqual("2026-12", primary.reference_month)
        self.assertEqual("2027-01", fallback.value)
        self.assertEqual("2026-12", fallback.reference_month)

    def test_ambiguous_or_missing_reference_requires_explicit_year(self) -> None:
        ambiguous = normalize_manual_revenue_month(
            "9月",
            primary_reference_month="2026-03",
        )
        missing = normalize_manual_revenue_month("9月")
        complete = normalize_manual_revenue_month("2026-09")

        self.assertEqual(MANUAL_MONTH_YEAR_REQUIRED, ambiguous.status)
        self.assertIsNone(ambiguous.value)
        self.assertEqual("2026-03", ambiguous.reference_month)
        self.assertEqual(MANUAL_MONTH_YEAR_REQUIRED, missing.status)
        self.assertIsNone(missing.value)
        self.assertEqual("2026-09", complete.value)

    def test_invalid_nonblank_values_are_rejected(self) -> None:
        values = (
            0,
            "0月",
            13,
            "13月",
            "2026-00",
            "2026-13",
            "2026-02-30",
            "9-10",
            "9月或10月",
            "九月份左右",
            "abc",
            9.5,
            202609.5,
        )
        for raw in values:
            with self.subTest(raw=raw):
                result = normalize_manual_revenue_month(
                    raw,
                    primary_reference_month="2026-06",
                )
                self.assertEqual(MANUAL_MONTH_INVALID, result.status)
                self.assertIsNone(result.value)

    def test_business_blank_values_remain_blank(self) -> None:
        values = (
            None,
            "",
            " \t\n　",
            "(空白)",
            "VALUE",
            "#VALUE",
            "#VALUE!",
        )
        for raw in values:
            with self.subTest(raw=raw):
                result = normalize_manual_revenue_month(
                    raw,
                    primary_reference_month="2026-06",
                    data_type="e" if raw == "#VALUE!" else None,
                )
                self.assertEqual(MANUAL_MONTH_BLANK, result.status)
                self.assertIsNone(result.value)


if __name__ == "__main__":
    unittest.main()
