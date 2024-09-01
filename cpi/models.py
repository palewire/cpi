#! /usr/bin/env python
"""
Python objects for modeling Consumer Price Index (CPI) data structures.
"""
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

THIS_DIR: Path = Path(__file__).parent.absolute()


def query(sql: str) -> list[dict]:
    # Connect
    conn = sqlite3.connect(THIS_DIR / "cpi.db")
    cursor = conn.cursor()

    # Query the sql
    query = cursor.execute(sql)
    columns = [d[0] for d in query.description]
    result_list = [dict(zip(columns, r)) for r in query.fetchall()]

    # Close
    conn.close()

    # Return the result
    return result_list


def queryone(sql: str) -> dict:
    dict_list = query(sql)
    try:
        assert len(dict_list) == 1
    except AssertionError:
        if len(dict_list) == 0:
            raise CPIObjectDoesNotExist("Object does not exist")
        elif len(dict_list) > 1:
            raise ValueError("More than one object exists")
    return dict_list[0]


class MappingList(list):
    """
    A custom list that allows for lookups by attribute.
    """

    def __init__(self):
        self._id_dict = {}
        self._name_dict = {}

    def get_by_id(self, value):
        try:
            return self._id_dict[value]
        except KeyError:
            raise CPIObjectDoesNotExist(f"Object with id {value} could not be found")

    def get_by_name(self, value):
        try:
            return self._name_dict[value]
        except KeyError:
            raise CPIObjectDoesNotExist(f"Object with id {value} could not be found")

    def append(self, item):
        """
        Override to default append method that allows dictionary-style lookups
        """
        # Add to dictionary lookup
        self._id_dict[item.id] = item
        self._name_dict[item.name] = item

        # Append to list
        super().append(item)


class BaseObject:
    """
    An abstract base class for all the models.
    """

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name


class Area(BaseObject):
    """
    A geographical area where prices are gathered monthly.
    """

    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}

    @staticmethod
    def get_by_id(value: str):
        d = queryone(f"SELECT * from 'areas' WHERE id='{value}';")
        return Area(**d)

    @staticmethod
    def get_by_name(value: str):
        d = queryone(f"SELECT * from 'areas' WHERE name='{value}';")
        return Area(**d)


class Item(BaseObject):
    """
    A consumer item that has its price tracked.
    """

    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}

    @staticmethod
    def get_by_id(value: str):
        d = queryone(f"SELECT * from 'items' WHERE id='{value}';")
        return Item(**d)

    @staticmethod
    def get_by_name(value: str):
        d = queryone(f"SELECT * from 'items' WHERE name='{value}';")
        return Item(**d)


class Period(BaseObject):
    """
    A time period tracked by the CPI.
    """

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

    @staticmethod
    def get_by_id(value: str):
        d = queryone(f"SELECT * from 'periods' WHERE id='{value}';")
        return Period(**d)

    @staticmethod
    def get_by_name(value: str):
        d = queryone(f"SELECT * from 'periods' WHERE name='{value}';")
        return Period(**d)


class Periodicity(BaseObject):
    """
    A time interval tracked by the CPI.
    """

    def __init__(self, id, code, name):
        self.id = code
        self.code = code
        self.name = name

    def __dict__(self):
        return {"id": self.id, "code": self.code, "name": self.name}

    @staticmethod
    def get_by_id(value: str):
        d = queryone(f"SELECT * from 'periodicities' WHERE id='{value}';")
        return Periodicity(**d)

    @staticmethod
    def get_by_name(value: str):
        d = queryone(f"SELECT * from 'periodicities' WHERE name='{value}';")
        return Periodicity(**d)


class Index(BaseObject):
    """A Consumer Price Index value generated by the Bureau of Labor Statistics."""

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

    @staticmethod
    def get_by_id(value: str):
        # If it's not there, try querying the database
        d = queryone(f"SELECT * FROM 'series' WHERE id='{value}';")

        # Throw an error if it can't be found
        if not d:
            raise CPIObjectDoesNotExist(f"Object with id {value} could not be found")

        # Get the other bits
        seasonalities = {1: True, 0: False}
        d["seasonally_adjusted"] = seasonalities[d["seasonally_adjusted"]]
        d["periodicity"] = Periodicity.get_by_id(d["periodicity"])
        d["area"] = Area.get_by_id(d["area"])
        d["items"] = Item.get_by_id(d["items"])

        # Get the indexes
        dict_list = query(f"SELECT * FROM 'index' WHERE series='{value}';")
        d["indexes"] = []
        for i in dict_list:
            obj = Index(
                series_id=d["id"],
                year=i["year"],
                period=Period.get_by_id(i["period"]),
                value=i["value"],
            )
            d["indexes"].append(obj)

        # Convert it into a Series object
        return Series(**d)


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

    def get(
        self,
        survey=DEFAULTS_SERIES_ATTRS["survey"],
        seasonally_adjusted=DEFAULTS_SERIES_ATTRS["seasonally_adjusted"],
        periodicity=DEFAULTS_SERIES_ATTRS["periodicity"],
        area=DEFAULTS_SERIES_ATTRS["area"],
        items=DEFAULTS_SERIES_ATTRS["items"],
    ) -> Series:
        """
        Returns a single CPI Series object based on the input.

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
