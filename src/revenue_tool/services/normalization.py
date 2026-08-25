from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import re
import unicodedata
from typing import Any


_WHITESPACE = re.compile(r"\s+")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return _WHITESPACE.sub(" ", text).strip()


def normalize_lookup(value: Any) -> str:
    return normalize_text(value).casefold()


def business_key_identity(
    contract_no: Any, supply_center: Any
) -> tuple[str, str]:
    """Return the stable internal identity without changing display values."""
    return (
        normalize_text(contract_no),
        normalize_lookup(supply_center),
    )


def normalize_signature_value(value: Any) -> tuple[str, str]:
    if value is None or (isinstance(value, str) and not normalize_text(value)):
        return ("blank", "")
    if isinstance(value, datetime):
        return ("date", value.date().isoformat())
    if isinstance(value, date):
        return ("date", value.isoformat())
    if isinstance(value, bool):
        return ("bool", "1" if value else "0")
    if isinstance(value, Decimal):
        return ("number", format(value.normalize(), "f"))
    if isinstance(value, (int, float)):
        return ("number", format(Decimal(str(value)).normalize(), "f"))
    return ("text", normalize_text(value))


def nonblank(value: Any) -> bool:
    return value is not None and (
        not isinstance(value, str) or bool(value.strip())
    )
