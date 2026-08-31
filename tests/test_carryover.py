from pathlib import Path
import unittest

from revenue_tool.config import load_config
from revenue_tool.domain.models import (
    IssueLog,
    ParsedRow,
    PreviousData,
    SourceData,
)
from revenue_tool.services.calculation import RevenueEngine
from revenue_tool.services.normalization import (
    canonical_country_identity,
    normalize_country_identity,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config(ROOT / "config" / "default.json")
COUNTRIES = [
    "阿拉伯联合酋长国",
    "巴基斯坦",
    "巴西",
    "菲律宾",
    "马来西亚",
    "沙特阿拉伯",
    "印度尼西亚",
]


class CarryoverCountryTest(unittest.TestCase):
    def test_all_seven_canonical_countries_are_delivery_carryover(self) -> None:
        rows = _calculate(COUNTRIES, COUNTRIES)

        self.assertEqual(7, len(rows))
        self.assertTrue(
            all(row.values["carryover_type"] == "交付类" for row in rows)
        )

    def test_country_identity_removes_whitespace_and_format_controls(self) -> None:
        variants = [
            "  阿拉伯联合酋长国\n",
            "　沙特阿拉伯　",
            "阿拉伯\t联合酋长国",
            "沙特\u200b阿拉伯",
            "印度尼西\ufeff亚",
        ]

        for value in variants:
            with self.subTest(value=repr(value)):
                self.assertIn(
                    normalize_country_identity(value),
                    {
                        normalize_country_identity(country)
                        for country in COUNTRIES
                    },
                )

        rows = _calculate(variants, variants)
        self.assertTrue(
            all(row.values["carryover_type"] == "交付类" for row in rows)
        )

        fallback_rows = _calculate([None] * len(variants), variants)
        self.assertTrue(
            all(
                row.values["carryover_type"] == "交付类"
                for row in fallback_rows
            )
        )

    def test_nonlisted_country_does_not_match(self) -> None:
        rows = _calculate(["日本"], ["日本"])

        self.assertIsNone(rows[0].values["carryover_type"])

    def test_carryover_uses_resolved_demand_country_fallback(self) -> None:
        rows = _calculate([None] * len(COUNTRIES), COUNTRIES)

        self.assertEqual(COUNTRIES, [row.values["country"] for row in rows])
        self.assertTrue(
            all(row.values["carryover_type"] == "交付类" for row in rows)
        )

    def test_indonesia_business_alias_is_explicitly_canonicalized(self) -> None:
        raw = "印度尼西亚（印尼）"
        normalized_aliases = {
            normalize_country_identity(alias): normalize_country_identity(
                canonical
            )
            for alias, canonical in CONFIG.rules["country_aliases"].items()
        }

        self.assertEqual("印度尼西亚(印尼)", normalize_country_identity(raw))
        self.assertEqual(
            "印度尼西亚",
            canonical_country_identity(raw, normalized_aliases),
        )

        legacy_priority = _calculate([raw], ["日本"])[0]
        self.assertEqual(raw, legacy_priority.values["country"])
        self.assertEqual("交付类", legacy_priority.values["carryover_type"])

        demand_fallback = _calculate([None], [raw])[0]
        self.assertEqual(raw, demand_fallback.values["country"])
        self.assertEqual("交付类", demand_fallback.values["carryover_type"])

    def test_country_aliases_do_not_enable_fuzzy_matching(self) -> None:
        rows = _calculate(["印度尼西亚洲"], ["印度尼西亚"])

        self.assertIsNone(rows[0].values["carryover_type"])


def _calculate(
    legacy_countries: list[str | None], demand_countries: list[str]
):
    legacy_rows = []
    demand_rows = []
    for index, (legacy_country, demand_country) in enumerate(
        zip(legacy_countries, demand_countries), start=1
    ):
        contract = f"C{index:03d}"
        legacy_rows.append(
            _row(
                "legacy",
                index + 1,
                {
                    "contract_no": contract,
                    "country": legacy_country,
                    "legacy_amount": 0,
                },
            )
        )
        demand_rows.append(
            _row(
                "demand_detail",
                index + 1,
                {
                    "contract_no": contract,
                    "country": demand_country,
                    "supply_center": f"SC-{index}",
                    "incoterm": "EXW",
                },
            )
        )
    source = SourceData(
        {
            "legacy": Path("legacy.xlsx"),
            "demand_detail": Path("demand.xlsx"),
            "transit": Path("transit.xlsx"),
        },
        {
            "legacy": legacy_rows,
            "monthly_order": [],
            "demand_detail": demand_rows,
            "transit": [],
        },
        {
            "legacy": "Sheet1",
            "demand_detail": "Sheet1",
            "transit": "Sheet1",
        },
    )
    return RevenueEngine().calculate(
        source,
        PreviousData({}, usable=False),
        CONFIG,
        IssueLog(),
    )


def _row(role: str, row_number: int, overrides: dict[str, object]) -> ParsedRow:
    values = {
        field: None for field in CONFIG.fields[role]
    }
    values.update(overrides)
    return ParsedRow(
        role=role,
        workbook=f"{role}.xlsx",
        sheet="Sheet1",
        row_number=row_number,
        values=values,
        raw_values=dict(values),
    )


if __name__ == "__main__":
    unittest.main()
