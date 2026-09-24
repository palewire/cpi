"""Default values."""

from typing import TypedDict


class SeriesAttributes(TypedDict):
    """Human-readable attributes identifying a CPI series."""

    survey: str
    seasonally_adjusted: bool
    periodicity: str
    area: str
    items: str


DEFAULT_SERIES_ID = "CUUR0000SA0"
DEFAULTS_SERIES_ATTRS: SeriesAttributes = {
    "survey": "All urban consumers",
    "seasonally_adjusted": False,
    "periodicity": "Monthly",
    "area": "U.S. city average",
    "items": "All items",
}
