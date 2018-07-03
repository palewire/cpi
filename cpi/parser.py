#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse and prepare the Consumer Price Index (CPI) dataset.
"""
import collections
from .base import BaseParser
from .mappings import ParsePeriod
from .models import Index, Series, ObjectList


class ParseSeries(BaseParser):
    """
    Parses the raw list of CPI series from the BLS.
    """
    def parse(self):
        """
        Returns a list Series objects.
        """
        object_list = ObjectList()
        for row in self.get_file('cu.series'):
            obj = Series(
                row['series_id']
            )
            object_list.append(obj)
        return object_list


class ParseIndex(BaseParser):

    def __init__(self, periods=None):
        self.by_year = collections.defaultdict(collections.OrderedDict)
        self.by_month = collections.defaultdict(collections.OrderedDict)

        # Mappings
        self.periods = periods or ParsePeriod().parse()

    def parse(self):
        """
        Parse the raw BLS data into dictionaries for Python lookups.
        """
        for row in self.get_file("cu.data.1.AllItems"):
            # Create a series
            series = Series(row['series_id'])

            # Create an object
            index = Index(
                series,
                int(row['year']),
                self.periods.get(row['period']),
                float(row['value'])
            )

            # Sort it to the proper lookup
            if index.period.type == 'annual':
                self.by_year[series.id][index.year] = index
            elif index.period.type == 'monthly':
                self.by_month[series.id][index.date] = index
