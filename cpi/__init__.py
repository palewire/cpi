#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)
"""
import warnings
from datetime import date, datetime

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
if DAYS_SINCE_LATEST_YEAR > (365*2.25) or DAYS_SINCE_LATEST_MONTH > 60:
    warnings.warn(StaleDataWarning())


def get(year_or_month):
    """
    Returns the CPI value for a given year.
    """
    if isinstance(year_or_month, int):
        try:
            return cpi_by_year[year_or_month]
        except KeyError:
            raise CPIDoesNotExist("CPI value not found for {}".format(year_or_month))
    elif isinstance(year_or_month, date):
        # If it's not set to the first day of the month, we should do that now.
        if year_or_month.day != 1:
            year_or_month = year_or_month.replace(day=1)
        try:
            return cpi_by_month[year_or_month]
        except KeyError:
            raise CPIDoesNotExist("CPI value not found for {}".format(year_or_month))
    else:
        raise ValueError("Only integers and date objects are accepted.")


def inflate(value, year_or_month, to=None):
    """
    Returns a dollar value adjusted for inflation.

    You must submit the value, followed by the year or month its from.

    Years should be submitted as integers. Months as datetime.date objects.

    By default, the input is adjusted to the most recent year or month available from the CPI.

    If you'd like to adjust to a different year or month, submit it to the optional `to` keyword argument.

    Yearly data can only be updated to other years. Monthly data can only be updated to other months.
    """
    # If the two dates match, just return the value unadjusted
    if year_or_month == to:
        return value

    # Figure out the 'to' date if it has not been provided
    if not to:
        if isinstance(year_or_month, int):
            to = LATEST_YEAR
        elif isinstance(year_or_month, (date, datetime)):
            to = LATEST_MONTH

    # If a datetime has been provided, shave it down to a date.
    if isinstance(year_or_month, datetime):
        year_or_month = year_or_month.date()

    # Make sure the two dates are the same type
    if type(year_or_month) != type(to):
        raise TypeError("Years can only be converted to other years. Months only to other months.")

    # Otherwise, let's do the math.
    # The input value is multiplied by the CPI of the target year,
    # then divided into the CPI from the source year.
    return (value * get(to)) / float(get(year_or_month))


def update():
    """
    Updates the core Consumer Price Index dataset at the core of this library.

    Requires an Internet connection.
    """
    Downloader().update()
