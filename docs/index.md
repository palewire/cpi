# cpi

A Python library that quickly adjusts U.S. dollars for inflation using the [Consumer Price Index](https://www.bls.gov/cpi/).

```{contents} Table of contents
:local:
:depth: 2
```

## Installation

The library can be installed from the [Python Package Index](https://pypi.org/project/cpi/) with any of the standard Python installation tools, such as [pipenv](https://pipenv.pypa.io/en/latest/).

```bash
pipenv install cpi
```

## Working with Python

Adjusting prices for inflation is as simple as providing a dollar value along with its year of origin to the `inflate` method.

```python
import cpi

cpi.inflate(100, 1950)
1017.0954356846472
```

 By default the value is adjusted to the most recent year. Unless otherwise specified, "CPI-U" index for all urban consumers is used to make the conversion, the method recommended by the U.S. Bureau of Labor Statistics.

If you'd like to adjust to a different year, you can submit it as an integer to the optional `to` keyword argument.

```python
cpi.inflate(100, 1950, to=1960)
122.82157676348547
```

You can also adjust month to month. You should submit the months as `datetime.date` objects.

```python
from datetime import date

cpi.inflate(100, date(1950, 1, 1), to=date(2018, 1, 1))
1072.2936170212768
```

You can adjust values using any of the other series published by the BLS as part of its "All Urban Consumers (CU)" survey. They offer more precise measures for different regions and items.

Submit one of the 60 areas tracked by the agency to inflate dollars in that region. You can find a complete list in [the repository](https://github.com/palewire/cpi/blob/main/data/areas.csv).

```python
cpi.inflate(100, 1950, area="Los Angeles-Long Beach-Anaheim, CA")
1081.054852320675
```

You can do the same to inflate the price of 400 specific items lumped into the basket of goods that make up the overall index.  You can find a complete list in [the repository](https://github.com/palewire/cpi/blob/main/data/items.csv).

```python
cpi.inflate(100, 1980, items="Housing")
309.77681874229353
```

And you can do both together.

```python
cpi.inflate(100, 1980, items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
344.5364396654719
```

Each of the 7,800 variations on the CU survey has a unique identifier. If you know which one you want, you can submit it directly.

```python
cpi.inflate(100, 2000, series_id="CUUSS12ASETB01")
165.15176374077112
```

If you'd like to retrieve the CPI value itself for any year, use the `get` method.

```python
cpi.get(1950)
24.1
```

You can also do that by month.

```python
cpi.get(date(1950, 1, 1))
23.5
```

The same keyword arguments are available.

```python
cpi.get(1980, items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
83.7
```

If you'd like to retrieve a particular CPI series for inspection, use the `series` attribute's `get` method. No configuration returns the default series.

```python
cpi.series.get()
```

Alter the configuration options to retrieve variations based on item, area and other metadata.

```python
cpi.series.get(items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
```

If you know a series's identifier code, you can submit that directly to `get_by_id`.

```python
cpi.series.get_by_id("CUURS49ASAH")
```

Once retrieved, the complete set of index values for a series is accessible via the `indexes` property.

```python
series = cpi.series.get(items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
series.indexes
```

That's it!

## Working with pandas

An inflation-adjusted column can quickly be added to a pandas DataFrame using the `apply` method. Here is an example using data tracking the median household income in the United States from [The Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/MEHOINUSA646N).

```python
import cpi
import pandas as pd

df = pd.read("test.csv")
df["ADJUSTED"] = df.apply(
    lambda x: cpi.inflate(x.MEDIAN_HOUSEHOLD_INCOME, x.YEAR), axis=1
)
```

## Working from the command line

The Python package also installs a command-line interface for `inflate` that is available on the terminal.

It works the same as the Python library. First give it a value. Then a source year. By default it is adjusted to its value in the most recent year available.

```bash
inflate 100 1950
1017.09543568
```

If you'd like to adjust to a different year, submit it as an integer to the `--to` option.

```bash
inflate 100 1950 --to=1960
122.821576763
```

You can also adjust month to month. You should submit the months as parseable date strings.

```bash
inflate 100 1950-01-01 --to=2018-01-01
1054.75319149
```

Here are all its options.

```bash
inflate --help
Usage: inflate [OPTIONS] VALUE YEAR_OR_MONTH

  Returns a dollar value adjusted for inflation.

Options:
  --to TEXT      The year or month to adjust the value to.
  --series_id TEXT  The CPI data series used for the conversion. The default is the CPI-U.
  --help         Show this message and exit.
```

The lists of CPI series and each's index values can be converted to a DataFrame using the `to_dataframe` method.

Here's how to get the series list:

```python
series_df = cpi.series.to_dataframe()
```

Here's how to get a series's index values:

```python
series_obj = cpi.series.get(items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
index_df = series_obj.to_dataframe()
```

## About our source

The adjustment is made using data provided by [The Bureau of Labor Statistics](https://www.bls.gov/cpi/home.htm) at the U.S. Department of Labor.

Currently the library only supports inflation adjustments using series from the "All Urban Consumers (CU)" survey. The so-called "CPI-U" survey is the default, which is an average of all prices paid by all urban consumers. It is available from 1913 to the present. It is not seasonally adjusted. The dataset is identified by the BLS as "CUUR0000SA0." It is used as the default for most basic inflation calculations. All other series measuring all urban consumers are available by taking advantage of the library's options. The alternative survey of "Urban Wage Earners and Clerical Workers" is not yet available.

## Updating the data

Since the BLS routinely releases new CPI new values, this library must periodically download the latest data. This library *does not* do this automatically. You must update the BLS dataset stored alongside the code yourself by running the following method:

```python
cpi.update()
```

## Other resources

* Code: [github.com/datadesk/cpi](https://github.com/datadesk/cpi/)
* Issues: [github.com/datadesk/cpi/issues](https://github.com/datadesk/cpi/issues)
* Packaging: [pypi.python.org/pypi/cpi](https://pypi.python.org/pypi/cpi)
* Testing: [github.com/datadesk/cpi/actions](https://github.com/datadesk/cpi/actions)
