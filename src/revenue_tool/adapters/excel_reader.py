from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import math
from pathlib import Path
import re
from typing import Any

from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import (
    BaseRow,
    IssueLog,
    ParsedRow,
    PreviousData,
    SourceData,
    WorkbookReadError,
)
from revenue_tool.services.field_matching import resolve_name
from revenue_tool.services.normalization import (
    business_key_identity,
    normalize_signature_value,
    normalize_text,
)


class ExcelInputAdapter:
    def read_source(
        self, path: str | Path, config: ToolConfig, issues: IssueLog
    ) -> SourceData:
        workbook_path = Path(path)
        workbook = _open_workbook(workbook_path)
        result: dict[str, list[ParsedRow]] = {
            role: [] for role in config.sheets
        }
        sheet_names: dict[str, str] = {}
        try:
            available = list(workbook.sheetnames)
            for role, sheet_spec in config.sheets.items():
                match = resolve_name(
                    sheet_spec["canonical"],
                    sheet_spec.get("aliases", []),
                    available,
                    config.workbook["contains_direction"],
                )
                if match.index is None:
                    if match.mode == "ambiguous":
                        names = [available[index] for index in match.candidates]
                        issues.add(
                            "AMBIGUOUS_SHEET",
                            f"业务 Sheet {sheet_spec['canonical']} 命中多个候选: {names}",
                            workbook=workbook_path.name,
                            field=role,
                            raw_value=" | ".join(names),
                        )
                    elif not sheet_spec.get("optional", False):
                        issues.add(
                            "MISSING_SHEET",
                            f"缺少业务 Sheet: {sheet_spec['canonical']}",
                            workbook=workbook_path.name,
                            field=role,
                        )
                    continue
                worksheet = workbook[available[match.index]]
                sheet_names[role] = worksheet.title
                result[role] = self._read_role_sheet(
                    workbook_path,
                    workbook.epoch,
                    worksheet,
                    role,
                    config,
                    issues,
                )
        finally:
            workbook.close()
        return SourceData(workbook_path, result, sheet_names)

    def read_previous(
        self, path: str | Path, config: ToolConfig, issues: IssueLog
    ) -> PreviousData:
        workbook_path = Path(path)
        workbook = _open_workbook(workbook_path)
        try:
            expected_sheet, previous_names = _read_previous_metadata(
                workbook,
                config,
                workbook_path,
                issues,
            )
            match = resolve_name(
                expected_sheet,
                [],
                list(workbook.sheetnames),
                config.workbook["contains_direction"],
            )
            if match.index is None:
                issues.add(
                    "PREVIOUS_BASE_SHEET_UNAVAILABLE",
                    f"上期结果未唯一找到 Sheet: {expected_sheet}",
                    workbook=workbook_path.name,
                    raw_value=" | ".join(workbook.sheetnames),
                )
                return PreviousData({}, usable=False)
            sheet = workbook[workbook.sheetnames[match.index]]
            header_row = self._detect_output_header(
                sheet,
                config,
                [
                    previous_names.get(column["id"], column["name"])
                    for column in config.base_columns
                ],
            )
            if header_row is None:
                issues.add(
                    "PREVIOUS_HEADER_NOT_FOUND",
                    "上期基表未找到可识别表头",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                )
                return PreviousData({}, usable=False)
            headers = [
                normalize_text(cell.value)
                for cell in sheet[header_row]
            ]
            indexes: dict[str, int | None] = {}
            for column in config.base_columns:
                previous_name = previous_names.get(
                    column["id"], column["name"]
                )
                match = resolve_name(
                    previous_name,
                    [],
                    headers,
                    config.workbook["contains_direction"],
                )
                indexes[column["id"]] = match.index
                if match.index is None:
                    issues.add(
                        "PREVIOUS_FIELD_UNAVAILABLE",
                        f"上期基表字段未唯一匹配: {previous_name}",
                        workbook=workbook_path.name,
                        sheet=sheet.title,
                        field=column["id"],
                    )
            essential = {
                "contract_no",
                "supply_center",
                "revenue_month_rpd",
                "revenue_month_cpd",
            }
            if any(indexes[field] is None for field in essential):
                issues.add(
                    "PREVIOUS_BASE_UNUSABLE",
                    "上期基表缺少比较键或自动收入年月字段，本期不执行继承与比较",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                    field=" | ".join(
                        sorted(
                            field
                            for field in essential
                            if indexes[field] is None
                        )
                    ),
                )
                return PreviousData({}, usable=False)
            rows: dict[tuple[str, str], BaseRow] = {}
            for row_number in range(header_row + 1, sheet.max_row + 1):
                cells = list(sheet[row_number])
                if _row_is_blank(cells):
                    continue
                values: dict[str, Any] = {}
                for column in config.base_columns:
                    field = column["id"]
                    index = indexes[field]
                    cell = cells[index] if index is not None and index < len(cells) else None
                    values[field] = _parse_previous_value(
                        field,
                        cell.value if cell is not None else None,
                        workbook.epoch,
                    )
                display_key = (
                    str(values.get("contract_no") or ""),
                    str(values.get("supply_center") or ""),
                )
                if not all(display_key):
                    issues.add(
                        "PREVIOUS_INVALID_BUSINESS_KEY",
                        "上期基表业务键不完整，无法继承或比较",
                        workbook=workbook_path.name,
                        sheet=sheet.title,
                        row_number=row_number,
                        business_key=" | ".join(display_key),
                    )
                    continue
                key = business_key_identity(*display_key)
                if key in rows:
                    issues.add(
                        "PREVIOUS_DUPLICATE_BUSINESS_KEY",
                        "上期基表存在重复业务键，按原顺序保留第一条",
                        workbook=workbook_path.name,
                        sheet=sheet.title,
                        row_number=row_number,
                        business_key=_display_key(display_key),
                    )
                    continue
                rows[key] = BaseRow(values)
            return PreviousData(rows, usable=True)
        finally:
            workbook.close()

    def _read_role_sheet(
        self,
        workbook_path: Path,
        epoch: datetime,
        sheet,
        role: str,
        config: ToolConfig,
        issues: IssueLog,
    ) -> list[ParsedRow]:
        sheet_spec = config.sheets[role]
        header_row = sheet_spec.get("header_row")
        if header_row is None:
            header_row = self._detect_source_header(sheet, role, config)
        if not isinstance(header_row, int) or not (1 <= header_row <= sheet.max_row):
            issues.add(
                "HEADER_NOT_FOUND",
                "未找到满足配置条件的表头行",
                workbook=workbook_path.name,
                sheet=sheet.title,
                field=role,
            )
            return []

        headers = [normalize_text(cell.value) for cell in sheet[header_row]]
        indexes: dict[str, int | None] = {}
        matched_by_index: dict[int, list[str]] = {}
        for field, field_spec in config.fields[role].items():
            match = resolve_name(
                field_spec["canonical"],
                field_spec.get("aliases", []),
                headers,
                config.workbook["contains_direction"],
            )
            indexes[field] = match.index
            if match.index is not None:
                matched_by_index.setdefault(match.index, []).append(field)
            elif match.mode == "ambiguous":
                candidate_names = [headers[index] for index in match.candidates]
                issues.add(
                    "AMBIGUOUS_FIELD",
                    f"字段 {field_spec['canonical']} 命中多个候选",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                    row_number=header_row,
                    field=field,
                    raw_value=" | ".join(candidate_names),
                )
            else:
                issues.add(
                    "MISSING_FIELD",
                    f"未找到字段: {field_spec['canonical']}",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                    row_number=header_row,
                    field=field,
                )

        for index, fields in matched_by_index.items():
            if len(fields) <= 1:
                continue
            for field in fields:
                indexes[field] = None
            issues.add(
                "FIELD_COLLISION",
                "一个源表头被多个内部字段占用，本次均视为不可用",
                workbook=workbook_path.name,
                sheet=sheet.title,
                row_number=header_row,
                field=" | ".join(fields),
                raw_value=headers[index],
            )

        seen_signatures: dict[tuple[tuple[str, str], ...], int] = {}
        result: list[ParsedRow] = []
        for row_number in range(header_row + 1, sheet.max_row + 1):
            cells = list(sheet[row_number])
            if _row_is_blank(cells):
                continue
            signature = tuple(
                normalize_signature_value(cell.value) for cell in cells
            )
            first_row = seen_signatures.get(signature)
            if first_row is not None:
                issues.add(
                    "DUPLICATE_ROW_IGNORED",
                    f"完全重复行已忽略，首次出现于第 {first_row} 行",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                    row_number=row_number,
                    raw_value=f"first_row={first_row}",
                )
                continue
            seen_signatures[signature] = row_number

            values: dict[str, Any] = {}
            raw_values: dict[str, Any] = {}
            invalid: set[str] = set()
            for field, field_spec in config.fields[role].items():
                index = indexes[field]
                cell = (
                    cells[index]
                    if index is not None and index < len(cells)
                    else None
                )
                raw = cell.value if cell is not None else None
                raw_values[field] = raw
                value, valid = _parse_source_cell(
                    field_spec["type"],
                    cell,
                    epoch,
                )
                values[field] = value
                if not valid:
                    invalid.add(field)
                    issues.add(
                        _error_code_for_type(field_spec["type"]),
                        f"字段值无法按 {field_spec['type']} 解析，已排除该值",
                        workbook=workbook_path.name,
                        sheet=sheet.title,
                        row_number=row_number,
                        field=field,
                        raw_value=raw,
                    )
            if "contract_no" in values and not values["contract_no"]:
                issues.add(
                    "MISSING_CONTRACT_NO",
                    "合同号为空，该行无法进入合同集合",
                    workbook=workbook_path.name,
                    sheet=sheet.title,
                    row_number=row_number,
                    field="contract_no",
                    raw_value=raw_values.get("contract_no"),
                )
            result.append(
                ParsedRow(
                    role=role,
                    sheet=sheet.title,
                    row_number=row_number,
                    values=values,
                    raw_values=raw_values,
                    invalid_fields=frozenset(invalid),
                )
            )
        return result

    def _detect_source_header(
        self, sheet, role: str, config: ToolConfig
    ) -> int | None:
        max_row = min(
            int(config.workbook["header_scan_rows"]),
            sheet.max_row,
        )
        minimum = min(
            int(config.workbook["minimum_header_matches"]),
            len(config.fields[role]),
        )
        best: tuple[int, int] | None = None
        for row_number in range(1, max_row + 1):
            headers = [normalize_text(cell.value) for cell in sheet[row_number]]
            count = 0
            for field_spec in config.fields[role].values():
                match = resolve_name(
                    field_spec["canonical"],
                    field_spec.get("aliases", []),
                    headers,
                    config.workbook["contains_direction"],
                )
                if match.index is not None:
                    count += 1
            if count >= minimum and (best is None or count > best[0]):
                best = (count, row_number)
        return best[1] if best else None

    def _detect_output_header(
        self,
        sheet,
        config: ToolConfig,
        expected_names: list[str] | None = None,
    ) -> int | None:
        max_row = min(
            int(config.workbook["header_scan_rows"]),
            sheet.max_row,
        )
        expected = expected_names or [
            column["name"] for column in config.base_columns
        ]
        for row_number in range(1, max_row + 1):
            headers = [normalize_text(cell.value) for cell in sheet[row_number]]
            matched = sum(
                1
                for name in expected
                if resolve_name(
                    name,
                    [],
                    headers,
                    config.workbook["contains_direction"],
                ).index
                is not None
            )
            if matched >= min(5, len(expected)):
                return row_number
        return None


