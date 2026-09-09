"""Fixtures for Microsoft's independent schema/semantic package validator."""
from decimal import Decimal
from pathlib import Path
import sys

from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import BaseRow, IssueLog
from revenue_tool.services.final_revenue import calculate_final_values
from tests.test_pipeline import CONFIG, _run, _write_sources


def example_rows():
    """Independent edge rows for writer/package validation."""
    data = [
        ("A1", "A", "2026-08", "2026-09", "订未发", 100),
        ("A2", "A", "2026-09", "2026-08", "订未发", 20),
        ("A3", "A", "2026-09", "2026-09", "发未收", -5),
        ("A4", "A", "2026-09", "2026-09", "交未验", 0),
        ("A5", "A", "2026-09", "2026-09", "特殊处理", 7),
        ("NONE", "A", None, None, "订未发", 700),
        ("B2", "B", "2026-09", "2026-09", False, 3),
        ("EMPTY", None, "2026-09", "2026-09", "订未发", 4),
    ]
    result = []
    for contract, region, rpd, cpd, segment, amount in data:
        values = dict(
            contract_no=contract,
            supply_center="深供",
            region=region,
            revenue_month_rpd=rpd,
            revenue_month_cpd=cpd,
            revenue_segment=segment,
            revenue_forecast=Decimal(amount),
        )
        values.update(calculate_final_values(values))
        result.append(BaseRow(values))
    return result


def main():
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    source_dir = root / 'inputs'
    source_dir.mkdir(exist_ok=True)
    sources = _write_sources(source_dir, 'source', variant='first')
    _run(sources, root / 'pipeline.xlsx')
    config = load_config(CONFIG)
    for name, rows in [('edge-cases', example_rows()), ('empty', [])]:
        ExcelOutputAdapter().write(
            root / f'{name}.xlsx', rows, [], [], [], IssueLog(), config
        )


if __name__ == '__main__':
    main()
