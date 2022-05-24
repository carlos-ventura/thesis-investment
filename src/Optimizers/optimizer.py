import collections
import itertools
import json

from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import benchmark_stats, load_benchmark, print_correlation_heatmap,print_efficient_frontiers_graph, load_mst_data, optimize_variance, optimize_semivariance, write_json

import src.constants as c

DICT_BENCHMARK_STATS = collections.defaultdict(dict)
DICT_ETF_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST_PASSIVE = collections.defaultdict(dict)


DICT_CRYPTO_APY = collections.defaultdict(dict)

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

def etf_benchmark():
    for date in c.START_DATES:
        returns_benchmark = load_benchmark(date)
        stats_benchmark_dict = benchmark_stats(returns_benchmark)
        DICT_BENCHMARK_STATS[date]['benchmark'] = stats_benchmark_dict
    write_json(DICT_BENCHMARK_STATS, "benchmark_stats.json")

def etf_mst_optimizer():
    sector=False
    rebalance=True
    for date in c.START_DATES:
        print(date)
        for mst_mode in c.MST_MODES:
            mst_mode_print = mst_mode or 'No sr'
            print(mst_mode_print)
            DICT_ETF_MST[date][mst_mode_print]=[]
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            for i, bools in enumerate(bools_list):
                returns = load_mst_data(date, mst_type=None, mst_mode=mst_mode, etf=True)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(returns=train, title=f"{date} {mst_mode_print}",l2_reg=bools[0], min_weights=bools[1])
                # print_correlation_heatmap(train, title)
                in_sample, out_sample, non_zero_weights, weights = optimize_variance(
                    returns=returns,
                    train=train,
                    test=test,
                    l2_reg=bools[0],
                    min_weights=bools[1],
                    sector=sector,
                    rebalance=rebalance,
                    rebalance_weeks=52
                    )

                DICT_ETF_MST[date][mst_mode_print].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                 "l2_reg": bools[0], "min_weights": bools[1], "train": in_sample, "test": out_sample }})
                 
    if rebalance: write_json(DICT_ETF_MST, "etf_mst_stats_rebalance.json")
    else: write_json(DICT_ETF_MST, "etf_mst_stats.json")

def etf_mst_crypto_mst_optimizer():
    for date in c.START_DATES:
        print(date)
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            mst_mode_print = mst_mode or 'No SR filter'
            modes = f"{mst_type} {mst_mode_print}"
            print(f'{modes}')
            returns = load_mst_data(date, mst_type, mst_mode, etf=True)
            train, test = train_test_split(returns, train_size=0.3, shuffle=False)
            # print_efficient_frontiers_graph(train, title)
            # print_correlation_heatmap(train, title)
            in_sample, out_sample = optimize_variance(returns=returns, train=train, test=test, max_return = 0.1, min_risk = c.BENCHMARK_RISK, l2_reg=True)
            # optimize_semivariance()

def etf_mst_crypto_mst_apy_optimizer():
    pass

if __name__ == '__main__':
    etf_mst_optimizer()