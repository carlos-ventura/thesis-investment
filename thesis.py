"""
Main file
Thesis project - Investment with index funds and applied cryptocurrency
"""

import yfinance as yf
from cryptocmd import CmcScraper
import plotly.express as px

import constants as c
from compute import generate_asset_data, generate_passive_data
from utils import print_stats


crypto_data = {}

for crypto in c.CRYPTO_BASKET:
    ticker_scraper = CmcScraper(crypto)
    crypto_df = ticker_scraper.get_dataframe().sort_values(by='Date')
    crypto_df.set_index('Date', inplace=True)
    crypto_df.drop(['Open', 'High', 'Low', 'Volume', 'Market Cap'], axis=1, inplace=True)
    crypto_dict = generate_asset_data(crypto_df['Close'], crypto=True)
    crypto_dict['annual_passive_rates'] = c.APPLIED_CRYPTO_RATES[crypto]
    crypto_data.setdefault(crypto, crypto_dict)
    crypto_dict['passive'] = generate_passive_data(crypto_dict)
    print_stats(crypto, crypto_dict, crypto=True)

    # Graph with cumulative returns

    crypto_df['NORMAL'] = crypto_dict['cum_returns']
    for mode in ['min', 'mean', 'max']:
        crypto_df[mode.upper()] = crypto_dict['passive'][mode]['cum_returns']
    crypto_df.drop(['Close'], axis=1, inplace=True)
    crypto_df = crypto_df * 100
    fig = px.line(crypto_df, title=f'{crypto} comparison of investing vs investing with interest generator',
                  labels={'value': 'daily cumulative returns (%)', 'variable': 'Mode'})
    fig.show()

world_etfs_data = {}

world_etfs_pd = yf.download(c.WORLD_ETF_TICKERS, period="max", interval="1d")

for world_etf in c.WORLD_ETF_TICKERS:
    world_etf_price = world_etfs_pd['Adj Close'][world_etf]
    world_etf_dict = generate_asset_data(world_etf_price, crypto=False)
    world_etfs_data.setdefault(world_etf, world_etf_dict)
    print_stats(world_etf, world_etf_dict, crypto=False)


normalized_adjusted_closing_prices = (world_etfs_pd['Adj Close']-world_etfs_pd['Adj Close'].min(0)) / \
    (world_etfs_pd['Adj Close'].max(0) - world_etfs_pd['Adj Close'].min(0))

fig = px.line(normalized_adjusted_closing_prices, title='World ETFs Comparison (Adj Close) normalized')
fig.show()
