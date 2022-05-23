import collections
import itertools
import json

from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import benchmark_stats, load_benchmark, print_correlation_heatmap,print_efficient_frontiers_graph, load_mst_data, optimize_variance, optimize_semivariance, write_json

import src.constants as c

DICT_BENCHMARK_STATS = collections.defaultdict(dict)
DICT_ETF = collections.defaultdict(dict)
DICT_ETF_CRYPTO_MST = collections.defaultdict(dict)
DICT_ETF_CRYPTO_TOP = collections.defaultdict(dict)

def etf_benchmark():
    for date in c.START_DATES:
        returns_benchmark = load_benchmark(date)
        stats_benchmark_dict = benchmark_stats(returns_benchmark)
        DICT_BENCHMARK_STATS[date]['benchmark'] = stats_benchmark_dict
    write_json(DICT_BENCHMARK_STATS, "benchmark_stats.json")

def etf_optimizer():
    for date in c.START_DATES:
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            mst_mode_print = mst_mode or 'No SR filter'
            title = f"{date} {mst_type} {mst_mode_print}"
            print(f'\n{title}')
            returns = load_mst_data(date, mst_type, mst_mode)
            train, test = train_test_split(returns, train_size=0.3, shuffle=False)
            # print_efficient_frontiers_graph(train, title)
            # print_correlation_heatmap(train, title)
            in_sample, out_sample = optimize_variance(returns=returns, train=train, test=test, max_return = 0.1, min_risk = c.BENCHMARK_RISK, l2_reg=True)
            # optimize_semivariance()

def etf_crypto_optimizer():
    pass

def etf_crypto_passive_optimizer():
    pass

if __name__ == '__main__':
    etf_benchmark()