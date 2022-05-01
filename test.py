from ast import AsyncFor
import yfinance as yf
import pandas as pd
from scipy.stats.mstats import gmean

from utils import convert_to_annual

ticker = yf.download('SPY', interval='1d')['Adj Close']


prices = ticker[pd.notna(ticker)]
returns = prices.pct_change()
daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
annual_geomean_return = convert_to_annual(daily_geomean_return, 'd')

print(annual_geomean_return)

ticker = yf.download('VWCE.DE', interval='1wk')['Adj Close']


prices = ticker[pd.notna(ticker)]
returns = prices.pct_change()
daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
annual_geomean_return = convert_to_annual(daily_geomean_return, 'w')

print(annual_geomean_return)

ticker = yf.download('VWCE.DE', interval='1mo')['Adj Close']


prices = ticker[pd.notna(ticker)]
returns = prices.pct_change()
daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
annual_geomean_return = convert_to_annual(daily_geomean_return, 'm')

print(annual_geomean_return)
