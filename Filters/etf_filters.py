"""
Filter ETFs
"""

import pickle
import yfinance as yf

ETF_TICKER_FILENAME = '../data/etf_tickers.txt'
VOLUME_PREV_YEAR_MINIMUM = 50000

etf_tickers = []

with open(ETF_TICKER_FILENAME, "r", encoding="UTF-8") as etf_ticker_file:
    etf_tickers = etf_ticker_file.read().split('\n')

# etf_tickers_data = yf.download(etf_tickers, start='2021-01-01', end='2021-12-31')
print('Finished downloading ticker data')

# with open('etfs_data.pickle', 'wb') as f:
#    pickle.dump(etf_tickers_data, f)

with open('etfs_data.pickle', 'rb') as f:
    etf_tickers_data = pickle.load(f)

new_etf_tickers = [ticker for ticker in etf_tickers if etf_tickers_data['Volume'][ticker].mean() > VOLUME_PREV_YEAR_MINIMUM]

with open('../data/etf_tickers_volume_filtered.txt', 'w', encoding='UTF-8') as txt_volume_filtered_etf:
    txt_volume_filtered_etf.write("\n".join(map(str, new_etf_tickers)))

print(len(new_etf_tickers))
