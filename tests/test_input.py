import warnings
from pathlib import Path
from datetime import date, datetime

import pytest
import numpy as np
import pandas as pd
from click.testing import CliRunner

import cpi
from cpi import cli
from cpi.models import queryone
from cpi.errors import CPIObjectDoesNotExist


# These global variables change with each data update.
# They will need to be edited when the data changes, which
# happens every month.
LATEST_YEAR = 2024
LATEST_YEAR_1950_ALL_ITEMS = 1301.6141078838175
LATEST_YEAR_1950_CUSR0000SA0 = 1301.6141078838175
LATEST_MONTH = date(2025, 3, 1)
LATEST_MONTH_1950_ALL_ITEMS = 1360.8468085106383
LATEST_MONTH_1950_CUSR0000SA0 = 1359.4853253934496


def test_latest_year():
    assert cpi.LATEST_YEAR == LATEST_YEAR


def test_latest_month():
    assert cpi.LATEST_MONTH == LATEST_MONTH


def test_get():
    assert cpi.get(1950) == 24.1
    assert cpi.get(date(1950, 1, 1)) == 23.5
    assert cpi.get(2000) == 172.2


def test_get_by_kwargs():
    # "CUUR0000SA0"
    assert cpi.get(2000) == 172.2

    # "CUSR0000SA0"
    assert cpi.get(date(2000, 1, 1), seasonally_adjusted=True) == 169.30
    # ... which doesn't have annual values
    with pytest.raises(CPIObjectDoesNotExist):
        cpi.get(2000, seasonally_adjusted=True)

    # "CUSR0000SA0E"
    # ... which we don't have loaded yet as data
    with pytest.raises(CPIObjectDoesNotExist):
        cpi.get(2000, seasonally_adjusted=True, items="Energy")

    # "CUURS49ASA0"
    assert cpi.get(2000, area="Los Angeles-Long Beach-Anaheim, CA") == 171.6

    assert cpi.get(date(2000, 1, 1), area="Los Angeles-Long Beach-Anaheim, CA") == 167.9

    # "CUURS49ASA0E"
    assert (
        cpi.get(2000, items="Energy", area="Los Angeles-Long Beach-Anaheim, CA")
        == 132.0
    )

    # "CUURA421SAT"
    assert (
        cpi.get(2000, items="Transportation", area="Los Angeles-Long Beach-Anaheim, CA")
        == 154.2
    )

    # "CUURA421SA0E"
    assert (
        cpi.get(
            2000,
            items="All items - old base",
            area="Los Angeles-Long Beach-Anaheim, CA",
        )
        == 506.8
    )


def test_get_by_series_id():
    assert cpi.get(date(1950, 1, 1), series_id="CUSR0000SA0") == 23.51


def test_series_list():
    cpi.series.get_by_id("CUSR0000SA0")


def test_metadata_lists():
    assert len(cpi.areas.all()) > 0
    assert len(cpi.periods.all()) > 0
    assert len(cpi.periodicities.all()) > 0
    assert len(cpi.items.all()) > 0


def test_series_indexes():
    # Make sure we can lazy load the full database
    for series in cpi.series:
        assert len(series.indexes) > 0
        series.latest_month
        series.latest_year
        series.__str__()
        series.__dict__()
        for index in series.indexes:
            index.__str__()
            index.__dict__()


def test_get_errors():
    with pytest.raises(CPIObjectDoesNotExist):
        cpi.get(1900)
    with pytest.raises(CPIObjectDoesNotExist):
        cpi.get(date(1900, 1, 1))
    with pytest.raises(CPIObjectDoesNotExist):
        cpi.get(1950, series_id="FOOBAR")


def test_get_value_error():
    with pytest.raises(ValueError):
        cpi.get(1900.1)
        cpi.get(datetime.now())
        cpi.get(3000)


def test_inflate_years():
    assert cpi.inflate(100, 1950) == LATEST_YEAR_1950_ALL_ITEMS
    assert (
        cpi.inflate(100, 1950, series_id="CUUR0000SA0") == LATEST_YEAR_1950_CUSR0000SA0
    )
    assert cpi.inflate(100, 1950, to=2017) == 1017.0954356846472
    assert cpi.inflate(100, 1950, to=1960) == 122.82157676348547
    assert cpi.inflate(100.0, 1950, to=1950) == 100


