from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from revenue_tool.domain.errors import InputValidationError


@dataclass(frozen=True)
class ToolConfig:
    mappings: dict[str, Any]
    rules: dict[str, Any]

    @property
    def sheet_names(self) -> dict[str, str]:
        return self.mappings["sheets"]

    def columns(self, section: str) -> dict[str, str]:
        return self.mappings[section]


def load_config(config_dir: str | Path) -> ToolConfig:
    directory = Path(config_dir)
    mappings = _load_json(directory / "field_mappings.json")
    rules = _load_json(directory / "business_rules.json")
    _validate_config(mappings, rules)
    return ToolConfig(mappings=mappings, rules=rules)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise InputValidationError(f"Missing configuration file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputValidationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputValidationError(f"Configuration root must be an object: {path}")
    return value


def _validate_config(mappings: dict[str, Any], rules: dict[str, Any]) -> None:
    required_sections = {"sheets", "prd", "shipment", "transit_days"}
    missing = required_sections.difference(mappings)
    if missing:
        raise InputValidationError(
            "Missing field mapping sections: " + ", ".join(sorted(missing))
        )

    required_rule_sections = {"grouping", "prd", "transit", "comparison"}
    missing_rules = required_rule_sections.difference(rules)
    if missing_rules:
        raise InputValidationError(
            "Missing business rule sections: " + ", ".join(sorted(missing_rules))
        )

