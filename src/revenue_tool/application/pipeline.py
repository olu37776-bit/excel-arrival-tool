from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from revenue_tool.adapters.excel_reader import ExcelInputAdapter
from revenue_tool.adapters.excel_writer import ExcelOutputAdapter
from revenue_tool.adapters.previous_result_reader import PreviousResultReader
from revenue_tool.config import ToolConfig, load_config
from revenue_tool.domain.models import IssueLog, PipelineResult, SourceData, SourceFiles
from revenue_tool.domain.revenue_models import (
    CANDIDATE_ID_VERSION,
    PROJECTION_FINGERPRINT_VERSION,
    PreviousRunState,
    RevenuePhase1Models,
)
from revenue_tool.services.allocation import AllocationService
from revenue_tool.services.allocation_candidates import AllocationCandidateBuilder
from revenue_tool.services.candidate_history import CandidateHistoryService
from revenue_tool.services.comparison import (
    build_supply_pull_rows,
    compare_revenue_months,
)
from revenue_tool.services.contract_finance import ContractFactBuilder
from revenue_tool.services.data_quality import DataQualityAnalyzer
from revenue_tool.services.demand_records import DemandRecordService
from revenue_tool.services.fulfillment_projection import FulfillmentProjectionService
from revenue_tool.services.legacy_projection_adapter import LegacyProjectionAdapter
from revenue_tool.services.monthly_revenue import MonthlyRevenueService
from revenue_tool.services.normalization import ZERO_AMOUNT
from revenue_tool.services.previous_run_state import previous_state_to_previous_data
from revenue_tool.services.revenue_datasets import RevenueDatasetBuilder


METADATA_SCHEMA_VERSION = "4"
RULES_VERSION = "revenue-allocation-v3"


def build_phase1_models(
    source: SourceData,
    config: ToolConfig,
    issues: IssueLog,
) -> RevenuePhase1Models:
    """Build the frozen Phase 1 facts and fulfillment projections."""

    contract_facts = ContractFactBuilder().build(source, config)
    demand_records = DemandRecordService().build(source.rows["demand_detail"])
    fulfillment_projections = FulfillmentProjectionService().build(
        contract_facts,
        demand_records,
        source,
        config,
        issues,
    )
    return RevenuePhase1Models(
        contract_facts=tuple(contract_facts),
        demand_records=tuple(demand_records),
        fulfillment_projections=tuple(fulfillment_projections),
    )


def run_pipeline(
    legacy_path: str | Path,
    monthly_order_path: str | Path | None,
    demand_detail_path: str | Path,
    transit_path: str | Path,
    output_path: str | Path,
    config_path: str | Path,
    previous_path: str | Path | None = None,
) -> PipelineResult:
    source_files = SourceFiles(
        legacy=Path(legacy_path),
        monthly_order=Path(monthly_order_path) if monthly_order_path else None,
        demand_detail=Path(demand_detail_path),
        transit=Path(transit_path),
    )
    _validate_paths(source_files, output_path, previous_path)
    config = load_config(config_path)
    issues = IssueLog()
    source = ExcelInputAdapter().read_source(source_files, config, issues)
    DataQualityAnalyzer().analyze(source, issues)
    phase1 = build_phase1_models(source, config, issues)

    previous = (
        PreviousResultReader().read(previous_path, config, issues)
        if previous_path
        else PreviousRunState.empty()
    )
    candidates = AllocationCandidateBuilder().build(
        phase1.fulfillment_projections, issues
    )
    history = CandidateHistoryService().apply(
        candidates, list(phase1.contract_facts), previous, issues
    )
    decisions, allocation_summaries = AllocationService().allocate(
        list(phase1.contract_facts), list(history.candidates), issues
    )
    (
        postings,
        rpd_summary,
        cpd_summary,
        pending,
        allocation_summaries,
    ) = MonthlyRevenueService().build(
        list(phase1.contract_facts),
        list(history.candidates),
        decisions,
        allocation_summaries,
        list(history.orphaned_allocations),
    )

    comparable_rows = LegacyProjectionAdapter().to_base_rows(
        phase1.contract_facts, phase1.fulfillment_projections
    )
    previous_data = previous_state_to_previous_data(previous)
    if previous.usable_for_projection_comparison:
        rpd_changes = compare_revenue_months(
            comparable_rows,
            previous_data,
            "rpd",
            source.workbook_for("demand_detail").name,
            issues,
        )
        cpd_changes = compare_revenue_months(
            comparable_rows,
            previous_data,
            "cpd",
            source.workbook_for("demand_detail").name,
            issues,
        )
    else:
        rpd_changes = []
        cpd_changes = []
    supply_pull = build_supply_pull_rows(
        comparable_rows,
        source.workbook_for("demand_detail").name,
        issues,
    )

    datasets = RevenueDatasetBuilder().build(
        facts=list(phase1.contract_facts),
        records=list(phase1.demand_records),
        projections=list(phase1.fulfillment_projections),
        candidates=list(history.candidates),
        decisions=decisions,
        summaries=allocation_summaries,
        postings=postings,
        rpd_summary=rpd_summary,
        cpd_summary=cpd_summary,
        pending=pending,
        rpd_changes=rpd_changes,
        cpd_changes=cpd_changes,
        supply_pull=supply_pull,
        issues=issues,
    )
    run_id = str(uuid4())
    metadata = {
        "schema_version": METADATA_SCHEMA_VERSION,
        "run_id": run_id,
        "rules_version": RULES_VERSION,
        "candidate_id_version": CANDIDATE_ID_VERSION,
        "projection_fingerprint_version": PROJECTION_FINGERPRINT_VERSION,
        "amount_precision": "0.01",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file_fingerprints": _source_fingerprints(source_files),
    }
    written = ExcelOutputAdapter().write(
        output_path, datasets, config, metadata
    )
    return PipelineResult(
        output_path=written,
        contract_count=len(phase1.contract_facts),
        candidate_count=len(history.candidates),
        allocated_amount=sum(
            (item.allocated_amount for item in allocation_summaries),
            ZERO_AMOUNT,
        ),
        unallocated_amount=sum(
            (item.unallocated_amount for item in allocation_summaries),
            ZERO_AMOUNT,
        ),
        rpd_posted_amount=sum(
            (item.rpd_posted_amount for item in allocation_summaries),
            ZERO_AMOUNT,
        ),
        cpd_posted_amount=sum(
            (item.cpd_posted_amount for item in allocation_summaries),
            ZERO_AMOUNT,
        ),
        pending_count=len(pending),
        rpd_change_count=len(rpd_changes),
        cpd_change_count=len(cpd_changes),
        supply_pull_count=len(supply_pull),
        issue_count=len(issues.items),
    )


def _validate_paths(
    source_files: SourceFiles,
    output_path: str | Path,
    previous_path: str | Path | None,
) -> None:
    source_resolved = {
        role: path.resolve()
        for role, path in source_files.as_dict().items()
        if path is not None
    }
    if len(set(source_resolved.values())) != len(source_resolved):
        raise ValueError("已选择的源文件必须互相独立，不能重复选择同一文件")
    output_resolved = Path(output_path).resolve()
    if output_resolved in source_resolved.values():
        raise ValueError("输出文件不能覆盖任何一个本次源文件")
    if previous_path is not None and Path(previous_path).resolve() == output_resolved:
        raise ValueError("输出文件不能覆盖上一次结果 / 已分配结果")


def _source_fingerprints(source_files: SourceFiles) -> dict[str, str]:
    result: dict[str, str] = {}
    for role, path in source_files.as_dict().items():
        if path is None:
            continue
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        result[role] = digest.hexdigest()
    return result
