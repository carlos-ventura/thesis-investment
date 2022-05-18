import json
import time
from src.Filters.utils_filters import mst_filter

import src.constants as c

if __name__ == '__main__':
    start_time = time.time()
    len_dict = {}
    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]
        filenames = [f'../data/crypto-{target_name}-f.txt', f'../data/etf-{target_name}-f.txt']
        joint_mst_len = mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=False)
        joint_mst_sr0_len = mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=True, sr_value=0)
        joint_mst_sr1_len = mst_filter(filenames, start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etf-crypto', min_sr=True, sr_value=1)

        len_dict_date = {'joint_mst': joint_mst_len, 'joint_mst_sr0':joint_mst_sr0_len, 'joint_mst_sr1': joint_mst_sr1_len}
        len_dict[target_name] = len_dict_date

    with open("../data/joint_len.json", "w") as outfile:
        json.dump(len_dict, outfile, indent=4)

    print(f"Filter took {time.time() - start_time}s to run")
