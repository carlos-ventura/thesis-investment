# Thesis project - Investment with index funds and applied cryptocurrency

# imports
import pandas as pd
import numpy as np
import datetime
import yfinance as yf

from cryptocmd import CmcScraper
import constants as c

all_data_tickers = {}

crypto_tickers = c.CRYPTO_BASKET
crypto_rates = c.APPLIED_CRYPTO_RATES

for ticker in crypto_tickers:
    ticker_scraper = CmcScraper(ticker)
    ticker_df = ticker_scraper.get_dataframe()
    ticker_df = ticker_df[ticker_df['Close'].notna()]
    ticker_rates = crypto_rates[ticker]
    data = {'returns': ticker_df, 'annual_passive_rates': ticker_rates}
    all_data_tickers.setdefault(ticker, data)

print(all_data_tickers)

# stock = yf.download('BTC-USD', period="max")
# stock = stock[stock['Adj Close'].notna()]
# print(stock)
