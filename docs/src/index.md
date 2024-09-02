---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: '0.8'
    jupytext_version: '1.4.1'
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

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

Before you can use it, you need to add the library to your Python script with an `import` statement.

```{code-cell}
import cpi
```

Adjusting prices for inflation is as simple as providing a dollar value along with its year of origin to the `inflate` method.

```{code-cell}
cpi.inflate(100, 1950)
```

By default, the value is adjusted to the most recent year. Unless otherwise specified, the "CPI-U" index for all urban consumers is used to make the conversion, the method recommended by the U.S. Bureau of Labor Statistics.

If you'd like to adjust to a different year, you can submit it as an integer to the optional `to` keyword argument.

```{code-cell}
cpi.inflate(100, 1950, to=1960)
```

You can also adjust month to month. You should submit the months as `datetime.date` objects.

```{code-cell}
from datetime import date

cpi.inflate(100, date(1950, 1, 1), to=date(2018, 1, 1))
```

You can adjust values using any other series published by the BLS as part of its "All Urban Consumers (CU)" survey. They offer more precise measures for different regions and items.

Submit one of the 60 agency-tracked areas to inflate dollars in that region.

```{code-cell}
cpi.inflate(100, 1950, area="Los Angeles-Long Beach-Anaheim, CA")
```

You can find a complete list in [the repository](https://github.com/palewire/cpi/blob/main/data/areas.csv) or by running the following command:

```{code-cell}
cpi.areas.all()[:5]
```

You can do the same to inflate the price of 400 specific items lumped into the basket of goods that make up the overall index.

```{code-cell}
cpi.inflate(100, 1980, items="Housing")
```

You can find a complete list in [the repository](https://github.com/palewire/cpi/blob/main/data/items.csv) or by running the following command:

```{code-cell}
cpi.items.all()[:5]
```

And you can do both together.

```{code-cell}
cpi.inflate(100, 1980, items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
```

Each of the 7,800 variations on the CU survey has a unique identifier. If you know which one you want, you can submit it directly.

```{code-cell}
cpi.inflate(100, 2000, series_id="CUUSS12ASETB01")
```

If you'd like to retrieve the CPI value itself for any year, use the `get` method.

```{code-cell}
cpi.get(1950)
```

You can also do that by month.

```{code-cell}
cpi.get(date(1950, 1, 1))
```

The same keyword arguments are available.

```{code-cell}
cpi.get(1980, items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
```

If you'd like to retrieve a particular CPI series for inspection, use the `series` attribute's `get` method. No configuration returns the default series.

```{code-cell}
cpi.series.get()
```

Alter the configuration options to retrieve variations based on item, area and other metadata.

```{code-cell}
cpi.series.get(items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
```

If you know a series' identifier code, you can submit it directly to `get_by_id`.

```{code-cell}
cpi.series.get_by_id("CUURS49ASAH")
```

Once retrieved, a series's complete set of index values is accessible via the `indexes` property.

```{code-cell}
series = cpi.series.get(items="Housing", area="Los Angeles-Long Beach-Anaheim, CA")
series.indexes[:5]
```

That's it!

## Working with pandas

Using the ' apply ' method, an inflation-adjusted column can quickly be added to a pandas DataFrame. Here is an example using data tracking the median household income in the United States from [The Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/MEHOINUSA646N).

```{code-cell}
import cpi
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/palewire/cpi/main/tests/test.csv")
df["ADJUSTED"] = df.apply(
    lambda x: cpi.inflate(x.MEDIAN_HOUSEHOLD_INCOME, x.YEAR), axis=1
)
```

## Working from the command line

The Python package also installs a command-line interface for `inflate` available on the terminal.

It works the same as the Python library. First, give it a value, then a source year. By default, it is adjusted to its value in the most recent available year.

```bash
inflate 100 1950
```

If you'd like to adjust to a different year, submit it as an integer to the `--to` option.

```bash
inflate 100 1950 --to=1960
```

You can also adjust month to month. You should submit the months as parseable date strings.

```bash
inflate 100 1950-01-01 --to=2018-01-01
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

## About our source

The adjustment is made using data provided by [The Bureau of Labor Statistics](https://www.bls.gov/cpi/home.htm) at the U.S. Department of Labor.

Currently, the library only supports inflation adjustments using a series from the "All Urban Consumers (CU)" survey. The so-called "CPI-U" survey is the default, an average of all prices paid by all urban consumers. It has been available since 1913. It is not seasonally adjusted. The BLS identifies the dataset as "CUUR0000SA0." It is used as the default for most basic inflation calculations. All other series measuring all urban consumers are available by taking advantage of the library's options. The alternative "Urban Wage Earners and Clerical Workers" survey is not yet available.

## Updating the data

Since the BLS routinely releases new CPI values, this library must periodically download the latest data. This library *does not* do this automatically. You must update the BLS dataset stored alongside the code yourself by running the following method:

```python
cpi.update()
```

## Other resources

* Code: [github.com/palewire/cpi](https://github.com/palewire/cpi/)
* Issues: [github.com/palewire/cpi/issues](https://github.com/palewire/cpi/issues)
* Packaging: [pypi.python.org/pypi/cpi](https://pypi.python.org/pypi/cpi)
* Testing: [github.com/palewire/cpi/actions](https://github.com/palewire/cpi/actions)
