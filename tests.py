#! /usr/bin/env python
# -*- coding: utf-8 -*-
import cpi
import unittest
from cpi.errors import CPIDoesNotExist


class CPITest(unittest.TestCase):

    def test_get(self):
        self.assertEqual(cpi.get(1950), 24.1)
        self.assertEqual(cpi.get(2000), 172.2)
        with self.assertRaises(CPIDoesNotExist):
            cpi.get(1900)

    def test_inflate(self):
        self.assertEqual(cpi.inflate(100, 1950), 1017.0954356846472)
        self.assertEqual(cpi.inflate(100, 1950, to=1960), 122.82157676348547)

    def test_deflate(self):
        self.assertEqual(cpi.inflate(1017.0954356846472, 2017, to=1950), 100)
        self.assertEqual(cpi.inflate(122.82157676348547, 1960, to=1950), 100)


if __name__ == '__main__':
    unittest.main()
