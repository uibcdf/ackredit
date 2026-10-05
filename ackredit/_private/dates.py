"""Bounded calendar-date interpretation shared by CFF and CSL export."""

from datetime import date


def calendar_date_parts(value: object) -> list[int] | None:
    """Read YYYY-MM-DD only; callers retain non-calendar values as original text."""
    text = str(value).strip()
    if (
        len(text) != 10
        or text[4] != "-"
        or text[7] != "-"
        or not all(part.isdecimal() for part in (text[:4], text[5:7], text[8:]))
    ):
        return None
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        return None
    return [parsed.year, parsed.month, parsed.day]
