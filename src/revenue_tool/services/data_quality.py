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
