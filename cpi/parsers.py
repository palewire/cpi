#! /usr/bin/env python
"""
Parse and prepare the Consumer Price Index (CPI) dataset.
"""

import logging
import os
import sqlite3

import pandas as pd

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BaseParser:
    THIS_DIR = os.path.dirname(__file__)

    def get_file(self, file):
        """
        Returns the CPI data file provided as a list of dictionaries.
        """
        # Connect to database
        db_path = os.path.join(self.THIS_DIR, "cpi.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query this file
        query = cursor.execute(f'SELECT * FROM "{file}"')
        columns = [d[0] for d in query.description]
        result_list = [dict(zip(columns, r)) for r in query.fetchall()]

        # Close database connection
        cursor.close()
        cursor.connection.close()

        # Return data
        return result_list

    def parse(self) -> list[dict]:
        raise NotImplementedError

    def get_df(self) -> pd.DataFrame:
        """Convert the database table to a polished dataframe."""
        return pd.DataFrame(self.parse()).drop_duplicates()


class ParseArea(BaseParser):
    """Parse the raw list of CPI areas."""

    def parse(self):
        """
        Returns a list Area objects.
        """
        logger.debug("Parsing area file")
        object_list = []
        for row in self.get_file("cu.area"):
            d = dict(
                id=row["area_code"],
                code=row["area_code"],
                name=row["area_name"],
            )
            object_list.append(d)
        return object_list


class ParseItem(BaseParser):
    """
    Parses the raw list of CPI items.
    """

    def parse(self):
        """
        Returns a list Area objects.
        """
        logger.debug("Parsing item file")
        object_list = []
        for row in self.get_file("cu.item"):
            d = dict(
                id=row["item_code"],
                code=row["item_code"],
                name=row["item_name"],
            )
            object_list.append(d)
        return object_list


class ParsePeriod(BaseParser):
    """
    Parses the raw list of CPI periods.
    """

    def parse(self):
        """
        Returns a list Area objects.
        """
        logger.debug("Parsing period file")
        object_list = []
        for row in self.get_file("cu.period"):
            d = dict(
                id=row["period"],
                code=row["period"],
                abbreviation=row["period_abbr"],
                name=row["period_name"],
            )
            object_list.append(d)
        return object_list


class ParsePeriodicity(BaseParser):
    """
    Parses the raw list of CPI periodicities.
    """

    def parse(self):
        """
        Returns a list Periodicity objects.
        """
        logger.debug("Parsing periodicity file")
        object_list = []
        for row in self.get_file("cu.periodicity"):
            d = dict(
                id=row["periodicity_code"],
                code=row["periodicity_code"],
                name=row["periodicity_name"],
            )
            object_list.append(d)
        return object_list


class ParseSeries(BaseParser):
    """
    Parses the raw list of CPI series from the BLS.
    """

    SURVEYS = {
        "CU": "All urban consumers",
        "CW": "Urban wage earners and clerical workers",
    }

    def parse_id(self, id):
        return dict(
            survey_code=id[:2],
            seasonal_code=id[2:3],
            periodicity_code=id[3:4],
            area_code=id[4:8],
            item_code=id[8:],
        )

    def parse(self):
        """Parse the data."""
        logger.debug("Parsing series file")
        object_list = []
        for row in self.get_file("cu.series"):
            parsed_id = self.parse_id(row["series_id"])
            d = dict(
                id=row["series_id"],
                title=row["series_title"],
                survey=self.SURVEYS[parsed_id["survey_code"]],
                seasonally_adjusted=row["seasonal"] == "S",
                periodicity=row["periodicity_code"],
                area=row["area_code"],
                items=row["item_code"],
            )
            object_list.append(d)
        return object_list


class ParseIndex(BaseParser):
    """Parse indexes."""

    FILE_LIST = [
        "cu.data.0.Current",
        "cu.data.1.AllItems",
        "cu.data.2.Summaries",
        "cu.data.3.AsizeNorthEast",
        "cu.data.4.AsizeNorthCentral",
        "cu.data.5.AsizeSouth",
        "cu.data.6.AsizeWest",
        "cu.data.7.OtherNorthEast",
        "cu.data.8.OtherNorthCentral",
        "cu.data.9.OtherSouth",
        "cu.data.10.OtherWest",
        "cu.data.11.USFoodBeverage",
        "cu.data.12.USHousing",
        "cu.data.13.USApparel",
        "cu.data.14.USTransportation",
        "cu.data.15.USMedical",
        "cu.data.16.USRecreation",
        "cu.data.17.USEducationAndCommunication",
        "cu.data.18.USOtherGoodsAndServices",
        "cu.data.19.PopulationSize",
        "cu.data.20.USCommoditiesServicesSpecial",
    ]

    def parse(self):
        logger.debug("Parsing index files")
        # Loop through all the files ...
        object_list = []
        for file in self.FILE_LIST:
            # ... and for each file ...
            for row in self.get_file(file):
                # Create an object
                d = dict(
                    series=row["series_id"],
                    year=int(row["year"]),
                    period=row["period"],
                    value=float(row["value"]),
                )
                object_list.append(d)
        return object_list
