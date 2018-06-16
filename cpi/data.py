#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open the Consumer Price Index (CPI) dataset.
"""
import os
import csv


def _get_cpi_dict():
    """
    Returns a dictionary of the CPI-U adjustment value for each year available.
    """
    # Open up the CSV from the BLS
    this_dir = os.path.dirname(__file__)
    csv_path = os.path.join(this_dir, 'data.csv')
    csv_file = open(csv_path, "r")
    csv_data = csv.DictReader(csv_file)

    # Convert it into a dictionary and pass it out.
    return dict(
        (int(r['year']), float(r['value'])) for r in csv_data
    )


cpi_by_year = _get_cpi_dict()
