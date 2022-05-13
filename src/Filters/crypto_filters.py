import time
from src.Filters.utils_filters import volume_filter, expense_ratio_filter_yf, date_filter,mst_filter

import src.constants as c

SOURCE_CRYPTO = '../data/crypto_tickers.txt'
CRYPTO_FILTERED_VOLUME = '../data/crypto-volume-f.txt'
CRYPTO_FILTERED_RATES = '../data/crypto-rates-f.txt'
CRYPTO_PREP_VOL = '../data/crypto-date-vol-prep-f.txt'

if __name__ == '__main__':
    start_time = time.time()
    # rates_filter(SOURCE_CRYPTO)
    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]
        filename = [f'../data/crypto-{target_name}-f.txt']
        date_filter(CRYPTO_FILTERED_RATES, start_date=date, ticker_type='crypto', target_name=target_name)
        volume_filter(filename[0], date, c.END_DATE, c.MINIMUM_DAILY_VOLUME, 'crypto')
        mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=False)
        mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=0)
        mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=1)

    print(f"Filter took {time.time() - start_time}s to run")
