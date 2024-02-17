"""Usage examples."""

import datetime as dt
from pandas import date_range
from wikianalyzer import WikiAnalyzer

DATE = dt.date(2024, 2, 16)
DATE_RANGE = date_range("2024-02-01", "2024-02-16")
MAX_RESULTS = 5

wk = WikiAnalyzer("pt")

# get data for a specific day of interest
data = wk.get_data_for_date(DATE, MAX_RESULTS)
print(f"Results for {DATE}:\n")
print(data.head())

# get data for a given date range
hist_data = wk.get_historical_data(DATE_RANGE, MAX_RESULTS)
print(f"Results between {DATE_RANGE[0]} and {DATE_RANGE[-1]}:\n")
print(hist_data)
