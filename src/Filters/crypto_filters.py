import json
import time
from src.Filters.utils_filters import volatility_filter, volume_filter, expense_ratio_filter_yf, date_filter,mst_filter

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
        crypto_date_len = date_filter(CRYPTO_FILTERED_RATES, start_date=date, ticker_type='crypto', target_name=target_name)
        crypto_volume_len = volume_filter(filename[0], date, c.END_DATE, c.MINIMUM_DAILY_VOLUME, 'crypto')
        crypto_volatility_filter = volatility_filter(filename[0], date, c.END_DATE, c.MAXIMUM_ANNUAL_STD)
        crypto_mst_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=False)
        crypto_mst_sr0_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=0)
        crypto_mst_sr1_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='crypto', min_sr=True, sr_value=1)
    
    len_dict = {'date': crypto_date_len, 'volume': crypto_volume_len, 'volatility': crypto_volatility_filter,
    'mst': crypto_mst_len, 'mst_sr0':crypto_mst_sr0_len, 'mst_sr1': crypto_mst_sr1_len}
    
    with open("../data/crypto_len.json", "w") as outfile:
        json.dump(len_dict, outfile)

    print(f"Filter took {time.time() - start_time}s to run")
