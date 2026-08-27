from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import HAS_DEMAND, NO_DEMAND, ParsedRow, SourceData
from revenue_tool.domain.revenue_models import ContractFinancialFact
from revenue_tool.services.normalization import (
    ZERO_AMOUNT,
    nonblank,
    normalize_country_identity,
    normalize_lookup,
)


class ContractFactBuilder:
    """Build exactly one authoritative financial fact for every contract."""

    def __init__(self, *, legacy_carryover_compat: bool = False) -> None:
        self._legacy_carryover_compat = legacy_carryover_compat

    def build(
        self,
        source: SourceData,
        config: ToolConfig,
    ) -> list[ContractFinancialFact]:
        legacy_rows = _valid_contract_rows(source.rows["legacy"])
        monthly_rows = _valid_contract_rows(source.rows["monthly_order"])
        demand_rows = _valid_contract_rows(source.rows["demand_detail"])

        legacy_first = _first_contract_rows(legacy_rows)
        monthly_first = _first_contract_rows(monthly_rows)
        demand_first = _first_contract_rows(demand_rows)
        demand_counts: dict[str, int] = defaultdict(int)
        for row in demand_rows:
            demand_counts[str(row.values["contract_no"])] += 1

        carryover_countries = {
            normalize_country_identity(value)
            for value in config.rules["carryover_countries"]
        }
        contracts = {
            str(row.values["contract_no"])
            for row in legacy_rows + monthly_rows + demand_rows
        }
        result: list[ContractFinancialFact] = []
        for contract in sorted(contracts, key=normalize_lookup):
            legacy = legacy_first.get(contract)
            monthly = monthly_first.get(contract)
            demand = demand_first.get(contract)
            legacy_amount = _amount_value(legacy, "legacy_amount")
            monthly_new_order = _amount_value(
                monthly, "monthly_new_order"
            )
            legacy_country = _value(legacy, "country")
            resolved_country = _fallback(
                legacy_country,
                _value(demand, "country"),
            )
            carryover_country = (
                legacy_country
                if self._legacy_carryover_compat
                else resolved_country
            )
            result.append(
                ContractFinancialFact(
                    contract_no=contract,
                    legacy_amount=legacy_amount,
                    monthly_new_order=monthly_new_order,
                    revenue_forecast=legacy_amount + monthly_new_order,
                    bg=_fallback(
                        _value(legacy, "bg"),
                        _value(monthly, "bg"),
                        _value(demand, "bg"),
                    ),
                    region=_fallback(
                        _value(legacy, "region"),
                        _value(demand, "region"),
                    ),
                    country=resolved_country,
                    carryover_type=(
                        "交付类"
                        if normalize_country_identity(carryover_country)
                        in carryover_countries
                        else None
                    ),
                    customer_group=_fallback(
                        _value(legacy, "customer_group"),
                        _value(demand, "customer_group"),
                    ),
                    project_name=_fallback(
                        _value(legacy, "project_name"),
                        _value(demand, "project_name"),
                    ),
                    demand_state=(
                        HAS_DEMAND if demand_counts[contract] else NO_DEMAND
                    ),
                )
            )
        return result


def contract_fact_to_legacy_values(
    fact: ContractFinancialFact,
) -> dict[str, Any]:
    """Expose only the contract fields consumed by the v0.8 BaseRow path."""

    return {
        "contract_no": fact.contract_no,
        "legacy_amount": fact.legacy_amount,
        "monthly_new_order": fact.monthly_new_order,
        "bg": fact.bg,
        "region": fact.region,
        "country": fact.country,
        "carryover_type": fact.carryover_type,
        "customer_group": fact.customer_group,
        "project_name": fact.project_name,
    }


def _valid_contract_rows(rows: list[ParsedRow]) -> list[ParsedRow]:
    return [row for row in rows if nonblank(row.values.get("contract_no"))]


def _first_contract_rows(
    rows: list[ParsedRow],
) -> dict[str, ParsedRow]:
    result: dict[str, ParsedRow] = {}
    for row in rows:
        contract = str(row.values["contract_no"])
        result.setdefault(contract, row)
    return result


def _fallback(*values: Any) -> Any:
    for value in values:
        if nonblank(value):
            return value
    return None


def _value(row: ParsedRow | None, field: str) -> Any:
    return row.values.get(field) if row is not None else None


def _amount_value(row: ParsedRow | None, field: str) -> Decimal:
    value = _value(row, field)
    return value if isinstance(value, Decimal) else ZERO_AMOUNT
