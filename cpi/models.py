"""Python objects for modeling Consumer Price Index (CPI) data structures."""

from __future__ import annotations

import logging
import sqlite3
from datetime import date
from pathlib import Path

from pandas import json_normalize

from .defaults import DEFAULTS_SERIES_ATTRS

# CPI tools
from .errors import CPIObjectDoesNotExist

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def query(sql: str, params: list | tuple | None = None) -> list[dict]:
    """Query the cpi.db database and return the result.

    Args:
        sql (str): The SQL query to execute.
        params (list | tuple): The parameters to pass to the query.

    Returns:
        list[dict]: A list of dictionaries representing the result of the query.

    Examples:
        >>> query("SELECT * FROM 'areas';")
        [{'id': '0000', 'code': 'US', 'name': 'United States'}, ...]
    """
    # Connect
    this_dir = Path(__file__).parent.absolute()
    conn = sqlite3.connect(this_dir / "cpi.db")
    cursor = conn.cursor()

    # Query the sql
    if not params:
        query = cursor.execute(sql)
    else:
        query = cursor.execute(sql, params)
    columns = [d[0] for d in query.description]
    result_list = [dict(zip(columns, r)) for r in query.fetchall()]

    # Close
    conn.close()

    # Return the result
    return result_list


def queryone(sql: str, params: list | tuple | None = None) -> dict:
    """Query the cpi.db database and return a single result.

    Args:
        sql (str): The SQL query to execute.
        params (list | tuple): The parameters to pass to the query.

    Returns:
        dict: A dictionary representing the result of the query.

    Raises:
        CPIObjectDoesNotExist: If the object does not exist.
        ValueError: If more than one object exists.

    Examples:
        >>> queryone("SELECT * FROM 'areas' WHERE id=?", ('0000',))
        {'id': '0000', 'code': 'US', 'name': 'United States'}
    """
    dict_list = query(sql, params)
    try:
        assert len(dict_list) == 1
    except AssertionError:
        if len(dict_list) == 0:
            raise CPIObjectDoesNotExist("Object does not exist")
        elif len(dict_list) > 1:
            raise ValueError("More than one object exists")
    return dict_list[0]


