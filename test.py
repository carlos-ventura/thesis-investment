import yfinance as yf
import pandas as pd
from scipy.stats.mstats import gmean

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

from utils import convert_to_annual

# ticker = yf.download('SPY', interval='1d')['Adj Close']


# prices = ticker[pd.notna(ticker)]
# returns = prices.pct_change()
# daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
# annual_geomean_return = convert_to_annual(daily_geomean_return, 'd')

# print(annual_geomean_return)

ticker = yf.download('VWCE.DE', interval='1wk')['Adj Close']


prices = ticker[pd.notna(ticker)].to_frame()
returns = prices.pct_change()
daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
std = returns.std()
annual_Std = convert_to_annual(std, 'w', std=True)
annual_geomean_return = convert_to_annual(daily_geomean_return, 'w')

print(annual_geomean_return)
print(annual_Std)

# Calculate expected returns and sample covariance
mu = expected_returns.mean_historical_return(prices, compounding=True, frequency=52)
S = risk_models.sample_cov(prices, frequency=52)

# Optimize for maximal Sharpe ratio
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
ef.portfolio_performance(verbose=True)

# ticker = yf.download('VWCE.DE', interval='1mo')['Adj Close']


# prices = ticker[pd.notna(ticker)]
# returns = prices.pct_change()
# daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
# annual_geomean_return = convert_to_annual(daily_geomean_return, 'm')

# print(annual_geomean_return)
