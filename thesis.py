"""
Main file
Thesis project - Investment with index funds and applied cryptocurrency
"""

import yfinance as yf
from cryptocmd import CmcScraper

from compute import generate_asset_data
import constants as c


crypto_data = {}

for crypto in c.CRYPTO_BASKET:
    ticker_scraper = CmcScraper(crypto)
    crypto_df = ticker_scraper.get_dataframe().sort_values(by='Date')
    crypto_dict = generate_asset_data(crypto_df['Close'], crypto=True)
    crypto_dict['annual_passive_rates'] = c.APPLIED_CRYPTO_RATES[crypto]
    crypto_data.setdefault(crypto, crypto_dict)
    print(f"{crypto}\ndaily return: {crypto_dict['daily_a_return'] * 100} %\nannual return: {crypto_dict['annual_a_return'] * 100} %")
    print(f"daily std: {crypto_dict['daily_std'] * 100} %\nannual std: {crypto_dict['annual_std'] * 100} %")

world_etfs_data = {}

world_etfs_pd = yf.download(c.WORLD_ETF_TICKERS, period="max", interval="1d")

for world_etf in c.WORLD_ETF_TICKERS:
    world_etf_price = world_etfs_pd['Adj Close'][world_etf]
    world_etf_dict = generate_asset_data(world_etf_price, crypto=False)
    world_etfs_data.setdefault(world_etf, world_etf_dict)
    print(f"{world_etf}\ndaily return: {world_etf_dict['daily_a_return'] * 100} %\nannual return: {world_etf_dict['annual_a_return'] * 100} %")
    print(f"daily std: {world_etf_dict['daily_std'] * 100} %\nannual std: {world_etf_dict['annual_std'] * 100} %")

normalized_adjusted_closing_prices = (world_etfs_pd['Adj Close']-world_etfs_pd['Adj Close'].min(0)) / \
    (world_etfs_pd['Adj Close'].max(0) - world_etfs_pd['Adj Close'].min(0))

# plt.plot(normalized_adjusted_closing_prices, label=list(world_etfs_pd['Adj Close']))
# plt.title('Closing Prices VWCE.DE, MSCI, ACWI')
# plt.xlabel('Year')
# plt.ylabel('Price USD / EUR')
# plt.legend()
# plt.grid()
# plt.show()
