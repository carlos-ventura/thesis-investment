import collections
import json
from statistics import mean

import pandas as pd

DICT_CRYPTO_APY = collections.defaultdict(dict)
RATES_STATS_DICT:dict = {}

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

crypto_top10 = []
with open('../data/crypto-top30-mcap.txt',"r",encoding="UTF-8") as crypto_top_file:
    crypto_top10 = crypto_top_file.read().split("\n")[:10]

for crypto in crypto_top10:
    crypto = crypto.split("-USD")[0]
    rates = DICT_CRYPTO_APY[crypto]
    RATES_STATS_DICT[crypto] = {"nr_rates": len(rates), "range":[round(min(rates) * 100, 2), round(max(rates) * 100, 2)], "mean": round(mean(rates) * 100, 2)}

df = pd.DataFrame.from_dict(RATES_STATS_DICT)

print(df)
