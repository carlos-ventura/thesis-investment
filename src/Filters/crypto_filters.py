import time
from src.Filters.utils_filters import volume_filter, expense_ratio_filter_yf, date_filter,mst_filter

SOURCE_CRYPTO = '../data/crypto_tickers.txt'
CRYPTO_FILTERED_VOLUME = '../data/crypto-volume-f.txt'
CRYPTO_FILTERED_RATES = '../data/crypto-rates-f.txt'
CRYPTO_PREP_VOL = '../data/crypto-date-vol-prep-f.txt'

MINIMUM_DAILY_VOLUME = 50000
VOLUME_START_DATE = '2021-05-01'
VOLUME_END_DATE = '2022-05-01'

DATE_ARRAY = ['2021-05-01', '2020-05-01', '2019-05-01', '2018-05-01', '2017-05-01']

if __name__ == '__main__':
    start_time = time.time()

    # rates_filter(SOURCE_CRYPTO)

    # date_filter(CRYPTO_FILTERED_RATES, VOLUME_START_DATE, 'crypto', 'date-vol-prep')
    # volume_filter(CRYPTO_PREP_VOL, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_DAILY_VOLUME, 'crypto')

    for date in DATE_ARRAY:
        target_name=date.split('-', maxsplit=1)[0]
        # time.sleep(60)
        # date_filter(CRYPTO_FILTERED_VOLUME, start_date=date, ticker_type='crypto', target_name=target_name)
        mst_filter([f'../data/crypto-{target_name}-f.txt'], start_date=date, end_date=VOLUME_END_DATE, target_name=target_name, ticker_type='crypto')
        # volume_filter(f'../data/crypto-{target_name}-f.txt', date, VOLUME_END_DATE, MINIMUM_DAILY_VOLUME, 'crypto')
        print(f"Finished date filter for {date}")


    print(f"Filter took {time.time() - start_time}s to run")
