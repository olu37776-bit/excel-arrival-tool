from decimal import Decimal
from pathlib import Path
import unittest

from revenue_tool.config import load_config
from revenue_tool.domain.models import HAS_DEMAND, NO_DEMAND, ParsedRow, SourceData
from revenue_tool.services.contract_finance import ContractFactBuilder


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


class ContractFactBuilderTest(unittest.TestCase):
    def test_one_fact_per_contract_and_forecast_is_exact(self) -> None:
        source = _source(
            legacy=[
                _row("legacy", 2, "C1", legacy_amount=Decimal("10.01")),
                _row("legacy", 3, "C2", legacy_amount=Decimal("-2.50")),
                _row("legacy", 4, "C3", legacy_amount=Decimal("0.00")),
            ],
            monthly=[
                _row(
                    "monthly_order",
                    2,
                    "C1",
                    monthly_new_order=Decimal("0.01"),
                ),
                _row(
                    "monthly_order",
                    3,
                    "C2",
                    monthly_new_order=Decimal("1.25"),
                ),
            ],
            demand=[
                _row("demand_detail", 2, "C1", supply_center="SC-A"),
                _row("demand_detail", 3, "C1", supply_center="SC-B"),
                _row("demand_detail", 4, "C3", supply_center="SC-C"),
            ],
        )

        facts = ContractFactBuilder().build(source, CONFIG)

        self.assertEqual(["C1", "C2", "C3"], [item.contract_no for item in facts])
        by_contract = {item.contract_no: item for item in facts}
        self.assertEqual(Decimal("10.02"), by_contract["C1"].revenue_forecast)
        self.assertEqual(Decimal("-1.25"), by_contract["C2"].revenue_forecast)
        self.assertEqual(Decimal("0.00"), by_contract["C3"].revenue_forecast)
        self.assertEqual(HAS_DEMAND, by_contract["C1"].demand_state)
        self.assertEqual(NO_DEMAND, by_contract["C2"].demand_state)

    def test_monthly_source_absent_and_contract_without_monthly_match(self) -> None:
        legacy = [
            _row("legacy", 2, "C1", legacy_amount=Decimal("8.00")),
            _row("legacy", 3, "C2", legacy_amount=Decimal("9.00")),
        ]
        demand = [
            _row("demand_detail", 2, "C1", supply_center="SC-A"),
            _row("demand_detail", 3, "C2", supply_center="SC-B"),
        ]

        absent = ContractFactBuilder().build(
            _source(legacy=legacy, monthly=[], demand=demand), CONFIG
        )
        unmatched = ContractFactBuilder().build(
            _source(
                legacy=legacy,
                monthly=[
                    _row(
                        "monthly_order",
                        2,
                        "C9",
                        monthly_new_order=Decimal("3.00"),
                    )
                ],
                demand=demand,
            ),
            CONFIG,
        )

        self.assertTrue(
            all(item.monthly_new_order == Decimal("0.00") for item in absent)
        )
        by_contract = {item.contract_no: item for item in unmatched}
        self.assertEqual(Decimal("0.00"), by_contract["C1"].monthly_new_order)
        self.assertEqual(Decimal("0.00"), by_contract["C2"].monthly_new_order)
        self.assertEqual(Decimal("3.00"), by_contract["C9"].monthly_new_order)

    def test_multiple_centers_do_not_duplicate_financial_fact(self) -> None:
        source = _source(
            legacy=[
                _row("legacy", 2, "C1", legacy_amount=Decimal("100.00"))
            ],
            monthly=[],
            demand=[
                _row("demand_detail", 2, "C1", supply_center="SC-A"),
                _row("demand_detail", 3, "C1", supply_center="SC-B"),
                _row("demand_detail", 4, "C1", supply_center="SC-A"),
            ],
        )

        facts = ContractFactBuilder().build(source, CONFIG)

        self.assertEqual(1, len(facts))
        self.assertEqual(Decimal("100.00"), facts[0].revenue_forecast)

    def test_issue_20_uses_resolved_demand_country_for_all_seven(self) -> None:
        legacy = []
        demand = []
        for index, country in enumerate(COUNTRIES, start=1):
            contract = f"C{index}"
            legacy.append(
                _row(
                    "legacy",
                    index + 1,
                    contract,
                    country=None,
                    legacy_amount=Decimal("1.00"),
                )
            )
            demand.append(
                _row(
                    "demand_detail",
                    index + 1,
                    contract,
                    country=f" \u3000{country}\n",
                    supply_center=f"SC-{index}",
                )
            )
        legacy.append(
            _row(
                "legacy",
                20,
                "OTHER",
                country=None,
                legacy_amount=Decimal("1.00"),
            )
        )
        demand.append(
            _row(
                "demand_detail",
                20,
                "OTHER",
                country="日本",
                supply_center="SC-X",
            )
        )

        facts = ContractFactBuilder().build(
            _source(legacy=legacy, monthly=[], demand=demand), CONFIG
        )
        by_contract = {item.contract_no: item for item in facts}

        for index, country in enumerate(COUNTRIES, start=1):
            with self.subTest(country=country):
                fact = by_contract[f"C{index}"]
                self.assertEqual(f" \u3000{country}\n", fact.country)
                self.assertEqual("交付类", fact.carryover_type)
        self.assertIsNone(by_contract["OTHER"].carryover_type)

    def test_no_demand_contract_still_has_financial_fact(self) -> None:
        facts = ContractFactBuilder().build(
            _source(
                legacy=[
                    _row(
                        "legacy",
                        2,
                        "C1",
                        legacy_amount=Decimal("5.00"),
                    )
                ],
                monthly=[],
                demand=[],
            ),
            CONFIG,
        )

        self.assertEqual(1, len(facts))
        self.assertEqual(NO_DEMAND, facts[0].demand_state)


def _source(*, legacy, monthly, demand) -> SourceData:
    return SourceData(
        {
            "legacy": Path("legacy.xlsx"),
            "demand_detail": Path("demand.xlsx"),
            "transit": Path("transit.xlsx"),
        },
        {
            "legacy": legacy,
            "monthly_order": monthly,
            "demand_detail": demand,
            "transit": [],
        },
        {
            "legacy": "Sheet1",
            "demand_detail": "Sheet1",
            "transit": "Sheet1",
        },
    )


def _row(role: str, row_number: int, contract_no: str, **overrides) -> ParsedRow:
    values = {field: None for field in CONFIG.fields[role]}
    values["contract_no"] = contract_no
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
