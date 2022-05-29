"""
Main file
Thesis project - Investment with index funds and applied cryptocurrency
"""

import collections
import json
import yfinance as yf
import plotly.express as px
import plotly

import src.constants as c
from src.compute import generate_asset_data, generate_passive_data
from src.utils import print_stats

MONEY_INVESTED = 100

DICT_CRYPTO_APY = collections.defaultdict(dict)

DICT_STATS = {}

with open('data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

crypto_data = {}
crypto = 'BTC-USD'
crypto_df = yf.download(crypto, interval='1wk')
crypto_df.drop(['Open', 'High', 'Low', 'Volume', 'Adj Close'], axis=1, inplace=True)
crypto_dict = generate_asset_data(crypto_df['Close'], crypto=True)
crypto_dict['annual_passive_rates'] = DICT_CRYPTO_APY['BTC']
crypto_data.setdefault(crypto, crypto_dict)
crypto_dict['passive'] = generate_passive_data(crypto_dict)
print_stats(crypto, crypto_dict, crypto=True)

    # Graph with cumulative returns

crypto_df['NORMAL'] = crypto_dict['cum_returns']
for mode in ['min', 'mean', 'max']:
    crypto_df[mode.upper()] = crypto_dict['passive'][mode]['cum_returns']
crypto_df.drop(['Close'], axis=1, inplace=True)
crypto_df = (crypto_df + 1) * MONEY_INVESTED
fig = px.line(crypto_df, title=f'{crypto} comparison of investing vs investing with interest generator',
                labels={'value': 'daily cumulative returns (%)', 'variable': 'Mode'})
print(crypto_df)
fig.show()

# world_etfs_data = {}

# world_etfs_pd = yf.download(c.WORLD_ETF_TICKERS, start='2018-01-01',end='2022-01-01', interval="1wk")
# print(world_etfs_pd)

# for world_etf in c.WORLD_ETF_TICKERS:
#     world_etf_price = world_etfs_pd['Adj Close'][world_etf]
#     world_etf_dict = generate_asset_data(world_etf_price, crypto=False)
#     world_etfs_data.setdefault(world_etf, world_etf_dict)
#     print_stats(world_etf, world_etf_dict, crypto=False)


# normalized_adjusted_closing_prices = (world_etfs_pd['Adj Close']-world_etfs_pd['Adj Close'].min(0)) / \
#     (world_etfs_pd['Adj Close'].max(0) - world_etfs_pd['Adj Close'].min(0))

# fig = px.line(normalized_adjusted_closing_prices, title='World ETFs Comparison (Adj Close) normalized')
# fig.show()
