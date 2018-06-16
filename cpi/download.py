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


class Downloader(object):
    this_dir = os.path.dirname(__file__)

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
        with open(os.path.join(self.this_dir, 'data.tsv'), 'w') as f:
            f.write(response.text)

    def parse_tsv(self):
        """
        Parse the downloaded fixed-width file from the BLS and convert it into a CSV.
        """
        # Get the raw data
        input = os.path.join(self.this_dir, "data.tsv")
        reader = csv.DictReader(open(input, 'r'), delimiter="\t")

        # Figure out where we're going to store the clean data
        output = os.path.join(self.this_dir, "data.csv")
        writer = csv.DictWriter(
            open(output, 'w'),
            fieldnames=["series", "period", "year", "value"]
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
            if d['series'] == 'CUUR0000SA0' and d['period'] == 'M13':
                writer.writerow(d)


if __name__ == '__main__':
    Downloader().update()