def _open_workbook(path: Path):
    if not path.exists():
        raise WorkbookReadError(f"工作簿不存在: {path}")
    try:
        return load_workbook(path, data_only=True, read_only=False)
    except Exception as exc:
        raise WorkbookReadError(f"工作簿无法读取: {path}: {exc}") from exc


def _row_is_blank(cells) -> bool:
    return all(
        cell.value is None
        or (isinstance(cell.value, str) and not cell.value.strip())
        for cell in cells
    )


def _parse_source_cell(
    field_type: str, cell, epoch: datetime
) -> tuple[Any, bool]:
    raw = cell.value if cell is not None else None
    if cell is not None and getattr(cell, "data_type", None) == "e":
        return None, False
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, True
    if field_type == "text":
        return _text_from_cell(cell), True
    if field_type == "flag":
        value = normalize_text(raw).upper()
        return (value, True) if value in {"Y", "N"} else (None, False)
    if field_type == "amount":
        value = _parse_decimal(raw)
        return value, value is not None
    if field_type == "date":
        value = _parse_date(raw, epoch)
        return value, value is not None
    if field_type == "nonnegative_integer":
        value = _parse_nonnegative_integer(raw)
        return value, value is not None
    return normalize_text(raw), True


def _text_from_cell(cell) -> str:
    raw = cell.value
    if isinstance(raw, bool):
        return "TRUE" if raw else "FALSE"
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        number = Decimal(str(raw))
        text = (
            str(int(number))
            if number == number.to_integral_value()
            else format(number.normalize(), "f")
        )
        format_section = str(cell.number_format or "").split(";")[0]
        if number == number.to_integral_value() and re.fullmatch(
            r"0+", format_section
        ):
            return text.zfill(len(format_section))
        return text
    return normalize_text(raw)


