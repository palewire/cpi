#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download the latest annual Consumer Price Index (CPI) dataset.
"""
import os
import csv
import logging
import requests
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Downloader(object):
    THIS_DIR = os.path.dirname(__file__)
    FILE_LIST = [
        "cu.series",
        "cu.data.1.AllItems",
    ]

    def update(self):
        """
        Update the Consumer Price Index dataset that powers this library.
        """
        logger.debug("Downloading {} files from the BLS".format(len(self.FILE_LIST)))
        [self.get_tsv(file) for file in self.FILE_LIST]

    def get_tsv(self, file):
        """
        Download TSV file from the BLS.
        """
        # Download it
        url = "https://download.bls.gov/pub/time.series/cu/{}".format(file)
        logger.debug(" - {}".format(url))

        tsv_path = os.path.join(self.THIS_DIR, '{}.tsv'.format(file))
        response = requests.get(url)
        with open(tsv_path, 'w') as f:
            f.write(response.text)

        # Convert it to csv
        reader = csv.reader(open(tsv_path, 'r'), delimiter="\t")
        csv_path = os.path.join(self.THIS_DIR, '{}.csv'.format(file))
        writer = csv.writer(open(csv_path, 'w'))
        for row in reader:
            writer.writerow([cell.strip() for cell in row])


if __name__ == '__main__':
    Downloader().update()
