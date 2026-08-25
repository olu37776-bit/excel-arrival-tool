from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from revenue_tool.config import ToolConfig
from revenue_tool.domain.models import IssueLog, ParsedRow, SourceData
from revenue_tool.services.normalization import (
    nonblank,
    normalize_lookup,
    normalize_text,
)


class DataQualityAnalyzer:
    """Report source-data risks without changing business calculations."""

    def analyze(
        self,
        source: SourceData,
        config: ToolConfig,
        issues: IssueLog,
    ) -> None:
        self._log_country_conflicts(source, issues)
        self._log_control_flag_risks(source.rows["demand_detail"], issues)
        self._log_small_legacy_amounts(
            source.rows["legacy"], config, issues
        )
        self._log_missing_incoterms(source.rows["demand_detail"], issues)
        self._log_date_storage_risks(source.rows["demand_detail"], issues)

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
        stock_count = sum(
            nonblank(row.values.get("stock_control_flag")) for row in rows
        )
        shipment_count = sum(
            nonblank(row.values.get("shipment_control_flag")) for row in rows
        )
        if stock_count != shipment_count:
            first = rows[0] if rows else None
            issues.add(
                "CONTROL_FLAG_COUNT_MISMATCH",
                "备货总控标识与发货总控标识的有效值条数不同",
                workbook=first.workbook if first else "",
                sheet=first.sheet if first else "",
                field="stock_control_flag+shipment_control_flag",
                raw_value=f"{stock_count} | {shipment_count}",
            )
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

    def _log_small_legacy_amounts(
        self,
        rows: list[ParsedRow],
        config: ToolConfig,
        issues: IssueLog,
    ) -> None:
        threshold = Decimal(
            str(config.rules["amount_residual_warning_threshold"])
        )
        for row in rows:
            value = row.values.get("legacy_amount")
            if not isinstance(value, Decimal) or value == 0:
                continue
            if abs(value) >= threshold:
                continue
            issues.add(
                "SUSPECT_AMOUNT_FLOAT_RESIDUE",
                (
                    f"非零遗留量绝对值小于 {threshold}，按两位小数显示为 0.00，"
                    "可能是浮点精度残留；为避免误改财务数据，本次保留原值"
                ),
                workbook=row.workbook,
                sheet=row.sheet,
                row_number=row.row_number,
                business_key=str(row.values.get("contract_no") or ""),
                field="legacy_amount",
                raw_value=row.raw_values.get("legacy_amount"),
            )

    def _log_missing_incoterms(
        self, rows: list[ParsedRow], issues: IssueLog
    ) -> None:
        for row in rows:
            if nonblank(row.values.get("incoterm")):
                continue
            contract = str(row.values.get("contract_no") or "")
            center = str(row.values.get("supply_center") or "")
            issues.add(
                "MISSING_INCOTERM",
                "贸易术语为空；运输周期将按同业务粒度的首个非空贸易术语继续，若均为空则按国家+供应中心匹配",
                workbook=row.workbook,
                sheet=row.sheet,
                row_number=row.row_number,
                business_key=f"{contract} | {center}",
                field="incoterm",
                raw_value=row.raw_values.get("incoterm"),
            )

    def _log_date_storage_risks(
        self, rows: list[ParsedRow], issues: IssueLog
    ) -> None:
        for row in rows:
            for field in ("ata", "asd", "rpd", "cpd"):
                value = row.values.get(field)
                raw = row.raw_values.get(field)
                if not isinstance(value, date) or isinstance(raw, date):
                    continue
                issues.add(
                    "DATE_STORAGE_TYPE_UNEXPECTED",
                    "日期虽可解析，但源单元格不是 Excel datetime；本次继续使用并报告存储类型偏差",
                    workbook=row.workbook,
                    sheet=row.sheet,
                    row_number=row.row_number,
                    business_key=(
                        f"{row.values.get('contract_no') or ''} | "
                        f"{row.values.get('supply_center') or ''}"
                    ),
                    field=field,
                    raw_value=raw,
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
        identity = normalize_lookup(value)
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
