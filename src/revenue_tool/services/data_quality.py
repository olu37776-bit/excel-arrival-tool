from __future__ import annotations

from collections import defaultdict
from typing import Any

from revenue_tool.domain.models import IssueLog, ParsedRow, SourceData
from revenue_tool.services.normalization import (
    nonblank,
    normalize_country_identity,
    normalize_lookup,
    normalize_text,
)


class DataQualityAnalyzer:
    """Report source-data risks without changing business calculations."""

    def analyze(
        self,
        source: SourceData,
        issues: IssueLog,
    ) -> None:
        self._log_country_conflicts(source, issues)
        self._log_control_flag_risks(source.rows["demand_detail"], issues)

    def _log_country_conflicts(
        self, source: SourceData, issues: IssueLog
    ) -> None:
        grouped: dict[str, list[ParsedRow]] = defaultdict(list)
        for role in ("legacy", "monthly_order", "demand_detail"):
            for row in source.rows[role]:
                contract = row.values.get("contract_no")
                if nonblank(contract):
                    grouped[str(contract)].append(row)
        for contract, rows in grouped.items():
            entries = _distinct_entries(rows, "country")
            if len(entries) <= 1:
                continue
            issues.add(
                "CONFLICTING_COUNTRY_FOR_CONTRACT",
                "同一合同在源数据中出现多个不同国家；仍按字段优先级和源表首条继续",
                workbook=rows[0].workbook,
                business_key=contract,
                field="country",
                raw_value=" | ".join(
                    _source_value(row, value) for value, row in entries
                ),
            )

    def _log_control_flag_risks(
        self, rows: list[ParsedRow], issues: IssueLog
    ) -> None:
        for row in rows:
            stock = row.values.get("stock_control_flag")
            shipment = row.values.get("shipment_control_flag")
            if (
                stock in {"Y", "N"}
                and shipment in {"Y", "N"}
                and stock != shipment
            ):
                contract = str(row.values.get("contract_no") or "")
                center = str(row.values.get("supply_center") or "")
                issues.add(
                    "CONTROL_FLAG_MISMATCH",
                    "同一要货明细记录的备货总控标识与发货总控标识不同步",
                    workbook=row.workbook,
                    sheet=row.sheet,
                    row_number=row.row_number,
                    business_key=f"{contract} | {center}",
                    field="stock_control_flag+shipment_control_flag",
                    raw_value=f"{stock} | {shipment}",
                )

def _distinct_entries(
    rows: list[ParsedRow], field: str
) -> list[tuple[Any, ParsedRow]]:
    result: list[tuple[Any, ParsedRow]] = []
    identities: set[str] = set()
    for row in rows:
        value = row.values.get(field)
        if not nonblank(value):
            continue
        identity = (
            normalize_country_identity(value)
            if field == "country"
            else normalize_lookup(value)
        )
        if identity in identities:
            continue
        identities.add(identity)
        result.append((value, row))
    return result


def _source_value(row: ParsedRow, value: Any) -> str:
    return (
        f"{row.workbook}/{row.sheet}!{row.row_number}="
        f"{normalize_text(value)}"
    )
