import collections
import itertools
import json
from statistics import mean
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import benchmark_stats, load_benchmark, print_correlation_heatmap,print_efficient_frontiers_graph, load_mst_data, optimize, write_json

import src.constants as c

DICT_BENCHMARK_STATS = collections.defaultdict(dict)
DICT_ETF_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST_PASSIVE = collections.defaultdict(dict)

NO_F, SR0_F, SR1_F = {"sigmas": [], "mus": []},{"sigmas": [], "mus": []},{"sigmas": [], "mus": []}

DICT_CRYPTO_APY = collections.defaultdict(dict)

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

def etf_benchmark():
    for date in c.START_DATES:
        returns_benchmark = load_benchmark(date)
        stats_benchmark_dict = benchmark_stats(returns_benchmark)
        DICT_BENCHMARK_STATS[date]['benchmark'] = stats_benchmark_dict
    write_json(DICT_BENCHMARK_STATS, "benchmark_stats.json")

def print_markers():
    f1 = go.Figure(
    data = [
        go.Scatter(x=NO_F['sigmas'], y = NO_F['mus'], name='No filter', mode='markers'),
        go.Scatter(x=SR0_F['sigmas'], y = SR0_F['mus'], name='Sr0 filter', mode='markers'),
        go.Scatter(x=SR1_F['sigmas'], y = SR1_F['mus'], name='Sr1 filter', mode='markers'),
    ],
    layout = go.Layout(
    autosize=False,
    width=700,
    height=500,
    title=f"Comparison of portfolio performance {' and '.join(str(x) for x in c.START_TEST_DATES)} SR filters (MST)",
    xaxis=dict(title="Volatility"),
    yaxis=dict(title="Return")),

    )   
    f1.show()

def print_stats_mst():
    sigmas_nof = NO_F['sigmas']
    returns_nof = NO_F['mus']
    sigmas_sr0 = SR0_F['sigmas']
    returns_sr0 = SR0_F['mus']
    sigmas_sr1 = SR1_F['sigmas']
    returns_sr1 = SR1_F['mus']
    print(f"No filter stats: SIGMA: {round(mean(sigmas_nof) * 100, 2)} ::: Returns: {round(mean(returns_nof) * 100, 2)}")
    print(f"Sr0 filter stats: SIGMA: {round(mean(sigmas_sr0) * 100, 2)} ::: Returns: {round(mean(returns_sr0) * 100, 2)}")
    print(f"Sr1 filter stats: SIGMA: {round(mean(sigmas_sr1) * 100, 2)} ::: Returns: {round(mean(returns_sr1) * 100, 2)}")

def write_markers_dict(out_sample:dict, mst_mode:str):
    sigma = out_sample['efficient risk']['std'] / 100
    returns = out_sample['efficient risk']['return'] / 100
    if not mst_mode:
        NO_F['sigmas'].append(sigma)
        NO_F['mus'].append(returns)
    if mst_mode == "sr0":
        SR0_F['sigmas'].append(sigma)
        SR0_F['mus'].append(returns)
    elif mst_mode == "sr1":
        SR1_F['sigmas'].append(sigma)
        SR1_F['mus'].append(returns)

def etf_mst_optimizer(semivariance=False, benchmark=False):
    sector=False
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        print(date)
        for mst_mode in c.MST_MODES:
            mst_mode_print = mst_mode or 'No sr'
            print(mst_mode_print)
            DICT_ETF_MST[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST[test_date][mst_mode_print]=[]
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            for i, bools in enumerate(bools_list):
                returns = load_mst_data(date, mst_type=None, mst_mode=mst_mode, etf=True, benchmark=benchmark)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(returns=train, title=f"{date} {mst_mode_print}",l2_reg=bools[0], min_weights=bools[1])
                # print_correlation_heatmap(train, title)
                out_sample, non_zero_weights, weights = optimize(
                    train=train,
                    test=test,
                    l2_reg=bools[0],
                    min_weights=bools[1],
                    sector=sector,
                    semivariance=semivariance
                    )

                DICT_ETF_MST[test_date][mst_mode_print].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                 "l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})
                if not benchmark:
                    write_markers_dict(out_sample, mst_mode)

    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"etf_mst{semi_var_string}stats.json"
    if benchmark:
        filename = f"etf_bench_mst{semi_var_string}stats.json"

    write_json(DICT_ETF_MST, filename)

def etf_mst_crypto_mst_optimizer(semivariance=False, benchmark=False):
    sector=True
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            mst_mode_print = mst_mode or 'No SR filter'
            modes = f"{mst_type} {mst_mode_print}"
            print(f'{modes}')
            DICT_ETF_MST_CRYPTO_MST[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST_CRYPTO_MST[test_date][modes]=[]
            for i, bools in enumerate(bools_list):
                returns = load_mst_data(date, mst_type, mst_mode, etf=True, crypto=True, benchmark=benchmark)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(train, title=f"{date} {modes}",l2_reg=bools[0], min_weights=bools[1])
                # print_correlation_heatmap(train, title)
                out_sample, non_zero_weights, weights = optimize(
                        train=train,
                        test=test,
                        l2_reg=bools[0],
                        min_weights=bools[1],
                        sector=sector,
                        semivariance=semivariance
                        )
                DICT_ETF_MST_CRYPTO_MST[test_date][modes].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                 "l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})

                write_markers_dict(out_sample, mst_mode)

    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"etf_mst_crypo_mst{semi_var_string}stats.json"
    if benchmark:
        filename = f"etf_bench_mst_crypo_mst{semi_var_string}stats.json"

    write_json(DICT_ETF_MST_CRYPTO_MST, filename)

                 
def etf_mst_crypto_mst_apy_optimizer(semivariance=False, benchmark=False):
    sector=True
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        print(date)
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            mst_mode_print = mst_mode or 'No SR filter'
            modes = f"{mst_type} {mst_mode_print}"
            print(f'{modes}')
            DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date][modes]=[]
            for i, bools in enumerate(bools_list):
                returns = load_mst_data(date, mst_type, mst_mode, etf=True, crypto=True, passive=True, benchmark=benchmark, dict_apy=DICT_CRYPTO_APY)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(train, title=f"{date} {modes}",l2_reg=bools[0], min_weights=bools[1])
                # print_correlation_heatmap(train, title)
                out_sample, non_zero_weights, weights = optimize(
                        train=train,
                        test=test,
                        l2_reg=bools[0],
                        min_weights=bools[1],
                        sector=sector,
                        semivariance=semivariance
                        )
                DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date][modes].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                 "l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})

                write_markers_dict(out_sample, mst_mode)

    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"etf_mst_crypo_mst{semi_var_string}passive_stats.json"
    if benchmark:
        filename = f"etf_bench_mst_crypo_mst{semi_var_string}passive_stats.json"

    write_json(DICT_ETF_MST_CRYPTO_MST_PASSIVE, filename)

if __name__ == '__main__':

    l = [False, True]
    bools_list = [list(i) for i in itertools.product(l, repeat=2)]

    for bools in bools_list:
        etf_mst_optimizer(semivariance=bools[0], benchmark=bools[1])
        etf_mst_crypto_mst_optimizer(semivariance=bools[0], benchmark=bools[1])
        etf_mst_crypto_mst_apy_optimizer(semivariance=bools[0], benchmark=bools[1])

    # etf_benchmark()

    print_markers()
    print_stats_mst()