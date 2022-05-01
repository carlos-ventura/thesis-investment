import time
from utils_filters import volume_filter, expense_ratio_filter_yf, date_filter

ETF_FILENAME = '../data/etf_tickers.txt'
ETF_VOLUME_FILTERED_FILENAME = '../data/etf_tickers_volume_filtered.txt'
ETF_ER_FILTERED_TICKERS = '../data/etf_tickers_er_filtered.txt'
MINIMUM_VOLUME_2021 = 50000
MAXIMUM_EXPENSE_RATIO = 0.005
VOLUME_START_DATE = '2021-01-01'
VOLUME_END_DATE = '2022-01-01'

if __name__ == '__main__':
    start_time = time.time()
    # volume_filtered_etf_tickers = volume_filter(ETF_FILENAME, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_VOLUME_2021, 'etf')
    # print(len(volume_filtered_etf_tickers))

    # er_filtered_etf_tickers = expense_ratio_filter_yf(ETF_VOLUME_FILTERED_FILENAME, MAXIMUM_EXPENSE_RATIO, True, True)
    # print(f"Filters took {time.time() - start_time}s to run")

    date_filtered_etf_tickers = date_filter(ETF_ER_FILTERED_TICKERS, VOLUME_START_DATE, 'etf')
