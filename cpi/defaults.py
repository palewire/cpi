from pathlib import Path

"""Default values."""

DEFAULT_SERIES_ID = "CUUR0000SA0"
DEFAULTS_SERIES_ATTRS = {
    "survey": "All urban consumers",
    "seasonally_adjusted": False,
    "periodicity": "Monthly",
    "area": "U.S. city average",
    "items": "All items",
}
DEFAULT_DB_PATH = Path(__file__).parent.absolute() / "cpi.db"
