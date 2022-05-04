import time
from utils_filters import volume_filter, expense_ratio_filter_yf, date_filter

ETF_FILENAME = '../data/etf.txt'
ETF_VOLUME_FILTERED_FILENAME = '../data/etf-volume-f.txt'
ETF_ER_FILTERED_TICKERS = '../data/etf-er-f.txt'
MINIMUM_VOLUME_2021 = 50000
MAXIMUM_EXPENSE_RATIO = 0.005
VOLUME_START_DATE = '2021-01-01'
VOLUME_END_DATE = '2022-01-01'

DATE_ARRAY = ['2020-01-01', '2019-01-01', '2018-01-01', '2017-01-01', '2016-01-01']

if __name__ == '__main__':
    start_time = time.time()
    # volume_filtered_etf_tickers = volume_filter(ETF_FILENAME, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_VOLUME_2021, 'etf')
    # print(len(volume_filtered_etf_tickers))

    # er_filtered_etf_tickers = expense_ratio_filter_yf(ETF_VOLUME_FILTERED_FILENAME, MAXIMUM_EXPENSE_RATIO, True, True)

    for date in DATE_ARRAY:
        date_filter(ETF_ER_FILTERED_TICKERS, start_date=date, ticker_type='etf', target_name=date.split('-', maxsplit=1)[0])
    # date_filter(ETF_ER_FILTERED_TICKERS, VOLUME_START_DATE, 'etf')

    print(f"Filters took {time.time() - start_time}s to run")
