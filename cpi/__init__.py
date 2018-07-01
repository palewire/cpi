#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)
"""
import numbers
import warnings
from datetime import date, datetime

from .download import Downloader
from .data import cpi_by_year, cpi_by_month
from .errors import CPIDoesNotExist, StaleDataWarning

# Configure a logger
import logging
logger = logging.getLogger(__name__).addHandler(logging.NullHandler())

# set the default series to the CPI-U
DEFAULT_SERIES = "CUUR0000SA0"

# Establish the range of data available
MONTHS = cpi_by_month[DEFAULT_SERIES].keys()
EARLIEST_MONTH = min(MONTHS)
LATEST_MONTH = max(MONTHS)

YEARS = cpi_by_year[DEFAULT_SERIES].keys()
EARLIEST_YEAR = min(YEARS)
LATEST_YEAR = max(YEARS)

# Figure out how out of date you are
DAYS_SINCE_LATEST_MONTH = (date.today() - LATEST_MONTH).days
DAYS_SINCE_LATEST_YEAR = (date.today() - date(LATEST_YEAR, 1, 1)).days

# If it's more than two and a half years out of date, raise a warning.
if DAYS_SINCE_LATEST_YEAR > (365*2.25) or DAYS_SINCE_LATEST_MONTH > 90:
    warnings.warn(StaleDataWarning())
    logger.warn("CPI data is out of date. To accurately inflate to today's dollars, you must run `cpi.update()`.")


def get(year_or_month, series=DEFAULT_SERIES):
    """
    Returns the CPI value for a given year.
    """
    # Pull the appropriate data dict depending on the input type.
    if isinstance(year_or_month, numbers.Integral):
        data_dict = cpi_by_year
    elif isinstance(year_or_month, date):
        # If it's not set to the first day of the month, we should do that now.
        if year_or_month.day != 1:
            year_or_month = year_or_month.replace(day=1)
        data_dict = cpi_by_month
    else:
        raise ValueError("Only integers and date objects are accepted.")

    # Pull the series from the data dict
    try:
        series_dict = data_dict[series]
    except KeyError:
        raise CPIDoesNotExist("CPI series {} not found".format(series))

    # Pull the value from the series_dict
    try:
        return series_dict[year_or_month]
    except KeyError:
        raise CPIDoesNotExist("CPI value not found for {}".format(year_or_month))


def inflate(value, year_or_month, to=None, series=DEFAULT_SERIES):
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
        if isinstance(year_or_month, (date, datetime)):
            to = LATEST_MONTH
        else:
            to = LATEST_YEAR
    # Otherwise sanitize it
    else:
        if isinstance(to, numbers.Integral):
            to = int(to)
        elif isinstance(to, datetime):
            to = to.date()

    # Sanitize the year_or_month
    if isinstance(year_or_month, numbers.Integral):
        # We need to make sure that int64, int32 and ints
        # are the same type for the comparison to come.
        year_or_month = int(year_or_month)
    # If a datetime has been provided, shave it down to a date.
    elif isinstance(year_or_month, datetime):
        year_or_month = year_or_month.date()

    # Make sure the two dates are the same type
    if type(year_or_month) != type(to):
        raise TypeError("Years can only be converted to other years. Months only to other months.")

    # Otherwise, let's do the math.
    # The input value is multiplied by the CPI of the target year,
    # then divided into the CPI from the source year.
    source_index = get(year_or_month, series=series)
    target_index = get(to, series=series)
    return (value * target_index) / float(source_index)


def update():
    """
    Updates the core Consumer Price Index dataset at the core of this library.

    Requires an Internet connection.
    """
    Downloader().update()
