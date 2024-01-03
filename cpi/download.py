"""Download the latest annual Consumer Price Index (CPI) dataset."""
import csv
import logging
import sqlite3
import typing
from pathlib import Path

import pandas as pd
import requests

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

    def get_data_dir(self) -> Path:
        """Return the directory Path where data will be stored."""
        data_dir = self.THIS_DIR / "data"
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir

    def rm(self):
        """Remove any existing files."""
        db_path = self.THIS_DIR / "cpi.db"
        if db_path.exists():
            logger.debug(f"Deleting {db_path}")
            db_path.unlink()
        data_dir = self.get_data_dir()
        for f in data_dir.glob(".csv"):
            logger.debug(f"Deleting {f}")
            f.unlink()
        for f in data_dir.glob(".tsv"):
            logger.debug(f"Deleting {f}")
            f.unlink()

    def update(self):
        """Update the Consumer Price Index dataset that powers this library."""
        # Delete existing files
        self.rm()

        # Download the TSVs
        logger.debug(f"Downloading {len(self.FILE_LIST)} files from the BLS")
        [self.get_tsv(file) for file in self.FILE_LIST]

        # Insert the TSVs
        logger.debug("Loading data into SQLite database")
        [self.insert_tsv(file) for file in self.FILE_LIST]

    def insert_tsv(self, file: str):
        """Load the provided TSV file."""
        # Connect to db
        db_path = self.THIS_DIR / "cpi.db"
        conn = sqlite3.connect(db_path)

        # Read file
        logger.debug(f" - {file}")
        csv_path = self.get_data_dir() / f"{file}.csv"
        csv_reader = list(csv.DictReader(open(csv_path)))

        # Convert it to a DataFrame
        df = pd.DataFrame(csv_reader)
        df.drop([None], axis=1, inplace=True, errors="ignore")

        # Write file to db
        df.to_sql(file, conn, if_exists="replace", index=False)

        # Close connection
        conn.close()

    def get_tsv(self, file: str):
        """Download TSV file from the BLS."""
        # Download it
        url = f"https://download.bls.gov/pub/time.series/cu/{file}"
        logger.debug(f" - {url}")
        tsv_path = self.get_data_dir() / f"{file}.tsv"
        headers = {
            "User-Agent": "b@palewi.re",
        }
        response = requests.get(url, headers=headers, timeout=30)
        try:
            assert response.ok
        except AssertionError:
            logger.error(f"Error downloading {url}")
            logger.error(f"Response: {response.text}")
            raise AssertionError(f"Error downloading {url}")
        with open(tsv_path, "w") as fp:
            fp.write(response.text)

        # Convert it to csv
        with open(tsv_path) as in_file:
            reader = csv.reader(in_file, delimiter="\t")
            csv_path = self.get_data_dir() / f"{file}.csv"
            with open(csv_path, "w") as out_file:
                writer = csv.writer(out_file)
                for row in reader:
                    writer.writerow([cell.strip() for cell in row])


if __name__ == "__main__":
    Downloader().update()
