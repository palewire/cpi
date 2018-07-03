# cpi

A Python library that quickly adjusts U.S. dollars for inflation using the Consumer Price Index (CPI).

[![Build Status](https://travis-ci.org/datadesk/cpi.svg?branch=master)](https://travis-ci.org/datadesk/cpi)

## Installation

The library can be installed from the Python Package Index with any of the standard Python installation tools.

Like pipenv:

```bash
$ pipenv install cpi
```

Or pip:

```bash
$ pip install cpi
```

## Working with Python

Adjusting for inflation is as simple as providing a dollar value followed by the year it is from to  the `inflate` method. By default it is adjusted to its value in the most recent year available.

```python
>>> import cpi
>>> cpi.inflate(100, 1950)
1017.0954356846472
```

If you'd like to adjust to a different year, submit it as an integer to the optional `to` keyword argument.

```python
>>> cpi.inflate(100, 1950, to=1960)
122.82157676348547
```

You can also adjust month to month. You should submit the months as `datetime.date` objects.

```python
>>> from datetime import date
>>> cpi.inflate(100, date(1950, 1, 1), to=date(2018, 1, 1))
1054.7531914893618
```

If you'd like to retrieve the CPI value itself for any year, use the `get` method.

```python
>>> cpi.get(1950)
24.1
```

You can also do that by month.

```python
>>> cpi.get(date(1950, 1, 1))
23.5
```

That's it!

## Working with the command line

The Python package also installs a command-line interface for `inflate` that is available on the terminal.

It works the same as the Python library. First give it a value. Then a source year. By default it is adjusted to its value in the most recent year available.

```bash
$ inflate 100 1950
1017.09543568
```

If you'd like to adjust to a different year, submit it as an integer to the `--to` option.

```bash
$ inflate 100 1950 --to=1960
122.821576763
```

You can also adjust month to month. You should submit the months as parseable date strings.

```
$ inflate 100 1950-01-01 --to=2018-01-01
1054.75319149
```

Here are all its options.

```bash
$ inflate --help
Usage: inflate [OPTIONS] VALUE YEAR_OR_MONTH

  Returns a dollar value adjusted for inflation.

Options:
  --to TEXT      The year or month to adjust the value to.
  --series TEXT  The CPI data series used for the conversion. The default is the CPI-U.
  --help         Show this message and exit.
```

## Working with pandas

An inflation-adjusted column can quickly be added to a pandas DataFrame using the `apply` method. Here is an example using data tracking the median household income in the United States from [The Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/MEHOINUSA646N).

```python
>>> import cpi
>>> import pandas as pd
>>> df = pd.read("test.csv")
>>> df.head()
   YEAR  MEDIAN_HOUSEHOLD_INCOME
0  1984                    22415
1  1985                    23618
2  1986                    24897
3  1987                    26061
4  1988                    27225
>>> df['ADJUSTED'] = df.apply(lambda x: cpi.inflate(x.MEDIAN_HOUSEHOLD_INCOME, x.YEAR), axis=1)
>>> df.head()
   YEAR  MEDIAN_HOUSEHOLD_INCOME      ADJUSTED
0  1984                    22415  52881.278152
1  1985                    23618  53803.384387
2  1986                    24897  55682.049635
3  1987                    26061  56233.030986
4  1988                    27225  56410.752325
```

## Source

The adjustment is made using data provided by [The Bureau of Labor Statistics](https://www.bls.gov/cpi/home.htm) at the U.S. Department of Labor.

Currently the library only supports inflation adjustments using annual values from the so-called "CPI-U" survey, which is an average of all prices paid by all urban consumers. It is available from 1913 to the present. It is not seasonally adjusted. The dataset is identified by the BLS as "CUUR0000SA0." It is used as the default for most basic inflation calculations.

## Updating the CPI

Since the BLS routinely releases new CPI new values, this library must periodically download the latest data. This library *does not* do this automatically. You must update the BLS dataset stored alongside the code yourself by running the following method:

```python
>>> cpi.update()
```
