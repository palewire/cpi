#! /usr/bin/env python
# -*- coding: utf-8 -*-
import cpi
import pandas
import unittest
import warnings
from cpi.errors import CPIDoesNotExist
from datetime import date, datetime


class CPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.TEST_YEAR_EARLIER = 1950
        cls.TEST_YEAR_MIDDLE = 1960
        cls.TEST_YEAR_LATER = 2000
        cls.END_YEAR = 2018
        cls.EARLIEST_YEAR = 1913
        cls.LATEST_YEAR = 2017
        cls.DOLLARS = 100

    def test_get(self):
        self.assertEqual(cpi.get(CPITest.TEST_YEAR_EARLIER), 24.1)
        self.assertEqual(cpi.get(CPITest.TEST_YEAR_LATER), 172.2)
        with self.assertRaises(CPIDoesNotExist):
            cpi.get(1900)
        with self.assertRaises(CPIDoesNotExist):
            cpi.get(date(1900, 1, 1))

    def test_get_value_error(self):
        with self.assertRaises(ValueError):
            cpi.get(1900.1)
            cpi.get(datetime.now())

    def test_inflate_years(self):
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, CPITest.TEST_YEAR_EARLIER),
                1017.0954356846472)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, CPITest.TEST_YEAR_EARLIER, to=2017),
                1017.0954356846472)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, CPITest.TEST_YEAR_EARLIER,
                    to=CPITest.TEST_YEAR_MIDDLE),
                122.82157676348547)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, CPITest.TEST_YEAR_EARLIER,
                    to=CPITest.TEST_YEAR_EARLIER),
                CPITest.DOLLARS)

    def test_inflate_months(self):
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, date(CPITest.TEST_YEAR_EARLIER, 1, 1)),
                1070.587234042553)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, date(CPITest.TEST_YEAR_EARLIER, 1, 11)),
                1070.587234042553)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS,
                    datetime(CPITest.TEST_YEAR_EARLIER, 1, 1)),
                1070.587234042553)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, date(CPITest.TEST_YEAR_EARLIER, 1, 1),
                    to=date(CPITest.END_YEAR, 1, 1)), 1054.7531914893618)
        self.assertEqual(
                cpi.inflate(
                    CPITest.DOLLARS, date(CPITest.TEST_YEAR_EARLIER, 1, 1),
                    to=date(CPITest.TEST_YEAR_MIDDLE, 1, 1)),
                124.68085106382979)

    def test_inflate_months_total(self):
        d = pandas.read_csv('cpi-data.csv')

        def calculate_inflation(start_year):
            bi = d[d['Year'] == start_year]['Jan'].values[0]
            ei = d[d['Year'] == CPITest.END_YEAR]['Jan'].values[0]
            return (CPITest.DOLLARS / bi) * ei

        for year in range(CPITest.TEST_YEAR_EARLIER, CPITest.END_YEAR):
            self.assertTrue(
                abs(
                    cpi.inflate(
                        CPITest.DOLLARS,
                        date(year, 1, 1),
                        to=date(CPITest.END_YEAR, 1, 1)) -
                    calculate_inflation(year)) < 0.001)

    def test_deflate(self):
        self.assertEqual(
                cpi.inflate(
                    1017.0954356846472, 2017, to=CPITest.TEST_YEAR_EARLIER),
                CPITest.DOLLARS)
        self.assertEqual(
                cpi.inflate(
                    122.82157676348547,
                    CPITest.TEST_YEAR_MIDDLE,
                    to=CPITest.TEST_YEAR_EARLIER),
                CPITest.DOLLARS)

    def test_mismatch(self):
        with self.assertRaises(TypeError):
            cpi.inflate(
                CPITest.DOLLARS,
                CPITest.TEST_YEAR_EARLIER,
                to=date(CPITest.TEST_YEAR_LATER, 1, 1))
        with self.assertRaises(TypeError):
            cpi.inflate(
                CPITest.DOLLARS,
                date(CPITest.TEST_YEAR_LATER, 1, 1),
                to=CPITest.TEST_YEAR_EARLIER)

    def test_earliest_year(self):
        self.assertEqual(cpi.EARLIEST_YEAR, CPITest.EARLIEST_YEAR)

    def test_latest_year(self):
        self.assertEqual(cpi.LATEST_YEAR, CPITest.LATEST_YEAR)

    def test_earliest_month(self):
        self.assertEqual(
                cpi.EARLIEST_MONTH, date(CPITest.EARLIEST_YEAR, 1, 1))

    def test_latest_month(self):
        self.assertEqual(cpi.LATEST_MONTH, date(CPITest.END_YEAR, 5, 1))

    def test_warning(self):
        warnings.warn(cpi.StaleDataWarning())


if __name__ == '__main__':
    unittest.main()
