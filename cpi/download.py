"""Download the latest annual Consumer Price Index (CPI) dataset."""
import io
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

    def rm(self) -> None:
        """Remove any existing files."""
        db_path = self.THIS_DIR / "cpi.db"
        if db_path.exists():
            logger.debug(f"Deleting {db_path}")
            db_path.unlink()

    def update(self) -> None:
        """Update the Consumer Price Index dataset that powers this library."""
        # Delete existing files
        self.rm()

        # Download the TSVs
        logger.debug(f"Downloading {len(self.FILE_LIST)} files from the BLS")
        df_list = {name: self.get_df(name) for name in self.FILE_LIST}

        # Insert the TSVs
        logger.debug("Loading data into SQLite database")

        # Connect to db
        db_path = self.THIS_DIR / "cpi.db"
        conn = sqlite3.connect(db_path)

        # Load them one by one
        for name, df in df_list.items():
            logger.debug(f"- {name}")
            df.to_sql(name, conn, if_exists="replace", index=False)

        # Close connection
        conn.close()

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
        df.columns = [c.strip() for c in df.columns]

        # Clean file
        df.drop([None], axis=1, inplace=True, errors="ignore")

        # Pass it back
        return df


if __name__ == "__main__":
    Downloader().update()
