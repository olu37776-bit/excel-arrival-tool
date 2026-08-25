from __future__ import annotations

from collections.abc import Iterable

from revenue_tool.domain.errors import UnknownTradeTypeError
from revenue_tool.domain.models import TransitRule


class TransitDaysResolver:
    """Resolves base transit days, then applies isolated trade-type adjustments."""

    def __init__(
        self,
        rules: Iterable[TransitRule],
        adjustments: dict[str, dict[str, int | float]],
        unknown_trade_type: str = "error",
        default_days: int = 0,
    ) -> None:
        self._base_days = {
            _normalise(rule.trade_type): int(rule.transit_days) for rule in rules
        }
        self._adjustments = {
            _normalise(name): value for name, value in adjustments.items()
        }
        self._unknown_trade_type = unknown_trade_type
        self._default_days = int(default_days)

    def resolve(self, trade_type: str) -> int:
        key = _normalise(trade_type)
        if key in self._base_days:
            days = self._base_days[key]
        elif self._unknown_trade_type == "default":
            days = self._default_days
        else:
            raise UnknownTradeTypeError(
                f"Trade Type '{trade_type}' has no Transit Days configuration"
            )

        adjustment = self._adjustments.get(key, {})
        if "override_days" in adjustment:
            days = int(adjustment["override_days"])
        days = round(days * float(adjustment.get("multiplier", 1)))
        days += int(adjustment.get("extra_days", 0))
        if days < 0:
            raise ValueError(f"Calculated transit days cannot be negative: {trade_type}")
        return days


def _normalise(value: str) -> str:
    return value.strip().casefold()

