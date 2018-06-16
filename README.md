# cpi

A Python library that quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI).

## Getting started

First install the library.

```bash
$ pip install cpi
```

Once you have it, adjusting for inflation is as simple as providing a dollar value followed by the year it is from. By default it is adjusted to its value in the most recent year available.

```python
>>> import cpi
>>> cpi.inflate(100, 1950)
```

If you'd like to adjust to a different year, submit it as an integer to the optional `to` keyword argument.

```python
>>> cpi.inflate(100, 1950, to=1960)
```

If you'd like to retrieve the CPI value itself for any year, use the get method.

```python
cpi.get(1950)
```

That's it!

### Using pandas


## Source

The adjustment is made using data provided by [The Bureau of Labor Statistics](https://www.bls.gov/cpi/home.htm) at the U.S. Department of Labor.

Currently the library only supports inflation adjustments using annual values from the so-called "CPI-U" survey, which is an average of all prices paid by all urban consumers. It is not seasonally adjusted.

The dataset is identified by the BLS as "CUUR0000SA0." It used as the default for most basic inflation calculations

Learn more about the different types of CPI calculations on [the BLS website](https://www.bls.gov/cpi/questions-and-answers.htm).
