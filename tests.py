#! /usr/bin/env python
# -*- coding: utf-8 -*-
import cpi
import warnings
import unittest
import pandas as pd
from datetime import date, datetime
from cpi.errors import CPIDoesNotExist


class CPITest(unittest.TestCase):

    def test_get(self):
        self.assertEqual(cpi.get(1950), 24.1)
        self.assertEqual(cpi.get(2000), 172.2)
        with self.assertRaises(CPIDoesNotExist):
            cpi.get(1900)
        with self.assertRaises(CPIDoesNotExist):
            cpi.get(date(1900, 1, 1))

    def test_get_value_error(self):
        with self.assertRaises(ValueError):
            cpi.get(1900.1)
            cpi.get(datetime.now())
            cpi.get(3000)

    def test_inflate_years(self):
        self.assertEqual(cpi.inflate(100, 1950), 1017.0954356846472)
        self.assertEqual(cpi.inflate(100, 1950, to=2017), 1017.0954356846472)
        self.assertEqual(cpi.inflate(100, 1950, to=1960), 122.82157676348547)
        self.assertEqual(cpi.inflate(100, 1950, to=1950), 100)

    def test_inflate_months(self):
        self.assertEqual(cpi.inflate(100, date(1950, 1, 1)), 1070.587234042553)
        self.assertEqual(cpi.inflate(100, date(1950, 1, 11)), 1070.587234042553)
        self.assertEqual(cpi.inflate(100, datetime(1950, 1, 1)), 1070.587234042553)
        self.assertEqual(cpi.inflate(100, date(1950, 1, 1), to=date(2018, 1, 1)), 1054.7531914893618)
        self.assertEqual(cpi.inflate(100, date(1950, 1, 1), to=date(1960, 1, 1)), 124.68085106382979)

    def test_deflate(self):
        self.assertEqual(cpi.inflate(1017.0954356846472, 2017, to=1950), 100)
        self.assertEqual(cpi.inflate(122.82157676348547, 1960, to=1950), 100)

    def test_numpy_dtypes(self):
        self.assertEqual(
            cpi.get(pd.np.int64(1950)),
            cpi.get(1950)
        )
        self.assertEqual(
            cpi.inflate(100, pd.np.int32(1950)),
            cpi.inflate(100, 1950),
        )
        self.assertEqual(
            cpi.inflate(100, pd.np.int64(1950), to=pd.np.int64(1960)),
            cpi.inflate(100, 1950, to=1960),
        )
        self.assertEqual(
            cpi.inflate(100, pd.np.int64(1950), to=pd.np.int32(1960)),
            cpi.inflate(100, 1950, to=1960),
        )
        self.assertEqual(
            cpi.inflate(100, pd.np.int64(1950), to=1960),
            cpi.inflate(100, 1950, to=1960),
        )
        self.assertEqual(
            cpi.inflate(100, pd.to_datetime("1950-07-01"), to=pd.to_datetime("1960-07-01")),
            cpi.inflate(100, date(1950, 7, 1), to=date(1960, 7, 1))
        )

    def test_mismatch(self):
        with self.assertRaises(TypeError):
            cpi.inflate(100, 1950, to=date(2000, 1, 1))
        with self.assertRaises(TypeError):
            cpi.inflate(100, date(2000, 1, 1), to=1950)

    def test_earliest_year(self):
        self.assertEqual(cpi.EARLIEST_YEAR, 1913)

    def test_latest_year(self):
        self.assertEqual(cpi.LATEST_YEAR, 2017)

    def test_earliest_month(self):
        self.assertEqual(cpi.EARLIEST_MONTH, date(1913, 1, 1))

    def test_latest_month(self):
        self.assertEqual(cpi.LATEST_MONTH, date(2018, 5, 1))

    def test_warning(self):
        warnings.warn(cpi.StaleDataWarning())

    def test_pandas(self):
        df = pd.read_csv("test.csv")
        df['ADJUSTED'] = df.apply(lambda x: cpi.inflate(x.MEDIAN_HOUSEHOLD_INCOME, x.YEAR), axis=1)
        df = df.set_index("YEAR")
        self.assertEqual(
            cpi.inflate(df.at[1984, 'MEDIAN_HOUSEHOLD_INCOME'], 1984),
            df.at[1984, 'ADJUSTED']
        )

if __name__ == '__main__':
    unittest.main()
