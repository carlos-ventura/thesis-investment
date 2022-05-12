import yfinance as yf
import pandas as pd
from scipy.stats.mstats import gmean

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import objective_functions

import sys
sys.path.append('../')
import utils as u # pylint: disable=import-error $disable=wrong-import-position
sys.path.pop()

END_DATE = '2022-05-01'

DATES = ['2021-05-01', '2020-05-01', '2019-05-01', '2018-05-01', '2017-05-01']

benchmark_tickers = ['VWCE.DE', 'MSCI', 'ACWI']
benchmark_returns= []
benchmark_std = []

for bt in benchmark_tickers:
    ticker = yf.download(tickers=bt, start=DATES[0], end=END_DATE, interval='1wk')['Adj Close']
    prices = ticker[pd.notna(ticker)].to_frame()
    returns = prices.pct_change()
    daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
    std = returns.std()
    annual_std = u.convert_to_annual(std, 'w', std=True)
    annual_geomean_return = u.convert_to_annual(daily_geomean_return, 'w')

    benchmark_returns.append(annual_geomean_return)
    benchmark_std.append(annual_std)

    print(f"Annual geometrical mean {annual_geomean_return * 100}%")
    print(f"Annual std {annual_std * 100}%")

tickers_optimize = []

with open('../data/etf-2021-sr0-mst-f.txt', 'r', encoding='UTF-8') as mst_f:
    tickers_optimize = mst_f.read().split('\n')

ticker = yf.download(tickers=tickers_optimize, start=DATES[0], end=END_DATE, interval='1wk')['Adj Close']


prices = ticker.dropna(how='all')
mu = expected_returns.mean_historical_return(prices, compounding=True, frequency=52)
S = risk_models.sample_cov(prices, frequency=52)

# Optimize for maximal Sharpe ratio
ef = EfficientFrontier(mu, S)
# ef.add_objective(objective_functions.L2_reg, gamma=0.1)

weights = ef.efficient_risk(min(benchmark_std))

cleaned_weights = ef.clean_weights() # saves to file
print(cleaned_weights)

ef.portfolio_performance(verbose=True)

ef = EfficientFrontier(mu, S)

weights = ef.efficient_return(max(benchmark_returns))

cleaned_weights = ef.clean_weights() # saves to file
print(cleaned_weights)

ef.portfolio_performance(verbose=True)
