import json
import time
from src.Filters.utils_filters import volume_filter, expense_ratio_filter_yf, date_filter,mst_filter
import src.constants as c

ETF_FILENAME = '../data/etf-tickers.txt'
ETF_PREP_VOL = '../data/etf-date-vol-prep-f.txt'
ETF_VOLUME_FILTERED_FILENAME = '../data/etf-volume-f.txt'
ETF_ER_FILTERED_TICKERS = '../data/etf-er-f.txt'

if __name__ == '__main__':
    start_time = time.time()

    # date_filter(ETF_FILENAME, c.START_DATES[-1], 'etf', 'date-vol-prep')
    # while True:
        # expense_ratio_filter_yf(ETF_PREP_VOL, c.MAXIMUM_EXPENSE_RATIO)
    len_dict = {}

    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]
        filename = [f'../data/etf-{target_name}-f.txt']
        etf_date_len = date_filter(ETF_ER_FILTERED_TICKERS, start_date=date, ticker_type='etf', target_name=target_name)
        etf_volume_len = volume_filter(filename[0], date, c.END_DATE, c.MINIMUM_DAILY_VOLUME, 'etf')
        etf_mst_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf', min_sr=False)
        etf_mst_sr0_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf', min_sr=True, sr_value=0)
        etf_mst_sr1_len = mst_filter(filename, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf', min_sr=True, sr_value=1)

        len_dict_date = {'date': etf_date_len, 'volume': etf_volume_len, 'mst': etf_mst_len, 'mst_sr0':etf_mst_sr0_len, 'mst_sr1': etf_mst_sr1_len}
        len_dict[target_name] = len_dict_date
    
    with open("../data/etf_len.json", "w") as outfile:
        json.dump(len_dict, outfile, indent=4)

    print(f"Filters took {time.time() - start_time}s to run")