class BaseObject:
    """An abstract base class for all the models."""

    table_name: str | None = None  #: The name of the table in the database.

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name

    @classmethod
    def get_by_id(cls, value: str):
        """Returns the object with the provided identifier code."""
        d = queryone(f"SELECT * from '{cls.table_name}' WHERE id=?", (value,))
        return cls(**d)

    @classmethod
    def get_by_name(cls, value: str):
        """Returns the object with the provided name."""
        d = queryone(f"SELECT * from '{cls.table_name}' WHERE name=?", (value,))
        return cls(**d)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the table."""
        dict_list = query(f"SELECT * FROM '{cls.table_name}'")
        return [cls(**d) for d in dict_list]


class Area(BaseObject):
    """A geographical area where prices are gathered monthly."""

    table_name = "areas"

    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}


class Item(BaseObject):
    """A type of consumer good or goods that has its price tracked."""

    table_name = "items"

    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}


class Period(BaseObject):
    """A time period tracked by the CPI."""

    table_name = "periods"

    def __init__(self, id, code, abbreviation, name):
        self.id = id
        self.code = code
        self.abbreviation = abbreviation
        self.name = name

    def __dict__(self):
        return {
            "id": self.id,
            "code": self.code,
            "abbreviation": self.abbreviation,
            "name": self.name,
            "month": self.month,
            "type": self.type,
        }

    @property
    def month(self):
        """
        Returns the month integer for the period.
        """
        if self.id in ["M13", "S01", "S03"]:
            return 1
        elif self.id == "S02":
            return 7
        else:
            return int(self.id.replace("M", ""))

    @property
    def type(self):
        """
        Returns a string classifying the period.
        """
        if self.id in ["M13", "S03"]:
            return "annual"
        elif self.id in ["S01", "S02"]:
            return "semiannual"
        else:
            return "monthly"


class Periodicity(BaseObject):
    """A time interval tracked by the CPI."""

    table_name = "periodicities"

    def __init__(self, id, code, name):
        self.id = code
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}


class Index(BaseObject):
    """A Consumer Price Index value generated by the Bureau of Labor Statistics."""

    table_name = "indexes"

    def __init__(self, series_id: str, year: int, period: Period, value: float):
        self.series_id = series_id
        self.year = year
        self.period = period
        self.value = value

    def __str__(self):
        return f"{self.date} ({self.period}): {self.value}"

    def __eq__(self, other):
        return (
            self.value == other.value
            and self.series_id == other.series_id
            and self.year == other.year
            and self.period == other.period
        )

    def __dict__(self):
        return {
            "series_id": self.series_id,
            "year": self.year,
            "date": str(self.date),
            "period": self.period.__dict__(),
            "value": self.value,
        }

    @property
    def date(self) -> date:
        """
        Accepts a row from the raw BLS data. Returns a Python date object based on its period.
        """
        return date(self.year, self.period.month, 1)


class Series(BaseObject):
    """
    A set of CPI data observed over an extended period of time over consistent time intervals ranging from
    a specific consumer item in a specific geographical area whose price is gathered monthly to a category
    of worker in a specific industry whose employment rate is being recorded monthly, etc.

    Yes, that's the offical government definition. I'm not kidding.
    """

    def __init__(
        self,
        id: str,
        title: str,
        survey: str,
        seasonally_adjusted: str,
        periodicity: Periodicity,
        area: Area,
        items: Item,
        indexes: list[Index],
    ):
        self.id = id
        self.title = title
        self.survey = survey
        self.seasonally_adjusted = seasonally_adjusted
        self.periodicity = periodicity
        self.area = area
        self.items = items
        self.indexes = indexes

    def __str__(self):
        return f"{self.id}: {self.title}"

    def __dict__(self):
        return {
            "id": self.id,
            "title": self.title,
            "survey": self.survey,
            "seasonally_adjusted": self.seasonally_adjusted,
            "periodicity": self.periodicity.__dict__(),
            "area": self.area.__dict__(),
            "items": self.items.__dict__(),
        }

    def to_dataframe(self):
        """
        Returns this series and all its indexes as a pandas DataFrame.
        """
        dict_list = [obj.__dict__() for obj in self.indexes]
        return json_normalize(dict_list, sep="_")

    @property
    def latest_month(self) -> date:
        return max([i.date for i in self.indexes if i.period.type == "monthly"])

    @property
    def latest_year(self) -> int:
        return max([i.year for i in self.indexes if i.period.type == "annual"])

    def get_index_by_date(self, date: date, period_type="annual"):
        period_list = [i for i in self.indexes if i.period.type == period_type]
        try:
            return next(i for i in period_list if i.date == date)
        except StopIteration:
            raise CPIObjectDoesNotExist(
                f"Index of {period_type} type for {date} does not exist"
            )

    @classmethod
    def get_by_id(cls, value: str):
        # If it's not there, try querying the database
        d = queryone("SELECT * FROM 'series' WHERE id=?", (value,))

        # Get the other bits
        seasonalities = {1: True, 0: False}
        d["seasonally_adjusted"] = seasonalities[d["seasonally_adjusted"]]
        d["periodicity"] = Periodicity.get_by_id(d["periodicity"])
        d["area"] = Area.get_by_id(d["area"])
        d["items"] = Item.get_by_id(d["items"])

        # Get the indexes
        dict_list = query("SELECT * FROM 'indexes' WHERE series=?", (value,))

        # Cache the periods to reduce queries
        period_cache = {p.id: p for p in Period.all()}

        # Load the indexes one by one
        d["indexes"] = []
        for i in dict_list:
            obj = Index(
                series_id=d["id"],
                year=int(i["year"]),
                period=period_cache[i["period"]],
                value=float(i["value"]),
            )
            d["indexes"].append(obj)

        # Convert it into a Series object
        return cls(**d)


class SeriesList(list):
    """
    A custom list of indexes in a series.
    """

    SEASONALITIES = {True: "S", False: "U"}
    SURVEYS = {
        "All urban consumers": "CU",
        "Urban wage earners and clerical workers": "CW",
    }

    # Set a cache
    _dict: dict[str, Series] = {}

    def to_dataframe(self):
        """
        Returns the list as a pandas DataFrame.
        """
        dict_list = [obj.__dict__() for obj in self]
        return json_normalize(dict_list, sep="_")

    def append(self, obj: Series):
        """
        Override to default append method that allows validation and dictionary-style lookups
        """
        # Add to dictionary lookup
        self._dict[obj.id] = obj

        # Append to list
        super().append(obj)

    def get_by_id(self, value) -> Series:
        """Returns the CPI series object with the provided identifier code."""
        logger.debug(f"Retrieving series with id {value}")

        # First try the cache
        try:
            return self._dict[value]
        except KeyError:
            pass

        # Get it
        obj = Series.get_by_id(value)

        # Cache it
        self._dict[value] = obj

        # Return it
        return obj

    def all(self) -> list[Series]:
        """Get all of the series from our database."""
        # Query all of the series ids from the database
        series_list = query("SELECT id FROM 'series';")

        # Get all of them, to ensure they're all loaded in the cache
        return [self.get_by_id(d["id"]) for d in series_list]

    def get(
        self,
        survey=DEFAULTS_SERIES_ATTRS["survey"],
        seasonally_adjusted=DEFAULTS_SERIES_ATTRS["seasonally_adjusted"],
        periodicity=DEFAULTS_SERIES_ATTRS["periodicity"],
        area=DEFAULTS_SERIES_ATTRS["area"],
        items=DEFAULTS_SERIES_ATTRS["items"],
    ) -> Series:
        """Returns a single CPI Series object based on the input.

        The default series is returned if not configuration is made to the keyword arguments.
        """
        # Get all the codes for these humanized input.
        try:
            survey_code = self.SURVEYS[survey]
        except KeyError:
            raise CPIObjectDoesNotExist(f"Survey with the name {survey} does not exist")

        try:
            seasonality_code = self.SEASONALITIES[seasonally_adjusted]
        except KeyError:
            raise CPIObjectDoesNotExist(
                f"Seasonality {seasonally_adjusted} does not exist"
            )

        # Generate the series id
        series_id = "{}{}{}{}{}".format(
            survey_code,
            seasonality_code,
            Periodicity.get_by_name(periodicity).code,
            Area.get_by_name(area).code,
            Item.get_by_name(items).code,
        )

        # Pull the series
        return Series.get_by_id(series_id)
