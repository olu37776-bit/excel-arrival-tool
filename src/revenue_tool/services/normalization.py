from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
import unicodedata
from typing import Any


_WHITESPACE = re.compile(r"\s+")
_NULL_TEXT_MARKERS = {"(空白)", "value", "#value", "#value!"}
AMOUNT_QUANTUM = Decimal("0.01")
ZERO_AMOUNT = Decimal("0.00")

MANUAL_MONTH_BLANK = "BLANK"
MANUAL_MONTH_NORMALIZED = "NORMALIZED"
MANUAL_MONTH_YEAR_REQUIRED = "YEAR_REQUIRED"
MANUAL_MONTH_INVALID = "INVALID"

_YEAR_MONTH_TEXT = re.compile(
    r"^(?P<year>\d{4})(?:[-/.](?P<month>\d{1,2})|(?P<compact>\d{2}))$"
)
_YEAR_MONTH_CHINESE = re.compile(
    r"^(?P<year>\d{4})年(?P<month>\d{1,2})月$"
)
_FULL_DATE_TEXT = re.compile(
    r"^(?P<year>\d{4})(?P<separator>[-/.])(?P<month>\d{1,2})"
    r"(?P=separator)(?P<day>\d{1,2})$"
)
_FULL_DATE_CHINESE = re.compile(
    r"^(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日$"
)
_MONTH_ONLY_TEXT = re.compile(r"^(?P<month>\d{1,2})(?:月|月份)?$")
_ENGLISH_MONTH_TEXT = re.compile(
    r"^(?P<month>[A-Za-z]{3})-(?P<year>\d{2}|\d{4})$"
)
_ENGLISH_MONTHS = {
    name: month
    for month, name in enumerate(
        (
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ),
        start=1,
    )
}


@dataclass(frozen=True)
class ManualMonthNormalizationResult:
    value: str | None
    status: str
    raw_value: Any
    reference_month: str | None = None


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


def normalize_manual_revenue_month(
    raw_value: Any,
    *,
    primary_reference_month: Any = None,
    secondary_reference_month: Any = None,
    data_type: str | None = None,
) -> ManualMonthNormalizationResult:
    """Normalize one user-entered revenue month without guessing a year."""
    if is_business_blank(raw_value, data_type=data_type):
        return ManualMonthNormalizationResult(
            None,
            MANUAL_MONTH_BLANK,
            raw_value,
        )
    if data_type == "e":
        return ManualMonthNormalizationResult(
            None,
            MANUAL_MONTH_INVALID,
            raw_value,
        )

    direct = _direct_year_month(raw_value)
    if direct is not None:
        return ManualMonthNormalizationResult(
            direct,
            MANUAL_MONTH_NORMALIZED,
            raw_value,
        )

    month = _month_only(raw_value)
    if month is None:
        return ManualMonthNormalizationResult(
            None,
            MANUAL_MONTH_INVALID,
            raw_value,
        )

    reference = _reference_year_month(primary_reference_month)
    if reference is None:
        reference = _reference_year_month(secondary_reference_month)
    if reference is None:
        return ManualMonthNormalizationResult(
            None,
            MANUAL_MONTH_YEAR_REQUIRED,
            raw_value,
        )

    reference_year, reference_month = map(int, reference.split("-"))
    reference_index = reference_year * 12 + reference_month
    candidates = [
        (year, abs(year * 12 + month - reference_index))
        for year in (
            reference_year - 1,
            reference_year,
            reference_year + 1,
        )
    ]
    nearest_distance = min(distance for _year, distance in candidates)
    nearest_years = [
        year for year, distance in candidates if distance == nearest_distance
    ]
    if len(nearest_years) != 1:
        return ManualMonthNormalizationResult(
            None,
            MANUAL_MONTH_YEAR_REQUIRED,
            raw_value,
            reference,
        )
    return ManualMonthNormalizationResult(
        _format_year_month(nearest_years[0], month),
        MANUAL_MONTH_NORMALIZED,
        raw_value,
        reference,
    )


def _direct_year_month(value: Any) -> str | None:
    if isinstance(value, datetime):
        return _format_year_month(value.year, value.month)
    if isinstance(value, date):
        return _format_year_month(value.year, value.month)
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        integer = _finite_integer(value)
        if integer is None or integer < 100000 or integer > 999999:
            return None
        year, month = divmod(integer, 100)
        return _format_year_month(year, month)

    text = _compact_month_text(value)
    match = _FULL_DATE_TEXT.fullmatch(text) or _FULL_DATE_CHINESE.fullmatch(
        text
    )
    if match:
        try:
            parsed = date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )
        except ValueError:
            return None
        return _format_year_month(parsed.year, parsed.month)

    match = _YEAR_MONTH_CHINESE.fullmatch(text)
    if match:
        return _format_year_month(
            int(match.group("year")), int(match.group("month"))
        )
    match = _YEAR_MONTH_TEXT.fullmatch(text)
    if match:
        month_text = match.group("month") or match.group("compact")
        return _format_year_month(
            int(match.group("year")), int(month_text)
        )

    match = _ENGLISH_MONTH_TEXT.fullmatch(text)
    if match:
        month = _ENGLISH_MONTHS.get(match.group("month").casefold())
        year_text = match.group("year")
        year = int(year_text) + (2000 if len(year_text) == 2 else 0)
        return _format_year_month(year, month) if month is not None else None
    return None


def _month_only(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        integer = _finite_integer(value)
        return integer if integer is not None and 1 <= integer <= 12 else None
    match = _MONTH_ONLY_TEXT.fullmatch(_compact_month_text(value))
    if not match:
        return None
    month = int(match.group("month"))
    return month if 1 <= month <= 12 else None


def _reference_year_month(value: Any) -> str | None:
    if isinstance(value, (date, datetime)):
        return _format_year_month(value.year, value.month)
    text = _compact_month_text(value)
    match = re.fullmatch(r"(?P<year>\d{4})-(?P<month>\d{2})", text)
    if not match:
        return None
    return _format_year_month(
        int(match.group("year")), int(match.group("month"))
    )


def _finite_integer(value: int | float | Decimal) -> int | None:
    try:
        decimal = Decimal(str(value))
    except InvalidOperation:
        return None
    if not decimal.is_finite() or decimal != decimal.to_integral_value():
        return None
    return int(decimal)


def _compact_month_text(value: Any) -> str:
    return "".join(normalize_text(value).split())


def _format_year_month(year: int, month: int) -> str | None:
    try:
        date(year, month, 1)
    except ValueError:
        return None
    return f"{year:04d}-{month:02d}"


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
