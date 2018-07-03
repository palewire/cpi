import os
import csv


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
