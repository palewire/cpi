#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse and prepare the Consumer Price Index (CPI) dataset.
"""
import collections
from .base import BaseParser
from .models import Index, Series, ObjectList
from .mappings import ParseArea, ParseItem, ParsePeriod, ParsePeriodicity


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
        object_list = ObjectList()
        for row in self.get_file('cu.series'):
            parsed_id = self.parse_id(row['series_id'])
            obj = Series(
                row['series_id'],
                row['series_title'],
                self.SURVEYS[parsed_id['survey_code']],
                row['seasonal'] == 'S',
                self.periodicities.get(row['periodicity_code']),
                self.areas.get(row['area_code']),
                self.items.get(row['item_code']),
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
                self.series.get(row['series_id']),
                int(row['year']),
                self.periods.get(row['period']),
                float(row['value'])
            )

            # Sort it to the proper lookup
            if index.period.type == 'annual':
                self.by_year[index.series.id][index.year] = index
            elif index.period.type == 'monthly':
                self.by_month[index.series.id][index.date] = index
