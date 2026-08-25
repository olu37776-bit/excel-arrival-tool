from __future__ import annotations

from pathlib import Path

from revenue_tool.adapters.excel_reader import ExcelInputAdapter
from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import (
    IssueLog,
    PipelineResult,
    PreviousData,
)
from revenue_tool.services.calculation import RevenueEngine
from revenue_tool.services.comparison import compare_revenue_months


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    config_path: str | Path,
    previous_path: str | Path | None = None,
) -> PipelineResult:
    input_resolved = Path(input_path).resolve()
    output_resolved = Path(output_path).resolve()
    if input_resolved == output_resolved:
        raise ValueError("输出文件不能与本次输入工作簿相同")
    if (
        previous_path is not None
        and Path(previous_path).resolve() == output_resolved
    ):
        raise ValueError("输出文件不能覆盖上一次成功运行结果")
    config = load_config(config_path)
    issues = IssueLog()
    reader = ExcelInputAdapter()
    source = reader.read_source(input_path, config, issues)
    previous = (
        reader.read_previous(previous_path, config, issues)
        if previous_path
        else PreviousData({}, usable=False)
    )
    base_rows = RevenueEngine().calculate(
        source, previous, config, issues
    )
    if previous_path and previous.usable:
        rpd_changes = compare_revenue_months(
            base_rows,
            previous,
            "rpd",
            source.workbook.name,
            issues,
        )
        cpd_changes = compare_revenue_months(
            base_rows,
            previous,
            "cpd",
            source.workbook.name,
            issues,
        )
    else:
        rpd_changes = []
        cpd_changes = []
    written = ExcelOutputAdapter().write(
        output_path,
        base_rows,
        rpd_changes,
        cpd_changes,
        issues,
        config,
    )
    return PipelineResult(
        output_path=written,
        base_count=len(base_rows),
        rpd_change_count=len(rpd_changes),
        cpd_change_count=len(cpd_changes),
        issue_count=len(issues.items),
    )
