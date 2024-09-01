"""Download the latest annual Consumer Price Index (CPI) dataset."""

import io
import logging
import sqlite3
import typing
from pathlib import Path

import pandas as pd
import requests

from cpi import parsers

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Downloader:
    """Download the latest data."""

    THIS_DIR: Path = Path(__file__).parent.absolute()
    FILE_LIST: typing.List[str] = [
        "cu.area",
        "cu.item",
        "cu.period",
        "cu.periodicity",
        "cu.series",
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

    def rm(self) -> None:
        """Remove any existing files."""
        db_path = self.THIS_DIR / "cpi.db"
        if db_path.exists():
            logger.debug("Clearing database")
            # Drop all tables in the database
            conn = self.get_db_conn()
            table_list = [
                "areas",
                "items",
                "periods",
                "periodicities",
                "series",
                "indexes",
            ]
            for t in table_list:
                conn.execute(f"DROP TABLE IF EXISTS '{t}';")
            conn.close()
            self.vaccum()

    def vaccum(self) -> None:
        """Vaccum the database."""
        conn = self.get_db_conn()
        conn.execute("VACUUM;")
        conn.close()

    def update(self) -> None:
        """Update the Consumer Price Index dataset that powers this library."""
        # Delete existing files
        self.rm()

        # Load the default files
        self.load_file_list(self.FILE_LIST)

        # Process flat CSVs we can use in our API
        self.process_files()

        # Drop the raw files now that we don't need them
        self.drop_file_list(self.FILE_LIST)

    def get_db_conn(self) -> sqlite3.Connection:
        """Connect to db."""
        db_path = self.THIS_DIR / "cpi.db"
        return sqlite3.connect(db_path)

    def process_files(self) -> None:
        """Process the raw data files into simplified tables."""
        logger.info("Parsing data files from the BLS")
        conn = self.get_db_conn()

        areas = parsers.ParseArea().get_df()
        areas.to_sql("areas", conn, if_exists="replace", index=False)

        items = parsers.ParseItem().get_df()
        items.to_sql("items", conn, if_exists="replace", index=False)

        periods = parsers.ParsePeriod().get_df()
        periods.to_sql("periods", conn, if_exists="replace", index=False)

        periodicities = parsers.ParsePeriodicity().get_df()
        periodicities.to_sql("periodicities", conn, if_exists="replace", index=False)

        series = parsers.ParseSeries().get_df()
        series.to_sql("series", conn, if_exists="replace", index=False)

        index = parsers.ParseIndex().get_df()
        index.to_sql("indexes", conn, if_exists="replace", index=False)

        conn.close()

    def load_file_list(self, file_list: typing.List[str]) -> None:
        # Download the TSVs
        logger.debug(f"Downloading {len(file_list)} files from the BLS")
        df_list = {name: self.get_df(name) for name in file_list}

        # Insert the TSVs
        logger.debug("Loading data into SQLite database")
        conn = self.get_db_conn()

        # Load them one by one
        for name, df in df_list.items():
            logger.debug(f"- {name}")
            df.to_sql(name, conn, if_exists="replace", index=False)

        # Close connection
        conn.close()

    def drop_file_list(self, file_list: typing.List[str]) -> None:
        """Drop the raw data from BLS."""
        logger.debug("Dropping data from SQLite database")

        # Connect
        conn = self.get_db_conn()

        # Do tables one by one
        for name in file_list:
            logger.debug(f"- {name}")
            conn.execute(f"DROP TABLE '{name}';")

        # Close the connection
        conn.close()

        # Vaccum the database
        self.vaccum()

    def get_df(self, file: str) -> pd.DataFrame:
        """Download TSV file from the BLS."""
        # Download it
        url = f"https://download.bls.gov/pub/time.series/cu/{file}"
        logger.debug(f" - {url}")
        headers = {
            "User-Agent": "b@palewi.re",
        }
        response = requests.get(url, headers=headers, timeout=30)

        # Make sure the response is legit
        try:
            assert response.ok
        except AssertionError:
            logger.error(f"Error downloading {url}")
            logger.error(f"Response: {response.text}")
            raise AssertionError(f"Error downloading {url} - {response.text}")

        # Read in the contents as an io.StringIO object
        df = pd.read_csv(io.StringIO(response.text), sep="\t")

        # .strip() every value in the dataframe
        df_obj = df.select_dtypes("object")
        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

        # .strip every column name
        df.columns = [col.strip() for col in df.columns]

        # Clean file
        df.drop([None], axis=1, inplace=True, errors="ignore")

        # Pass it back
        return df


if __name__ == "__main__":
    Downloader().update()
