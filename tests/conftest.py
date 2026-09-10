# tests/conftest.py
import os
from pathlib import Path

FIXTURE_DB_PATH = Path(__file__).parent.absolute() / "fixtures" / "cpi.db"
os.environ["CPI_DB_PATH"] = str(FIXTURE_DB_PATH)
