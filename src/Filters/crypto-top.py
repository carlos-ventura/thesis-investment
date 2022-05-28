import numpy as np
import yfinance
from src.Filters.utils_filters import date_filter
import src.constants as c

def filter_download_top_crypto():
    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]

        _ = date_filter(
            '../data/crypto-top30-mcap.txt',
            start_date=date, ticker_type='crypto-top30',
            target_name=target_name)

        with open(f"../data/crypto-top30-{target_name}-f.txt") as ticker_file:
            tickers = ticker_file.read().split('\n')

        tickers_data = yfinance.download(tickers, start=date, end=c.END_DATE, interval="1wk")["Adj Close"]
        tickers_data.dropna(how='all', inplace=True)
        tickers_returns = tickers_data.pct_change()[1:] # Remove first row of NaN value

        tickers_returns.drop(columns=tickers_returns.columns.to_series()[np.isinf(tickers_returns).any()], inplace=True)
        tickers_returns.fillna(0, inplace=True)

        new_tickers=tickers_returns.columns

        tickers_returns[new_tickers].to_pickle(f"../data/mst/pickle/crypto-top30-{target_name}.pkl")


if __name__ == '__main__':
    filter_download_top_crypto()