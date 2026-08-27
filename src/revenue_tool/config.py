from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import unicodedata
from typing import Any


@dataclass(frozen=True)
class ToolConfig:
    raw: dict[str, Any]

    @property
    def workbook(self) -> dict[str, Any]:
        return self.raw["workbook"]

    @property
    def sheets(self) -> dict[str, dict[str, Any]]:
        return self.raw["sheets"]

    @property
    def fields(self) -> dict[str, dict[str, dict[str, Any]]]:
        return self.raw["fields"]

    @property
    def rules(self) -> dict[str, Any]:
        return self.raw["rules"]

    @property
    def output(self) -> dict[str, Any]:
        return self.raw["output"]

    @property
    def base_columns(self) -> list[dict[str, str]]:
        return self.output["base_columns"]

    @property
    def base_names_by_id(self) -> dict[str, str]:
        return {item["id"]: item["name"] for item in self.base_columns}


def load_config(path: str | Path) -> ToolConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    _validate(raw)
    return ToolConfig(raw)


def _validate(raw: dict[str, Any]) -> None:
    if not isinstance(raw, dict):
        raise ValueError("配置根节点必须为对象")
    for key in ("workbook", "sheets", "fields", "rules", "output"):
        if key not in raw:
            raise ValueError(f"配置缺少顶层字段: {key}")
        if not isinstance(raw[key], dict):
            raise ValueError(f"配置顶层字段 {key} 必须为对象")
    expected_roles = {"legacy", "monthly_order", "demand_detail", "transit"}
    if set(raw["sheets"]) != expected_roles or set(raw["fields"]) != expected_roles:
        raise ValueError(
            "配置中的 Sheet 角色必须为 legacy/monthly_order/demand_detail/transit"
        )
    expected_fields = {
        "legacy": {
            "contract_no": "text",
            "region": "text",
            "country": "text",
            "customer_group": "text",
            "project_name": "text",
            "bg": "text",
            "legacy_amount": "amount",
        },
        "monthly_order": {
            "contract_no": "text",
            "region": "text",
            "country": "text",
            "project_name": "text",
            "bg": "text",
            "monthly_new_order": "amount",
        },
        "demand_detail": {
            "contract_no": "text",
            "region": "text",
            "country": "text",
            "customer_group": "text",
            "project_name": "text",
            "demand_status": "text",
            "supply_center": "text",
            "incoterm": "text",
            "stock_control_flag": "flag",
            "shipment_control_flag": "flag",
            "ata": "date",
            "asd": "date",
            "rpd": "date",
            "cpd": "date",
            "bg": "text",
        },
        "transit": {
            "country": "text",
            "supply_center": "text",
            "transit_days": "nonnegative_integer",
        },
    }
    for role, fields in expected_fields.items():
        configured = raw["fields"][role]
        if not isinstance(configured, dict):
            raise ValueError(f"{role} 字段配置必须为对象")
        if set(configured) != set(fields):
            raise ValueError(
                f"{role} 的稳定内部字段 ID 必须为: "
                + ", ".join(fields)
            )
        for field, expected_type in fields.items():
            spec = configured[field]
            if not isinstance(spec, dict):
                raise ValueError(f"{role}.{field} 配置必须为对象")
            if spec.get("type") != expected_type:
                raise ValueError(
                    f"{role}.{field} 类型必须为 {expected_type}"
                )
            if not isinstance(spec.get("canonical"), str) or not spec[
                "canonical"
            ].strip():
                raise ValueError(f"{role}.{field} canonical 不能为空")
            _validate_aliases(spec.get("aliases", []), f"{role}.{field}")
    for role, spec in raw["sheets"].items():
        if not isinstance(spec, dict):
            raise ValueError(f"Sheet 角色 {role} 配置必须为对象")
        if not isinstance(spec.get("canonical"), str) or not spec[
            "canonical"
        ].strip():
            raise ValueError(f"Sheet 角色 {role} canonical 不能为空")
        _validate_aliases(spec.get("aliases", []), f"Sheet 角色 {role}")
        expected_optional = role == "monthly_order"
        if spec.get("optional") is not expected_optional:
            raise ValueError(
                "仅 monthly_order 可选；其余三个源文件角色必须为必选"
            )
        required_fields = spec.get("required_fields")
        if (
            not isinstance(required_fields, list)
            or not required_fields
            or any(
                not isinstance(field, str) or not field.strip()
                for field in required_fields
            )
            or len(set(required_fields)) != len(required_fields)
            or any(field not in raw["fields"][role] for field in required_fields)
        ):
            raise ValueError(
                f"Sheet 角色 {role} required_fields 必须是该角色内唯一、"
                "非空的稳定字段 ID 列表"
            )
        header_row = spec.get("header_row")
        if header_row is not None and (
            not isinstance(header_row, int)
            or isinstance(header_row, bool)
            or header_row < 1
        ):
            raise ValueError(f"Sheet 角色 {role} header_row 必须为空或正整数")

    columns = raw["output"].get("base_columns", [])
    expected_base_ids = [
        "contract_no",
        "legacy_amount",
        "monthly_new_order",
        "revenue_forecast",
        "bg",
        "region",
        "country",
        "carryover_type",
        "customer_group",
        "project_name",
        "incoterm",
        "supply_center",
        "multiple_supply_centers",
        "stock_unlocked",
        "split_shipment",
        "transit_days",
        "ata",
        "asd",
        "rpd",
        "multiple_demand",
        "latest_asd",
        "latest_rpd",
        "shipment_incomplete",
        "cpd",
        "split_supply",
        "arrival_date_rpd",
        "arrival_date_cpd",
        "revenue_month_rpd",
        "revenue_month_cpd",
        "revenue_segment",
        "manual_adjust_flag",
        "manual_revenue_forecast_rpd",
        "manual_revenue_forecast_cpd",
        "manual_revenue_month",
        "adjustment_note",
    ]
    if not _valid_columns(columns, expected_base_ids):
        raise ValueError("基表 35 个稳定字段 ID、顺序和显示名必须符合契约")
    expected_change_common = [
        "contract_no",
        "legacy_amount",
        "monthly_new_order",
        "region",
        "country",
        "customer_group",
        "supply_center",
    ]
    change_common = raw["output"].get("change_common_columns", [])
    if not _valid_columns(change_common, expected_change_common):
        raise ValueError("变化清单公共字段 ID 或顺序不符合契约")
    expected_supply_pull = expected_change_common + [
        "revenue_month_rpd",
        "revenue_month_cpd",
    ]
    if not _valid_columns(
        raw["output"].get("supply_pull_columns", []),
        expected_supply_pull,
    ):
        raise ValueError("供应需要提拉诉求清单字段 ID 或顺序不符合契约")
    change_tails = raw["output"].get("change_tail_columns")
    if not isinstance(change_tails, dict) or set(change_tails) != {
        "rpd",
        "cpd",
    }:
        raise ValueError("变化清单尾部配置必须同时包含 rpd 和 cpd")
    for mode in ("rpd", "cpd"):
        tail = change_tails[mode]
        if not _valid_columns(tail, [
            "previous_month",
            "current_month",
            "direction",
            "change_months",
        ]):
            raise ValueError(f"{mode.upper()} 变化清单尾部字段配置不完整")
        combined_names = [
            column["name"] for column in change_common + tail
        ]
        if len({_name_identity(name) for name in combined_names}) != len(
            combined_names
        ):
            raise ValueError(f"{mode.upper()} 变化清单显示名必须唯一")
    expected_issue_ids = [
        "code",
        "severity",
        "workbook",
        "sheet",
        "row_number",
        "business_key",
        "field",
        "raw_value",
        "message",
    ]
    if not _valid_columns(
        raw["output"].get("issue_columns", []), expected_issue_ids
    ):
        raise ValueError("异常清单字段 ID 或顺序不符合契约")
    output_sheets = raw["output"].get("sheets")
    if not isinstance(output_sheets, dict):
        raise ValueError("输出 sheets 必须为对象")
    output_sheet_names = list(output_sheets.values())
    output_names_are_valid = all(
        isinstance(name, str) and bool(name.strip())
        for name in output_sheet_names
    )
    if (
        set(output_sheets)
        != {
            "base",
            "rpd_changes",
            "cpd_changes",
            "supply_pull",
            "issues",
        }
        or not output_names_are_valid
        or len({_name_identity(name) for name in output_sheet_names})
        != len(output_sheet_names)
        or _name_identity("_tool_meta")
        in {_name_identity(name) for name in output_sheet_names}
        or any(not _valid_sheet_name(name) for name in output_sheet_names)
    ):
        raise ValueError("五个输出 Sheet 显示名必须非空、唯一且不能占用 _tool_meta")
    if raw["workbook"].get("contains_direction") not in {
        "header_contains_expected",
        "either",
    }:
        raise ValueError("contains_direction 只能为 header_contains_expected 或 either")
    if raw["workbook"].get("duplicate_scope") != "normalized_physical_row":
        raise ValueError(
            "当前 duplicate_scope 只支持 normalized_physical_row"
        )
    for field in ("header_scan_rows", "minimum_header_matches"):
        value = raw["workbook"].get(field)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 1
        ):
            raise ValueError(f"{field} 必须为正整数")
    fixed_transit = raw["rules"].get("fixed_transit_days")
    if not isinstance(fixed_transit, dict) or not fixed_transit:
        raise ValueError("fixed_transit_days 必须为非空对象")
    if any(
        not isinstance(term, str)
        or not term.strip()
        or not isinstance(days, int)
        or isinstance(days, bool)
        or days < 0
        for term, days in fixed_transit.items()
    ):
        raise ValueError("fixed_transit_days 必须使用非空术语和非负整数天数")
    carryover = raw["rules"].get("carryover_countries")
    if not isinstance(carryover, list) or any(
        not isinstance(country, str) or not country.strip()
        for country in carryover
    ):
        raise ValueError("carryover_countries 必须为非空字符串数组")
def _validate_aliases(aliases: Any, context: str) -> None:
    if not isinstance(aliases, list) or any(
        not isinstance(alias, str) or not alias.strip()
        for alias in aliases
    ):
        raise ValueError(f"{context} aliases 必须为字符串数组")


def _valid_columns(columns: Any, expected_ids: list[str]) -> bool:
    if not isinstance(columns, list) or any(
        not isinstance(column, dict) for column in columns
    ):
        return False
    ids = [column.get("id") for column in columns]
    names = [column.get("name") for column in columns]
    return (
        ids == expected_ids
        and all(isinstance(name, str) and name.strip() for name in names)
        and len({_name_identity(name) for name in names}) == len(names)
    )


def _name_identity(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.split()).casefold()


def _valid_sheet_name(value: str) -> bool:
    return len(value) <= 31 and not any(
        character in value for character in "[]:*?/\\"
    )
