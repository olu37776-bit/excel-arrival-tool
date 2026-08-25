from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from revenue_tool.services.normalization import normalize_lookup


@dataclass(frozen=True)
class MatchResult:
    index: int | None
    mode: str
    candidates: tuple[int, ...] = ()


def resolve_name(
    canonical: str,
    aliases: Iterable[str],
    candidates: list[str],
    contains_direction: str = "header_contains_expected",
) -> MatchResult:
    expected = {normalize_lookup(canonical)}
    expected.update(normalize_lookup(alias) for alias in aliases)
    expected.discard("")
    normalized = [normalize_lookup(value) for value in candidates]

    exact = tuple(
        index for index, value in enumerate(normalized) if value in expected
    )
    if len(exact) == 1:
        return MatchResult(exact[0], "exact", exact)
    if len(exact) > 1:
        return MatchResult(None, "ambiguous", exact)

    def matches(value: str, token: str) -> bool:
        if not value or not token:
            return False
        if contains_direction == "either":
            return token in value or value in token
        return token in value

    contains = tuple(
        index
        for index, value in enumerate(normalized)
        if any(matches(value, token) for token in expected)
    )
    if len(contains) == 1:
        return MatchResult(contains[0], "contains", contains)
    if len(contains) > 1:
        return MatchResult(None, "ambiguous", contains)
    return MatchResult(None, "missing", ())

