from pathlib import Path
import unittest

from revenue_tool.domain.models import IssueLog, ParsedRow, SourceData
from revenue_tool.services.calculation import (
    _build_transit_index,
    _resolve_transit_days,
)


class TransitDiagnosticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SourceData(
            {
                "legacy": Path("legacy.xlsx"),
                "demand_detail": Path("demand.xlsx"),
                "transit": Path("transit.xlsx"),
            },
            {},
            {
                "demand_detail": "Sheet2",
                "transit": "Sheet3",
            },
        )
        self.fixed = {"FCA": 5, "FOB": 5, "EXW": 5}

    def test_fixed_incoterm_does_not_query_or_report(self) -> None:
        issues = IssueLog()

        value = self._resolve("fob", None, {}, issues)

        self.assertEqual(5, value)
        self.assertEqual([], issues.items)

    def test_valid_lookup_returns_transit_days(self) -> None:
        issues = IssueLog()
        index = _build_transit_index(
            [_transit_row(20)], self.source, issues
        )

        value = self._resolve("CIF", "日本", index, issues)

        self.assertEqual(20, value)
        self.assertEqual([], issues.items)

    def test_missing_country_reports_specific_reason(self) -> None:
        issues = IssueLog()

        value = self._resolve("CIF", None, {}, issues)

        self.assertIsNone(value)
        self.assertEqual("TRANSIT_COUNTRY_MISSING", issues.items[0].code)
        self.assertEqual(
            "缺少国家，无法匹配国家运输周期表",
            issues.items[0].message,
        )
        self.assertEqual("C001 | SC-C", issues.items[0].business_key)
        self.assertEqual("Sheet2", issues.items[0].sheet)

    def test_missing_pair_reports_lookup_key(self) -> None:
        issues = IssueLog()

        value = self._resolve("CIF", "日本", {}, issues)

        self.assertIsNone(value)
        issue = issues.items[0]
        self.assertEqual("TRANSIT_NOT_FOUND", issue.code)
        self.assertEqual(
            "国家运输周期表无对应组合：日本 + SC-C", issue.message
        )
        self.assertEqual("transit.xlsx", issue.workbook)
        self.assertEqual("Sheet3", issue.sheet)

    def test_blank_or_value_pair_reports_unavailable(self) -> None:
        for raw in (None, "#VALUE!"):
            with self.subTest(raw=raw):
                issues = IssueLog()
                index = _build_transit_index(
                    [_transit_row(None, raw=raw)], self.source, issues
                )

                value = self._resolve("CIF", "日本", index, issues)

                self.assertIsNone(value)
                self.assertEqual(1, len(issues.items))
                issue = issues.items[0]
                self.assertEqual("TRANSIT_VALUE_UNAVAILABLE", issue.code)
                self.assertEqual(3, issue.row_number)
                self.assertIn("SC-C", issue.raw_value)

    def test_invalid_nonblank_value_reports_once_with_business_key(self) -> None:
        issues = IssueLog()
        index = _build_transit_index(
            [_transit_row(None, raw="bad", invalid=True)],
            self.source,
            issues,
        )

        value = self._resolve("CIF", "日本", index, issues)

        self.assertIsNone(value)
        self.assertEqual(1, len(issues.items))
        issue = issues.items[0]
        self.assertEqual("INVALID_TRANSIT_DAYS", issue.code)
        self.assertEqual("C001 | SC-C", issue.business_key)
        self.assertEqual("transit.xlsx", issue.workbook)
        self.assertEqual("Sheet3", issue.sheet)
        self.assertEqual(3, issue.row_number)
        self.assertIn("transit_days=bad", issue.raw_value)

    def _resolve(self, incoterm, country, index, issues):
        return _resolve_transit_days(
            incoterm=incoterm,
            country=country,
            supply_center="SC-C",
            fixed_transit=self.fixed,
            transit_index=index,
            source=self.source,
            issues=issues,
            business_key="C001 | SC-C",
        )


def _transit_row(
    value: int | None,
    *,
    raw=None,
    invalid: bool = False,
) -> ParsedRow:
    return ParsedRow(
        role="transit",
        workbook="transit.xlsx",
        sheet="Sheet3",
        row_number=3,
        values={
            "country": "日本",
            "supply_center": "SC-C",
            "transit_days": value,
        },
        raw_values={
            "country": "日本",
            "supply_center": "SC-C",
            "transit_days": raw if raw is not None else value,
        },
        invalid_fields=(
            frozenset({"transit_days"}) if invalid else frozenset()
        ),
    )


if __name__ == "__main__":
    unittest.main()