def _parse_decimal(value: Any) -> Decimal | None:
    try:
        text = normalize_text(value).replace(",", "")
        negative = text.startswith("(") and text.endswith(")")
        if negative:
            text = text[1:-1]
        result = Decimal(text)
        if not result.is_finite():
            return None
        result = -result if negative else result
        as_float = float(result)
        if not math.isfinite(as_float) or (
            result != 0 and as_float == 0
        ):
            return None
        return result
    except (InvalidOperation, ValueError):
        return None


def _parse_nonnegative_integer(value: Any) -> int | None:
    decimal = _parse_decimal(value)
    if (
        decimal is None
        or decimal < 0
        or decimal != decimal.to_integral_value()
    ):
        return None
    return int(decimal)


def _parse_date(value: Any, epoch: datetime) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            converted = from_excel(value, epoch)
            if isinstance(converted, datetime):
                return converted.date()
            if isinstance(converted, date):
                return converted
            return None
        except (TypeError, ValueError, OverflowError):
            return None
    text = normalize_text(value)
    for pattern in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y年%m月%d日",
        "%Y%m%d",
        "%d-%b-%Y",
        "%d %b %Y",
    ):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _parse_previous_value(field: str, value: Any, epoch: datetime) -> Any:
    if value is None:
        return None
    if field in {"contract_no", "supply_center"}:
        return normalize_text(value)
    if field in {"legacy_amount", "monthly_new_order"}:
        return _parse_decimal(value)
    if field in {
        "ata",
        "asd",
        "rpd",
        "cpd",
        "arrival_date_rpd",
        "arrival_date_cpd",
    }:
        return _parse_date(value, epoch)
    if field in {"revenue_month_rpd", "revenue_month_cpd"}:
        if isinstance(value, (date, datetime)):
            return value.strftime("%Y-%m")
        return normalize_text(value)
    if field == "manual_revenue_month":
        return value
    return normalize_text(value)


