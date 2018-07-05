#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python objects for modeling Consumer Price Index (CPI) data structures.
"""
import collections
from datetime import date
from .errors import CPIObjectDoesNotExist


class MappingList(list):
    """
    A custom list that allows for lookups by attribute.
    """
    def get_by_id(self, value):
        try:
            return list(filter(lambda obj: obj.id == value, self))[0]
        except IndexError:
            raise CPIObjectDoesNotExist("Object with id {} could not be found".format(value))

    def get_by_name(self, value):
        try:
            return list(filter(lambda obj: obj.name == value, self))[0]
        except IndexError:
            raise CPIObjectDoesNotExist("Object with id {} could not be found".format(value))


class SeriesList(list):
    """
    A custom list of indexes in a series.
    """
    SURVEYS = {
        'All urban consumers': 'CU',
        'Urban wage earners and clerical workers': 'CW'
    }
    SEASONALITIES = {
        True: 'S',
        False: 'U'
    }

    def __init__(self, periodicities, areas, items):
        self.periodicities = periodicities
        self.areas = areas
        self.items = items

    def get_by_id(self, value):
        try:
            return list(filter(lambda obj: obj.id == value, self))[0]
        except IndexError:
            raise CPIObjectDoesNotExist("Object with id {} could not be found".format(value))

    def get(self, survey, seasonally_adjusted, periodicity, area, items):
        # Get all the codes for these humanized input.
        survey_code = self.SURVEYS[survey]
        seasonality_code = self.SEASONALITIES[seasonally_adjusted]
        periodicity_code = self.periodicities.get_by_name(periodicity).code
        area_code = self.areas.get_by_name(area).code
        items_code = self.items.get_by_name(items).code

        # Generate the series id
        series_id = "{}{}{}{}{}".format(
            survey_code,
            seasonality_code,
            periodicity_code,
            area_code,
            items_code
        )

        # Pull the series
        return self.get_by_id(series_id)


class BaseObject(object):
    """
    An abstract base class for all the models.
    """
    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.__str__())


class Area(BaseObject):
    """
    A geographical area where prices are gathered monthly.
    """
    def __init__(self, code, name):
        self.id = code
        self.code = code
        self.name = name

    def __str__(self):
        return self.name


class Item(BaseObject):
    """
    A consumer item that has its price tracked.
    """
    def __init__(self, code, name):
        self.id = code
        self.code = code
        self.name = name

    def __str__(self):
        return self.name


class Period(BaseObject):
    """
    A time period tracked by the CPI.
    """
    def __init__(self, code, abbreviation, name):
        self.id = code
        self.code = code
        self.abbreviation = abbreviation
        self.name = name

    def __str__(self):
        return self.name

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
    """
    A time interval tracked by the CPI.
    """
    def __init__(self, code, name):
        self.id = code
        self.code = code
        self.name = name

    def __str__(self):
        return self.name


class Series(BaseObject):
    """
    A set of CPI data observed over an extended period of time over consistent time intervals ranging from
    a specific consumer item in a specific geographical area whose price is gathered monthly to a category
    of worker in a specific industry whose employment rate is being recorded monthly, etc.

    Yes, that's the offical government definition. I'm not kidding.
    """
    def __init__(
        self,
        id,
        title,
        survey,
        seasonally_adjusted,
        periodicity,
        area,
        items
    ):
        self.id = id
        self.title = title
        self.survey = survey
        self.seasonally_adjusted = seasonally_adjusted
        self.periodicity = periodicity
        self.area = area
        self.items = items
        self._indexes = {
            'annual': collections.OrderedDict(),
            'monthly': collections.OrderedDict(),
            'semiannual': collections.OrderedDict(),
        }

    def __str__(self):
        return "{}: {}".format(self.id, self.title)

    @property
    def indexes(self):
        flat = []
        for l in self._indexes.values():
            flat.extend(l)
        return flat

    @property
    def earliest_date(self):
        return min([i.date for i in self.indexes])

    @property
    def latest_date(self):
        return min([i.date for i in self.indexes])

    @property
    def latest_month(self):
        return max([i.date for i in self._indexes['monthly'].values()])

    @property
    def latest_year(self):
        return max([i.year for i in self._indexes['annual'].values()])

    def get_index_by_date(self, date, period_type='annual'):
        try:
            return self._indexes[period_type][date]
        except KeyError:
            raise CPIObjectDoesNotExist("Index of {} type for {} does not exist".format(period_type, date))


class Index(BaseObject):
    """
    A Consumer Price Index value generated by the Bureau of Labor Statistics.
    """
    def __init__(self, series, year, period, value):
        self.series = series
        self.year = year
        self.period = period
        self.value = value

    def __str__(self):
        return "{} ({}): {}".format(self.date, self.period, self.value)

    @property
    def date(self):
        """
        Accepts a row from the raw BLS data. Returns a Python date object based on its period.
        """
        return date(self.year, self.period.month, 1)
