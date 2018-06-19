# cpi

A Python library that quickly adjusts U.S. dollars for inflation using the Consumer Price Index (CPI).

[![Build Status](https://travis-ci.org/datadesk/cpi.svg?branch=master)](https://travis-ci.org/datadesk/cpi)

## Getting started

First install the library.

```bash
$ pip install cpi
```

Once you have it, adjusting for inflation is as simple as providing a dollar value followed by the year it is from to  the `inflate` method. By default it is adjusted to its value in the most recent year available.

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

That's it!

## Source

The adjustment is made using data provided by [The Bureau of Labor Statistics](https://www.bls.gov/cpi/home.htm) at the U.S. Department of Labor.

Currently the library only supports inflation adjustments using annual values from the so-called "CPI-U" survey, which is an average of all prices paid by all urban consumers. It is not seasonally adjusted. The dataset is identified by the BLS as "CUUR0000SA0." It used as the default for most basic inflation calculations.

## Updating the CPI

Since the BLS routinely releases new CPI new values, this library must periodically download the latest data. This library *does not* do this automatically. You must update the BLS dataset stored alongside the code yourself by running the following method:

```python
>>> cpi.update()
```
