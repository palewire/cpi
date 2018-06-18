#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download, parse and prepare the latest annual Consumer Price Index (CPI) dataset.

Source: The Bureau of Labor Statistics at the U.S. Department of Labor.
Survey: CPI-All Urban Consumers (Current Series)
        All items in U.S. city average, all urban consumers, not seasonally adjusted
Identifer: CUUR0000SA0
"""
import os
import csv
import requests
from datetime import date


class Downloader(object):
    THIS_DIR = os.path.dirname(__file__)

    def update(self):
        """
        Update the Consumer Price Index dataset that powers this library.
        """
        self.get_tsv()
        self.parse_tsv()

    def get_tsv(self):
        """
        Download the latest annual Consumer Price Index (CPI) dataset.
        """
        bls_url = "https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems"
        response = requests.get(bls_url)
        with open(os.path.join(self.THIS_DIR, 'data.tsv'), 'w') as f:
            f.write(response.text)

    def parse_periodtype(self, row):
        """
        Accepts a row from the raw BLS data. Returns a string classifying the period.
        """
        period_types = dict(("M{:02d}".format(i), "monthly") for i in range(1, 13))
        period_types["M13"] = "annual"
        return period_types[row['period']]

    def parse_date(self, row):
        """
        Accepts a row from the raw BLS data. Returns a Python date object based on its period.
        """
        # If it is annual data, return it as Jan. 1 of that year.
        if row['period'] == 'M13':
            return date(row['year'], 1, 1)
        # If it is month data, return it as the first day of the month.
        else:
            return date(row['year'], int(row['period'].replace("M", "")), 1)

    def parse_tsv(self):
        """
        Parse the downloaded fixed-width file from the BLS and convert it into a CSV.
        """
        # Get the raw data
        input = os.path.join(self.THIS_DIR, "data.tsv")
        reader = csv.DictReader(open(input, 'r'), delimiter="\t")

        # Figure out where we're going to store the clean data
        output = os.path.join(self.THIS_DIR, "data.csv")
        writer = csv.DictWriter(
            open(output, 'w'),
            fieldnames=["series", "period", "period_type", "year", "date", "value"]
        )
        writer.writeheader()

        # Loop through it
        for row in reader:
            # Clean it up
            d = dict(
                series=row['series_id'].strip(),
                period=row['period'].strip(),
                year=int(row['year'].strip()),
                value=float(row['value'].strip())
            )
            # Only keep the annual totals (M13) from the series we care about.
            if d['series'] == 'CUUR0000SA0':
                d['period_type'] = self.parse_periodtype(d)
                d['date'] = self.parse_date(d)
                writer.writerow(d)


if __name__ == '__main__':
    Downloader().update()
