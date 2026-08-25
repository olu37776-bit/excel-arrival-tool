from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    severity: str = "WARNING"
    workbook: str = ""
    sheet: str = ""
    row_number: int | None = None
    business_key: str = ""
    field: str = ""
    raw_value: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "workbook": self.workbook,
            "sheet": self.sheet,
            "row_number": self.row_number,
            "business_key": self.business_key,
            "field": self.field,
            "raw_value": self.raw_value,
            "message": self.message,
        }


@dataclass
class IssueLog:
    items: list[Issue] = field(default_factory=list)

    def add(self, code: str, message: str, **context: Any) -> None:
        self.items.append(Issue(code=code, message=message, **context))


@dataclass(frozen=True)
class ParsedRow:
    role: str
    sheet: str
    row_number: int
    values: dict[str, Any]
    raw_values: dict[str, Any]
    invalid_fields: frozenset[str] = frozenset()


@dataclass
class SourceData:
    workbook: Path
    rows: dict[str, list[ParsedRow]]
    sheet_names: dict[str, str]


@dataclass
class BaseRow:
    values: dict[str, Any]


@dataclass
class PreviousData:
    rows: dict[tuple[str, str], BaseRow]
    usable: bool = True


@dataclass
class ComparisonRow:
    values: dict[str, Any]


@dataclass(frozen=True)
class PipelineResult:
    output_path: Path
    base_count: int
    rpd_change_count: int
    cpd_change_count: int
    issue_count: int


class WorkbookReadError(RuntimeError):
    """输入工作簿完全无法读取时抛出。"""
