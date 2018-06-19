#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)
"""
import warnings
from datetime import date
from .download import Downloader
from .data import cpi_by_year, cpi_by_month
from .errors import CPIDoesNotExist, StaleDataWarning


# Establish the range of data available
MONTHS = cpi_by_month.keys()
EARLIEST_MONTH = min(MONTHS)
LATEST_MONTH = max(MONTHS)

YEARS = cpi_by_year.keys()
EARLIEST_YEAR = min(YEARS)
LATEST_YEAR = max(YEARS)

# Figure out how out of date you are
DAYS_SINCE_LATEST_MONTH = (date.today() - LATEST_MONTH).days
DAYS_SINCE_LATEST_YEAR = (date.today() - date(LATEST_YEAR, 1, 1)).days

# If it's more than two and a half years out of date, raise a warning.
if DAYS_SINCE_LATEST_YEAR > (365*2.5) or DAYS_SINCE_LATEST_MONTH > 90:
    warnings.warn(StaleDataWarning())


def get(year):
    """
    Returns the CPI value for a given year.
    """
    if isinstance(year, int):
        try:
            return cpi_by_year[year]
        except KeyError:
            raise CPIDoesNotExist("CPI value not found for {}".format(year))
    else:
        raise ValueError("Only integers and date objects are accepted.")


def inflate(value, year, to=LATEST_YEAR):
    """
    Returns a dollar value adjusted for inflation.

    You must submit the value, followed by the year its from.

    By default, the input is adjusted to the most recent year available from the CPI.

    If you'd like to adjust to a different year, submit it as an integer to the optional `to` keyword argument.
    """
    # If the two years match, just return the value unadjusted
    if year == to:
        return value

    # Otherwise, let's do the math.
    # The input value is multiplied by the CPI of the target year,
    # then divided into the CPI from the source year.
    return (value * get(to)) / float(get(year))


def update():
    """
    Updates the core Consumer Price Index dataset at the core of this library.

    Requires an Internet connection.
    """
    Downloader().update()
