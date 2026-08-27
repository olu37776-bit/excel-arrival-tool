from __future__ import annotations

from datetime import date
from hashlib import sha256
from typing import Any

from revenue_tool.domain.models import ParsedRow
from revenue_tool.domain.revenue_models import DemandRecord
from revenue_tool.services.normalization import nonblank, normalize_lookup, normalize_text


class DemandRecordService:
    """Translate already-deduplicated ParsedRows into run-scoped evidence."""

    def build(self, rows: list[ParsedRow]) -> list[DemandRecord]:
        records: list[DemandRecord] = []
        for row in rows:
            contract = row.values.get("contract_no")
            if not nonblank(contract):
                continue
            contract_no = str(contract)
            supply_center = _text_or_none(row.values.get("supply_center"))
            records.append(
                DemandRecord(
                    demand_record_id=_record_id(
                        row,
                        contract_no,
                        supply_center,
                    ),
                    contract_no=contract_no,
                    supply_center=supply_center,
                    demand_status=_text_or_none(
                        row.values.get("demand_status")
                    ),
                    incoterm=_text_or_none(row.values.get("incoterm")),
                    stock_control_flag=_text_or_none(
                        row.values.get("stock_control_flag")
                    ),
                    shipment_control_flag=_text_or_none(
                        row.values.get("shipment_control_flag")
                    ),
                    ata=_date_or_none(row.values.get("ata")),
                    asd=_date_or_none(row.values.get("asd")),
                    rpd=_date_or_none(row.values.get("rpd")),
                    cpd=_date_or_none(row.values.get("cpd")),
                    bg=_text_or_none(row.values.get("bg")),
                    source_workbook=row.workbook,
                    source_sheet=row.sheet,
                    source_row_number=row.row_number,
                    invalid_fields=tuple(sorted(row.invalid_fields)),
                )
            )
        return records


def _record_id(
    row: ParsedRow,
    contract_no: str,
    supply_center: str | None,
) -> str:
    trace = "\x1f".join(
        (
            row.workbook,
            row.sheet,
            str(row.row_number),
            normalize_text(contract_no),
            normalize_lookup(supply_center),
        )
    )
    return f"DR-{sha256(trace.encode('utf-8')).hexdigest()[:20]}"


def _text_or_none(value: Any) -> str | None:
    return normalize_text(value) if nonblank(value) else None


def _date_or_none(value: Any) -> date | None:
    return value if isinstance(value, date) else None
