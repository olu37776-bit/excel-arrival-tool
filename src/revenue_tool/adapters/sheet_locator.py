from __future__ import annotations

from dataclasses import dataclass

from revenue_tool.config import ToolConfig
from revenue_tool.services.field_matching import resolve_name
from revenue_tool.services.normalization import normalize_lookup, normalize_text


@dataclass(frozen=True)
class SheetFingerprint:
    sheet_name: str
    header_row: int | None
    matched_fields: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    name_matches_role: bool
    meets_contract: bool


@dataclass(frozen=True)
class SheetResolution:
    mode: str
    selected: SheetFingerprint | None
    matches: tuple[SheetFingerprint, ...]
    fingerprints: tuple[SheetFingerprint, ...]


def resolve_role_sheet(
    workbook,
    role: str,
    config: ToolConfig,
) -> SheetResolution:
    """Resolve one business sheet by its field contract, never by name alone."""
    sheet_spec = config.sheets[role]
    expected_names = {
        normalize_lookup(sheet_spec["canonical"]),
        *(
            normalize_lookup(alias)
            for alias in sheet_spec.get("aliases", [])
        ),
    }
    ordered_sheets = sorted(
        workbook.worksheets,
        key=lambda sheet: (
            normalize_lookup(sheet.title) not in expected_names,
            workbook.sheetnames.index(sheet.title),
        ),
    )
    fingerprints = tuple(
        _fingerprint_sheet(
            sheet,
            role,
            config,
            normalize_lookup(sheet.title) in expected_names,
        )
        for sheet in ordered_sheets
    )
    matches = tuple(
        fingerprint
        for fingerprint in fingerprints
        if fingerprint.meets_contract
    )
    if len(matches) == 1:
        return SheetResolution("unique", matches[0], matches, fingerprints)
    if len(matches) > 1:
        return SheetResolution("ambiguous", None, matches, fingerprints)
    return SheetResolution("not_found", None, (), fingerprints)


def _fingerprint_sheet(
    sheet,
    role: str,
    config: ToolConfig,
    name_matches_role: bool,
) -> SheetFingerprint:
    fields = config.fields[role]
    required = tuple(config.sheets[role]["required_fields"])
    minimum = min(
        int(config.workbook["minimum_header_matches"]),
        len(fields),
    )
    configured_header = config.sheets[role].get("header_row")
    if configured_header is None:
        max_row = min(
            int(config.workbook["header_scan_rows"]),
            sheet.max_row,
        )
        row_numbers = range(1, max_row + 1)
    else:
        row_numbers = (int(configured_header),)
    best_row: int | None = None
    best_fields: tuple[str, ...] = ()
    best_score = (-1, -1, 0)
    for row_number in row_numbers:
        if row_number > sheet.max_row:
            continue
        headers = [normalize_text(cell.value) for cell in sheet[row_number]]
        matched = _matched_fields(headers, fields, config)
        matched_set = set(matched)
        score = (
            sum(field in matched_set for field in required),
            len(matched),
            -row_number,
        )
        if score > best_score:
            best_row = row_number
            best_fields = matched
            best_score = score
    matched_set = set(best_fields)
    missing_required = tuple(
        field for field in required if field not in matched_set
    )
    meets_contract = (
        best_row is not None
        and not missing_required
        and len(best_fields) >= minimum
    )
    return SheetFingerprint(
        sheet_name=sheet.title,
        header_row=best_row,
        matched_fields=best_fields,
        missing_required_fields=missing_required,
        name_matches_role=name_matches_role,
        meets_contract=meets_contract,
    )


def _matched_fields(
    headers: list[str],
    fields: dict[str, dict[str, object]],
    config: ToolConfig,
) -> tuple[str, ...]:
    matched_indexes: dict[str, int] = {}
    fields_by_index: dict[int, list[str]] = {}
    for field, field_spec in fields.items():
        match = resolve_name(
            str(field_spec["canonical"]),
            list(field_spec.get("aliases", [])),
            headers,
            config.workbook["contains_direction"],
        )
        if match.index is None:
            continue
        matched_indexes[field] = match.index
        fields_by_index.setdefault(match.index, []).append(field)
    collided = {
        field
        for grouped_fields in fields_by_index.values()
        if len(grouped_fields) > 1
        for field in grouped_fields
    }
    return tuple(
        field for field in fields if field in matched_indexes and field not in collided
    )
