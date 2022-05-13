import time
from src.Filters.utils_filters import volume_filter, expense_ratio_filter_yf, date_filter,mst_filter

SOURCE_CRYPTO = '../data/crypto_tickers.txt'
CRYPTO_FILTERED_VOLUME = '../data/crypto-volume-f.txt'
CRYPTO_FILTERED_RATES = '../data/crypto-rates-f.txt'
CRYPTO_PREP_VOL = '../data/crypto-date-vol-prep-f.txt'

MINIMUM_DAILY_VOLUME = 50000
VOLUME_START_DATE = '2021-05-01'
VOLUME_END_DATE = '2022-05-01'

DATE_ARRAY = ['2017-11-06', '2018-05-01', '2019-05-01', '2020-05-01', '2021-05-01']

if __name__ == '__main__':
    start_time = time.time()
    # rates_filter(SOURCE_CRYPTO)
    for date in DATE_ARRAY:
        target_name=date.split('-', maxsplit=1)[0]
        filename = f'../data/crypto-{target_name}-f.txt'
        date_filter(CRYPTO_FILTERED_RATES, start_date=date, ticker_type='crypto', target_name=target_name)
        volume_filter(filename, date, VOLUME_END_DATE, MINIMUM_DAILY_VOLUME, 'crypto')
        mst_filter([filename], start_date=date, end_date=VOLUME_END_DATE, target_name=target_name, ticker_type='crypto', min_sr=False)
        mst_filter([filename], start_date=date, end_date=VOLUME_END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=0)
        mst_filter([filename], start_date=date, end_date=VOLUME_END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=1)

    print(f"Filter took {time.time() - start_time}s to run")
