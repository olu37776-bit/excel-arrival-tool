from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from revenue_tool.services.normalization import normalize_text


STOCK_NOT_UNLOCKED = "未解锁"
STOCK_PARTIALLY_UNLOCKED = "部分解锁"
STOCK_UNLOCKED = "已解锁"


def aggregate_stock_unlock(values: Iterable[Any]) -> str | None:
    """Aggregate valid stock-control flags into the documented three states."""
    flags = {
        normalized
        for value in values
        if (normalized := normalize_text(value).upper()) in {"Y", "N"}
    }
    if not flags:
        return None
    if flags == {"Y"}:
        return STOCK_NOT_UNLOCKED
    if flags == {"N"}:
        return STOCK_UNLOCKED
    return STOCK_PARTIALLY_UNLOCKED
