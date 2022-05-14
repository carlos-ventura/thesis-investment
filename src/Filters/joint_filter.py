import time
from src.Filters.utils_filters import mst_filter

import src.constants as c

if __name__ == '__main__':
    start_time = time.time()
    # rates_filter(SOURCE_CRYPTO)
    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]
        filenames = [f'../data/crypto-{target_name}-f.txt', f'../data/etf-{target_name}-f.txt']
        mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=False)
        mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=True, sr_value=0)
        mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=True, sr_value=1)

    print(f"Filter took {time.time() - start_time}s to run")
