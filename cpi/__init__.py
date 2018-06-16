#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)
"""
from .data import cpi_by_year
from .download import Downloader
from .errors import CPIDoesNotExist


def get(year):
    """
    Returns the CPI value for a given year.
    """
    try:
        return cpi_by_year[year]
    except KeyError:
        raise CPIDoesNotExist("CPI value not found for {}".format(year))


def inflate(value, year, to=None):
    """
    Returns a dollar value adjusted for inflation.

    You must submit the value, followed by the year its from.

    By default, the input is adjusted to the most recent year available from the CPI.

    If you'd like to adjust to a different year, submit it as an integer to the optional `to` keyword argument.
    """
    # Figure out the year we're inflating to.
    if not to:
        # If an input hasn't been provided, we'll use the maximum year
        max_year = max(cpi_by_year.keys())
        to = max_year

    # If the two years match, just return the value unadjusted
    if year == to:
        return value

    # Otherwise, let's do the math.
    # The input value is multiplied by the CPI of the target year,
    # Then divided into the cpi from the source year.
    return (value * get(to)) / float(get(year))


def update():
    """
    Updates the core Consumer Price Index dataset at the core of this library.

    Requires an Internet connection.
    """
    Downloader().update()
