from __future__ import annotations

from pathlib import Path

from revenue_tool.adapters.excel_reader import ExcelInputAdapter
from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.config import load_config
from revenue_tool.domain.models import (
    IssueLog,
    PipelineResult,
    PreviousData,
    SourceFiles,
)
from revenue_tool.services.calculation import RevenueEngine
from revenue_tool.services.comparison import (
    build_supply_pull_rows,
    compare_revenue_months,
)
from revenue_tool.services.data_quality import DataQualityAnalyzer


def run_pipeline(
    legacy_path: str | Path,
    monthly_order_path: str | Path,
    demand_detail_path: str | Path,
    transit_path: str | Path,
    output_path: str | Path,
    config_path: str | Path,
    previous_path: str | Path | None = None,
) -> PipelineResult:
    source_files = SourceFiles(
        legacy=Path(legacy_path),
        monthly_order=Path(monthly_order_path),
        demand_detail=Path(demand_detail_path),
        transit=Path(transit_path),
    )
    source_resolved = {
        role: path.resolve()
        for role, path in source_files.as_dict().items()
    }
    if len(set(source_resolved.values())) != len(source_resolved):
        raise ValueError("四个源文件必须互相独立，不能重复选择同一文件")
    output_resolved = Path(output_path).resolve()
    if output_resolved in source_resolved.values():
        raise ValueError("输出文件不能覆盖任何一个本次源文件")
    if (
        previous_path is not None
        and Path(previous_path).resolve() == output_resolved
    ):
        raise ValueError("输出文件不能覆盖上一次成功运行结果")
    config = load_config(config_path)
    issues = IssueLog()
    reader = ExcelInputAdapter()
    source = reader.read_source(source_files, config, issues)
    DataQualityAnalyzer().analyze(source, issues)
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
            source.workbook_for("demand_detail").name,
            issues,
        )
        cpd_changes = compare_revenue_months(
            base_rows,
            previous,
            "cpd",
            source.workbook_for("demand_detail").name,
            issues,
        )
    else:
        rpd_changes = []
        cpd_changes = []
    supply_pull_rows = build_supply_pull_rows(
        base_rows,
        source.workbook_for("demand_detail").name,
        issues,
    )
    written = ExcelOutputAdapter().write(
        output_path,
        base_rows,
        rpd_changes,
        cpd_changes,
        supply_pull_rows,
        issues,
        config,
    )
    return PipelineResult(
        output_path=written,
        base_count=len(base_rows),
        rpd_change_count=len(rpd_changes),
        cpd_change_count=len(cpd_changes),
        supply_pull_count=len(supply_pull_rows),
        issue_count=len(issues.items),
    )
