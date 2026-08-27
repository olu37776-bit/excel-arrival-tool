from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from revenue_tool.config import ToolConfig


_HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
_HEADER_FONT = Font(color="FFFFFF", bold=True)
_EDITABLE_FILL = PatternFill("solid", fgColor="FFF2CC")
_BANDED_FILL = PatternFill("solid", fgColor="D9EAF7")
_THIN_BLUE = Side(style="thin", color="9EADBF")
_REFERENCE_COMMENT = (
    "该列是合同级收入预测参考值，会在同合同的多个分配候选上重复显示。"
    "禁止直接对本列求和；合同金额汇总请使用“合同收入预测”Sheet。"
)


class ExcelOutputAdapter:
    """Render already-computed datasets without business-rule calculations."""

    def write(
        self,
        output_path: str | Path,
        datasets: dict[str, list[dict[str, Any]]],
        config: ToolConfig,
        metadata: dict[str, Any],
    ) -> Path:
        workbook = Workbook()
        workbook.remove(workbook.active)
        for dataset_id, spec in config.datasets.items():
            self._write_dataset_sheet(
                workbook,
                spec,
                datasets.get(dataset_id, []),
            )
        self._write_metadata_sheet(workbook, config, metadata)

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(path)
        workbook.close()
        return path

    def _write_dataset_sheet(
        self,
        workbook: Workbook,
        spec: dict[str, Any],
        rows: list[dict[str, Any]],
    ) -> None:
        sheet = workbook.create_sheet(spec["sheet"])
        sheet.sheet_view.showGridLines = False
        sheet.freeze_panes = "A2"
        columns = spec["columns"]
        field_ids = [column["id"] for column in columns]
        sheet.append([column["name"] for column in columns])
        for row in rows:
            sheet.append([_excel_value(row.get(field)) for field in field_ids])

        for cell in sheet[1]:
            cell.fill = _HEADER_FILL
            cell.font = _HEADER_FONT
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
            cell.border = Border(bottom=_THIN_BLUE)
        sheet.row_dimensions[1].height = 38

        for index, column in enumerate(columns, start=1):
            field_id = column["id"]
            column_type = column["type"]
            letter = get_column_letter(index)
            for cell in sheet[letter][1:]:
                cell.alignment = Alignment(
                    horizontal=(
                        "right"
                        if column_type in {"amount", "integer"}
                        else "center" if column_type == "date" else "left"
                    ),
                    vertical="top",
                    wrap_text=False,
                )
                if column_type == "amount":
                    cell.number_format = "#,##0.00;[Red]-#,##0.00"
                elif column_type == "integer":
                    cell.number_format = "0"
                elif column_type == "date":
                    cell.number_format = "yyyy-mm-dd"
                if column.get("editable"):
                    cell.fill = _EDITABLE_FILL

            if field_id == "contract_revenue_forecast_reference":
                sheet.cell(1, index).comment = Comment(
                    _REFERENCE_COMMENT, "Excel Revenue Tool"
                )

        for row_number in range(2, sheet.max_row + 1):
            if row_number % 2:
                continue
            for column_number, column in enumerate(columns, start=1):
                if not column.get("editable"):
                    sheet.cell(row_number, column_number).fill = _BANDED_FILL

        last_column = get_column_letter(len(columns))
        sheet.auto_filter.ref = f"A1:{last_column}{max(1, sheet.max_row)}"
        for index, column in enumerate(columns, start=1):
            values = [
                _display_value(row.get(column["id"])) for row in rows[:200]
            ]
            configured_width = column.get("width")
            width = (
                configured_width
                if isinstance(configured_width, (int, float))
                else min(
                    42,
                    max(
                        12,
                        len(column["name"]) * 2 + 2,
                        *(map(len, values) or [0]),
                    ),
                )
            )
            sheet.column_dimensions[get_column_letter(index)].width = width
        if spec.get("hidden"):
            sheet.sheet_state = "hidden"

    def _write_metadata_sheet(
        self,
        workbook: Workbook,
        config: ToolConfig,
        metadata: dict[str, Any],
    ) -> None:
        sheet = workbook.create_sheet("_tool_meta")
        header = [
            ("schema_version", metadata["schema_version"]),
            ("run_id", metadata["run_id"]),
            ("rules_version", metadata["rules_version"]),
            ("candidate_id_version", metadata["candidate_id_version"]),
            (
                "projection_fingerprint_version",
                metadata["projection_fingerprint_version"],
            ),
            ("amount_precision", metadata["amount_precision"]),
            ("generated_at", metadata["generated_at"]),
            (
                "source_file_fingerprints",
                json.dumps(
                    metadata.get("source_file_fingerprints", {}),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
        ]
        for key, value in header:
            sheet.append([key, value])
        sheet.append([])
        sheet.append(["dataset_id", "sheet_name"])
        for dataset_id, spec in config.datasets.items():
            sheet.append([dataset_id, spec["sheet"]])
        sheet.append([])
        sheet.append(["field_dataset_id", "field_id", "display_name"])
        for dataset_id, spec in config.datasets.items():
            for column in spec["columns"]:
                sheet.append([dataset_id, column["id"], column["name"]])
        sheet.sheet_state = "hidden"


def _excel_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)
