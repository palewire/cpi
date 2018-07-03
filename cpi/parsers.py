#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse and prepare the Consumer Price Index (CPI) dataset.
"""
import os
import csv
import collections
from .models import MappingList, SeriesList
from .models import Area, Item, Period, Periodicity, Index, Series


class BaseParser(object):
    THIS_DIR = os.path.dirname(__file__)

    def get_file(self, file):
        """
        Returns the CPI data as a csv.DictReader object.
        """
        # Open up the CSV from the BLS
        csv_path = os.path.join(self.THIS_DIR, "{}.csv".format(file))
        csv_file = open(csv_path, "r")
        return csv.DictReader(csv_file)


class ParseArea(BaseParser):
    """
    Parses the raw list of CPI areas.
    """
    def parse(self):
        """
        Returns a list Area objects.
        """
        object_list = MappingList()
        for row in self.get_file('cu.area'):
            obj = Area(row['area_code'], row['area_name'])
            object_list.append(obj)
        return object_list


class ParseItem(BaseParser):
    """
    Parses the raw list of CPI items.
    """
    def parse(self):
        """
        Returns a list Area objects.
        """
        object_list = MappingList()
        for row in self.get_file('cu.item'):
            obj = Item(row['item_code'], row['item_name'])
            object_list.append(obj)
        return object_list


class ParsePeriod(BaseParser):
    """
    Parses the raw list of CPI periods.
    """
    def parse(self):
        """
        Returns a list Area objects.
        """
        object_list = MappingList()
        for row in self.get_file('cu.period'):
            obj = Period(row['period'], row['period_abbr'], row['period_name'])
            object_list.append(obj)
        return object_list


class ParsePeriodicity(BaseParser):
    """
    Parses the raw list of CPI periodicities.
    """
    def parse(self):
        """
        Returns a list Periodicity objects.
        """
        object_list = MappingList()
        for row in self.get_file('cu.periodicity'):
            obj = Periodicity(row['periodicity_code'], row['periodicity_name'])
            object_list.append(obj)
        return object_list


class ParseSeries(BaseParser):
    """
    Parses the raw list of CPI series from the BLS.
    """
    SURVEYS = {
        'CU': 'All urban consumers',
        'CW': 'Urban wage earners and clerical workers'
    }

    def __init__(self, periodicities=None, areas=None, items=None):
        self.periodicities = periodicities or ParsePeriodicity().parse()
        self.areas = areas or ParseArea().parse()
        self.items = items or ParseItem().parse()

    def parse_id(self, id):
        return dict(
            survey_code=id[:2],
            seasonal_code=id[2:3],
            periodicity_code=id[3:4],
            area_code=id[4:8],
            item_code=id[8:]
        )

    def parse(self):
        """
        Returns a list Series objects.
        """
        object_list = SeriesList(periodicities=self.periodicities, areas=self.areas, items=self.items)
        for row in self.get_file('cu.series'):
            parsed_id = self.parse_id(row['series_id'])
            obj = Series(
                row['series_id'],
                row['series_title'],
                self.SURVEYS[parsed_id['survey_code']],
                row['seasonal'] == 'S',
                self.periodicities.get_by_id(row['periodicity_code']),
                self.areas.get_by_id(row['area_code']),
                self.items.get_by_id(row['item_code']),
                int(row['begin_year']),
                int(row['end_year'])
            )
            object_list.append(obj)
        return object_list


class ParseIndex(BaseParser):

    def __init__(self, series=None, periods=None):
        self.by_year = collections.defaultdict(collections.OrderedDict)
        self.by_month = collections.defaultdict(collections.OrderedDict)
        self.series = series or ParseSeries().parse()
        self.periods = periods or ParsePeriod().parse()

    def parse(self):
        """
        Parse the raw BLS data into dictionaries for Python lookups.
        """
        for row in self.get_file("cu.data.1.AllItems"):
            # Create an object
            index = Index(
                self.series.get_by_id(row['series_id']),
                int(row['year']),
                self.periods.get_by_id(row['period']),
                float(row['value'])
            )

            # Sort it to the proper lookup
            if index.period.type == 'annual':
                self.by_year[index.series.id][index.year] = index
            elif index.period.type == 'monthly':
                self.by_month[index.series.id][index.date] = index
