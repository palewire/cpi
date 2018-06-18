#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open the Consumer Price Index (CPI) dataset.
"""
import os
import csv
from datetime import datetime


class Data(object):
    this_dir = os.path.dirname(__file__)

    def __init__(self):
        self.cpi_file = list(self.get_cpi_file())

    def get_year_dict(self):
        """
        Returns a dictionary of the CPI-U adjustment value for each year available.
        """
        return dict(
            (int(r['year']), float(r['value'])) for r in self.cpi_file if r['period_type'] == 'annual'
        )

    def get_month_dict(self):
        """
        Returns a dictionary of the CPI-U adjustment value for each year available.
        """
        return dict(
            (datetime.strptime(r['date'], '%Y-%m-%d').date(), float(r['value']))
            for r in self.cpi_file if r['period_type'] == 'monthly'
        )

    def get_cpi_file(self):
        """
        Returns the CPI data as a csv.DictReader object.
        """
        # Open up the CSV from the BLS
        csv_path = os.path.join(self.this_dir, 'data.csv')
        csv_file = open(csv_path, "r")
        return csv.DictReader(csv_file)


data = Data()
cpi_by_year = data.get_year_dict()
cpi_by_month = data.get_month_dict()