def _error_code_for_type(field_type: str) -> str:
    return {
        "amount": "INVALID_AMOUNT",
        "date": "INVALID_DATE",
        "flag": "INVALID_FLAG",
        "nonnegative_integer": "INVALID_TRANSIT_DAYS",
    }.get(field_type, "INVALID_VALUE")


def _display_key(key: tuple[str, str]) -> str:
    return f"{key[0]} | {key[1]}"


def _read_previous_metadata(
    workbook,
    config: ToolConfig,
    workbook_path: Path,
    issues: IssueLog,
) -> tuple[str, dict[str, str]]:
    default_sheet = config.output["sheets"]["base"]
    default_names = config.base_names_by_id
    if "_tool_meta" not in workbook.sheetnames:
        return default_sheet, default_names
    sheet = workbook["_tool_meta"]
    try:
        if (
            normalize_text(sheet["A1"].value) != "schema_version"
            or normalize_text(sheet["A2"].value) != "base_sheet"
            or normalize_text(sheet["A4"].value) != "field_id"
        ):
            raise ValueError("metadata header mismatch")
        base_sheet = normalize_text(sheet["B2"].value)
        names: dict[str, str] = {}
        for row_number in range(5, sheet.max_row + 1):
            field = normalize_text(sheet.cell(row_number, 1).value)
            name = normalize_text(sheet.cell(row_number, 2).value)
            if field and name:
                names[field] = name
        if not base_sheet or not names:
            raise ValueError("metadata content is incomplete")
        return base_sheet, names
    except Exception:
        issues.add(
            "PREVIOUS_METADATA_INVALID",
            "上期结果的内部字段元数据无效，回退到当前显示名匹配",
            workbook=workbook_path.name,
            sheet="_tool_meta",
        )
        return default_sheet, default_names
