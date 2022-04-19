"""
Filter Crypto
"""

from time import sleep
import winsound
from cryptocmd import CmcScraper

CRYPTO_TICKER_FILENAME = '../data/crypto_tickers.txt'
VOLUME_PREV_YEAR_MINIMUM = 50000

crypto_tickers = []

with open(CRYPTO_TICKER_FILENAME, "r", encoding="UTF-8") as crypto_ticker_file:
    crypto_tickers = crypto_ticker_file.read().split('\n')

new_crypto_tickers = []

for index, ticker in enumerate(crypto_tickers):
    print(index)
    sleep(1)
    crypto = CmcScraper(ticker, start_date='01-01-2021', end_date='31-12-2021', order_ascending=True)
    try:
        crypto_df = crypto.get_dataframe()
    except Exception:
        continue
    crypto_df['Coin Volume'] = crypto_df['Volume'] / crypto_df['Close']
    if crypto_df['Coin Volume'].mean() > VOLUME_PREV_YEAR_MINIMUM:
        new_crypto_tickers.append(ticker)

with open('crypto_tickers_volume_filtered.txt', 'w', encoding='UTF-8') as txt_volume_filtered_crypto:
    txt_volume_filtered_crypto.write("\n".join(map(str, new_crypto_tickers)))

print(len(new_crypto_tickers))
