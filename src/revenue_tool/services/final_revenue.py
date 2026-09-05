"""Final views never overwrite automatic values or become historical inputs."""
from __future__ import annotations

from typing import Any

from revenue_tool.services.normalization import (
    is_business_blank, normalize_amount, normalize_manual_revenue_month,
    MANUAL_MONTH_YEAR_REQUIRED,
)

FINAL_FIELD_SOURCES = {
    "final_revenue_segment": ("manual_revenue_segment", "revenue_segment"),
    "final_revenue_month_rpd": (
        "manual_revenue_forecast_rpd", "revenue_month_rpd",
    ),
    "final_revenue_month_cpd": (
        "manual_revenue_forecast_cpd", "revenue_month_cpd",
    ),
    "final_revenue_forecast": ("manual_revenue_month", "revenue_forecast"),
}
YEAR_REQUIRED_HINT = "待修正：请填写完整年月 YYYY-MM"
INVALID_MONTH_HINT = "待修正：月份无法识别，请填写 YYYY-MM"
INVALID_AMOUNT_HINT = "待修正：请填写有效金额"


def calculate_final_values(values: dict[str, Any]) -> dict[str, Any]:
    """Also accepts raw inputs for non-Excel consumers; reader still normalizes.

    Invalid live inputs have visible hints. After read_previous has reported
    and cleared an invalid input, the documented blank fallback applies.
    """
    result = {}
    for final, (manual, automatic) in FINAL_FIELD_SOURCES.items():
        raw = values.get(manual)
        fallback = values.get(automatic)
        if is_business_blank(raw):
            result[final] = fallback
        elif final in {"final_revenue_month_rpd", "final_revenue_month_cpd"}:
            secondary = (
                "revenue_month_cpd" if automatic == "revenue_month_rpd"
                else "revenue_month_rpd"
            )
            normalized = normalize_manual_revenue_month(
                raw, primary_reference_month=fallback,
                secondary_reference_month=values.get(secondary),
            )
            result[final] = normalized.value or (
                YEAR_REQUIRED_HINT
                if normalized.status == MANUAL_MONTH_YEAR_REQUIRED
                else INVALID_MONTH_HINT
            )
        elif final == "final_revenue_forecast":
            amount = normalize_amount(raw)
            result[final] = amount if amount is not None else INVALID_AMOUNT_HINT
        else:
            result[final] = raw
    return result
