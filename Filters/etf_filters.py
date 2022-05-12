import time
from utils_filters import volume_filter, expense_ratio_filter_yf, date_filter,mst_filter

ETF_FILENAME = '../data/etf-tickers.txt'
ETF_PREP_VOL = '../data/etf-date-vol-prep-f.txt'
ETF_VOLUME_FILTERED_FILENAME = '../data/etf-volume-f.txt'
ETF_ER_FILTERED_TICKERS = '../data/etf-er-f.txt'
MINIMUM_DAILY_VOLUME = 50000
MAXIMUM_EXPENSE_RATIO = 0.005
VOLUME_START_DATE = '2021-05-01'
VOLUME_END_DATE = '2022-05-01'

DATE_ARRAY = ['2021-05-01', '2020-05-01', '2019-05-01', '2018-05-01', '2017-05-01']

if __name__ == '__main__':
    start_time = time.time()

    # date_filter(ETF_FILENAME, VOLUME_START_DATE, 'etf', 'date-vol-prep')

    # while True:
        # expense_ratio_filter_yf(ETF_PREP_VOL, MAXIMUM_EXPENSE_RATIO)

    # volume_filter(ETF_ER_FILTERED_TICKERS, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_DAILY_VOLUME, 'etf')


    for date in DATE_ARRAY:
        target_name=date.split('-', maxsplit=1)[0]
        # date_filter(ETF_VOLUME_FILTERED_FILENAME, start_date=date, ticker_type='etf', target_name=target_name)
        mst_filter(f'../data/etf-{target_name}-f.txt', start_date=date, end_date=VOLUME_END_DATE, target_name=target_name, ticker_type='etf')
        # volume_filter(f'../data/etf-{target_name}-f.txt', date, VOLUME_END_DATE, MINIMUM_DAILY_VOLUME, 'etf')
        print(f"Finished date filter for {date}")
        # time.sleep(60)

    print(f"Filters took {time.time() - start_time}s to run")
