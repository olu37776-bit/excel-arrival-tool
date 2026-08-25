from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from revenue_tool.adapters.excel_input import ExcelInputAdapter
from revenue_tool.adapters.excel_output import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.rules.grouping import PrdSelectionRule, ShipmentGroupingRule
from revenue_tool.rules.transit import TransitDaysResolver
from revenue_tool.services.calculation import RevenueCalculator, summarise
from revenue_tool.services.comparison import compare_revenue_months


@dataclass(frozen=True)
class RunResult:
    revenue_detail_count: int
    revenue_summary_count: int
    delayed_count: int
    output_path: Path


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    config_dir: str | Path,
    previous_path: str | Path | None = None,
) -> RunResult:
    config = load_config(config_dir)
    input_adapter = ExcelInputAdapter()
    output_adapter = ExcelOutputAdapter()
    data = input_adapter.read(input_path, config)

    grouping = config.rules["grouping"]
    prd_rules = config.rules["prd"]
    transit_rules = config.rules["transit"]
    comparison_rules = config.rules["comparison"]

    calculator = RevenueCalculator(
        ShipmentGroupingRule(
            same_fields=grouping["required_same_fields"],
            quantity_aggregation=grouping.get("quantity_aggregation", "max"),
            revenue_amount_aggregation=grouping.get(
                "revenue_amount_aggregation", "max"
            ),
        ),
        PrdSelectionRule(
            date_aggregation=prd_rules.get("date_aggregation", "min"),
            quantity_aggregation=prd_rules.get(
                "original_po_quantity_aggregation", "max"
            ),
        ),
        TransitDaysResolver(
            rules=data.transit_rules,
            adjustments=transit_rules.get("trade_type_adjustments", {}),
            unknown_trade_type=transit_rules.get("unknown_trade_type", "error"),
            default_days=transit_rules.get("default_days", 0),
        ),
    )
    details = calculator.calculate(data.prd_rows, data.shipment_rows)
    summary = summarise(details)
    previous = input_adapter.read_previous(previous_path) if previous_path else []
    comparison = compare_revenue_months(
        details,
        previous,
        delay_threshold_months=int(
            comparison_rules.get("delay_threshold_months", 1)
        ),
        only_delayed=bool(comparison_rules.get("only_delayed", True)),
    )
    output_adapter.write(
        output_path,
        summary,
        details,
        comparison,
        source_file=str(Path(input_path)),
        previous_file=str(Path(previous_path)) if previous_path else None,
    )
    return RunResult(
        revenue_detail_count=len(details),
        revenue_summary_count=len(summary),
        delayed_count=sum(row.delayed for row in comparison),
        output_path=Path(output_path),
    )

