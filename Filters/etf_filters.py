import time
from utils_filters import volume_filter

ETF_FILENAME = '../data/etf_tickers.txt'
MINIMUM_VOLUME_2021 = 50000
VOLUME_START_DATE = '2021-01-01'
VOLUME_END_DATE = '2022-01-01'

if __name__ == '__main__':
    start_time = time.time()
    volume_filtered_etf_tickers = volume_filter(ETF_FILENAME, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_VOLUME_2021, 'etf')
    print(len(volume_filtered_etf_tickers))
    print(f"Filter took {time.time() - start_time}s to run")
