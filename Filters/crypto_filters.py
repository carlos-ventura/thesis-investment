import time
from utils_filters import rates_filter, volume_filter

SOURCE_CRYPTO = '../data/crypto_tickers.txt'
CRYPTO_FILTERED_VOLUME = '../data/crypto_tickers_volume_filtered.txt'
CRYPTO_FILTERED_RATES = '../data/crypto_tickers_rates_filtered.txt'

MINIMUM_VOLUME_2021 = 50000
VOLUME_START_DATE = '2021-01-01'
VOLUME_END_DATE = '2022-01-01'

if __name__ == '__main__':
    start_time = time.time()

    rates_filtered_crypto_tickers = rates_filter(SOURCE_CRYPTO)
    print(f'{len(rates_filtered_crypto_tickers)} crypto tickers after rates filter')
    volume_filtered_crypto_tickers = volume_filter(CRYPTO_FILTERED_RATES, VOLUME_START_DATE, VOLUME_END_DATE, MINIMUM_VOLUME_2021, 'crypto')
    print(f'{len(volume_filtered_crypto_tickers)} crypto tickers after volume filter')

    print(f"Filter took {time.time() - start_time}s to run")