def test_inflate_months():
    assert cpi.inflate(100, date(1950, 1, 1)) == LATEST_MONTH_1950_ALL_ITEMS
    assert cpi.inflate(100, date(1950, 1, 11)) == LATEST_MONTH_1950_ALL_ITEMS
    assert cpi.inflate(100, datetime(1950, 1, 1)) == LATEST_MONTH_1950_ALL_ITEMS
    assert cpi.inflate(100, date(1950, 1, 1), to=date(2018, 1, 1)) == 1054.7531914893618
    assert cpi.inflate(100, date(1950, 1, 1), to=date(1960, 1, 1)) == 124.68085106382979


def test_inflate_other_series():
    assert (
        cpi.inflate(100, date(1950, 1, 1), series_id="CUSR0000SA0")
        == LATEST_MONTH_1950_CUSR0000SA0
    )


def test_deflate():
    assert cpi.inflate(1017.0954356846472, 2017, to=1950) == 100
    assert cpi.inflate(122.82157676348547, 1960, to=1950) == 100


def test_numpy_dtypes():
    assert cpi.get(np.int64(1950)) == cpi.get(1950)
    assert cpi.inflate(100, np.int32(1950)) == cpi.inflate(100, 1950)
    assert cpi.inflate(100, np.int64(1950), to=np.int64(1960)) == cpi.inflate(
        100, 1950, to=1960
    )
    assert cpi.inflate(100, np.int64(1950), to=np.int32(1960)) == cpi.inflate(
        100, 1950, to=1960
    )
    assert cpi.inflate(100, np.int64(1950), to=1960) == cpi.inflate(100, 1950, to=1960)
    assert cpi.inflate(
        100, pd.to_datetime("1950-07-01"), to=pd.to_datetime("1960-07-01")
    ) == cpi.inflate(100, date(1950, 7, 1), to=date(1960, 7, 1))


def test_mismatch():
    with pytest.raises(TypeError):
        cpi.inflate(100, 1950, to=date(2000, 1, 1))
    with pytest.raises(TypeError):
        cpi.inflate(100, date(2000, 1, 1), to=1950)


def test_warning():
    warnings.warn(cpi.StaleDataWarning(), stacklevel=2)


def test_bad_queryone():
    with pytest.raises(CPIObjectDoesNotExist):
        queryone("SELECT * FROM series WHERE id = 'FOOBAR'")
    with pytest.raises(ValueError):
        queryone("SELECT * FROM series")


def test_pandas():
    this_dir = Path(__file__).parent.absolute()
    df = pd.read_csv(this_dir / "test.csv")
    df["ADJUSTED"] = df.apply(
        lambda x: cpi.inflate(x.MEDIAN_HOUSEHOLD_INCOME, x.YEAR), axis=1
    )
    df = df.set_index("YEAR")
    assert (
        cpi.inflate(df.at[1984, "MEDIAN_HOUSEHOLD_INCOME"], 1984)
        == df.at[1984, "ADJUSTED"]
    )
    cpi.series.to_dataframe()
    cpi.series.get().to_dataframe()


def invoke(*args):
    """Invoke the CLI with the given arguments and return the output."""
    runner = CliRunner()
    result = runner.invoke(cli.inflate, args)
    assert result.exit_code == 0
    string_value = result.output.replace("\n", "")
    # Do some rounding to ensure the same results for Python 2 and 3
    return str(round(float(string_value), 7))


def test_cli_inflate_years():
    assert invoke("100", "1950") == str(round(LATEST_YEAR_1950_CUSR0000SA0, 7))
    assert invoke("100", "1950", "--to", "1960") == "122.8215768"
    assert invoke("100", "1950", "--to", "1950") == "100.0"


def test_cli_inflate_months():
    assert invoke("100", "1950-01-01") == str(round(LATEST_MONTH_1950_ALL_ITEMS, 7))
    assert invoke("100", "1950-01-11") == str(round(LATEST_MONTH_1950_ALL_ITEMS, 7))
    assert invoke("100", "1950-01-11", "--to", "1960-01-01") == "124.6808511"
    assert invoke("100", "1950-01-01 00:00:00", "--to", "1950-01-01") == "100.0"
    assert invoke("100", "1950-01-01", "--to", "2018-01-01") == "1054.7531915"
    assert invoke("100", "1950-01-01", "--to", "1960-01-01") == "124.6808511"
    assert invoke("100", "1950-01-01", "--series_id", "CUSR0000SA0") == str(
        round(LATEST_MONTH_1950_CUSR0000SA0, 7)
    )
