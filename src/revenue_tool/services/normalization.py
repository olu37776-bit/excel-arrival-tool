from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
import unicodedata
from typing import Any


_WHITESPACE = re.compile(r"\s+")
_NULL_TEXT_MARKERS = {"(空白)", "value", "#value", "#value!"}
AMOUNT_QUANTUM = Decimal("0.01")
ZERO_AMOUNT = Decimal("0.00")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return _WHITESPACE.sub(" ", text).strip()


def normalize_lookup(value: Any) -> str:
    return normalize_text(value).casefold()


def normalize_country_identity(value: Any) -> str:
    """Return a strict country identity without guessing similar names."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return "".join(
        character
        for character in text
        if not character.isspace()
        and unicodedata.category(character) != "Cf"
    ).casefold()


def canonical_country_identity(
    value: Any,
    aliases: dict[str, str] | None = None,
) -> str:
    """Resolve one strict, explicitly configured country identity."""
    identity = normalize_country_identity(value)
    return (aliases or {}).get(identity, identity)


def is_business_blank(value: Any, *, data_type: str | None = None) -> bool:
    """Return whether a source value is a documented business null."""
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    text = normalize_text(value)
    if not text:
        return True
    normalized = text.casefold()
    if normalized in _NULL_TEXT_MARKERS:
        return True
    return data_type == "e" and normalized == "#value!"


def normalize_amount(value: Any) -> Decimal | None:
    """Parse and quantize an amount using the single business precision."""
    if is_business_blank(value):
        return ZERO_AMOUNT
    if isinstance(value, bool):
        return None
    try:
        text = normalize_text(value).replace(",", "")
        negative = text.startswith("(") and text.endswith(")")
        if negative:
            text = text[1:-1]
        amount = Decimal(text)
        if not amount.is_finite():
            return None
        if negative:
            amount = -amount
        return amount.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return None


def business_key_identity(
    contract_no: Any, supply_center: Any
) -> tuple[str, str]:
    """Return the stable internal identity without changing display values."""
    return (
        normalize_text(contract_no),
        normalize_lookup(supply_center),
    )


def normalize_signature_value(value: Any) -> tuple[str, str]:
    if is_business_blank(value):
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
    return not is_business_blank(value)
