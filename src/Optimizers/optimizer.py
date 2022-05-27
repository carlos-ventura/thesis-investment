import collections
import itertools
import json
from statistics import mean
from turtle import write
from typing import Counter
import plotly.graph_objects as go
import plotly.io as pio

from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import benchmark_stats, load_benchmark, print_correlation_heatmap,print_efficient_frontiers_graph, load_mst_data, optimize, write_json

import src.constants as c

COUNTER_TESTS = 0

def increment():
    global COUNTER_TESTS
    COUNTER_TESTS+=1

DICT_BENCHMARK_STATS = collections.defaultdict(dict)
DICT_ETF_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST = collections.defaultdict(dict)
DICT_ETF_MST_CRYPTO_MST_PASSIVE = collections.defaultdict(dict)

crypto_w=[0.05, 0.1]

NO_F, SR0_F, SR1_F = {"sigmas": [], "mus": []},{"sigmas": [], "mus": []},{"sigmas": [], "mus": []}

CHOSEN_NO_F = {i: {"sigmas": [], "mus": []} for i in range(4)}

DICT_CRYPTO_APY = collections.defaultdict(dict)

SEMI_VARIANCE = {'sigmas': [], "returns": []}
VARIANCE = {'sigmas': [], "returns": []}

BENCH = {'sigmas': [], "returns": []}
NO_BENCH = {'sigmas': [], "returns": []}

JOINT = {'sigmas': [], "returns": []}
SEPARATE = {'sigmas': [], "returns": []}

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

def etf_benchmark():
    for date in c.START_DATES:
        returns_benchmark = load_benchmark(date)
        stats_benchmark_dict = benchmark_stats(returns_benchmark)
        DICT_BENCHMARK_STATS[date]['benchmark'] = stats_benchmark_dict
    write_json(DICT_BENCHMARK_STATS, "benchmark_stats.json")

def write_variances_dict(semivariance, out_sample):
    sigma = out_sample['efficient risk']['std'] / 100
    mu = out_sample['efficient risk']['return'] / 100
    if semivariance:
        SEMI_VARIANCE['sigmas'].append(sigma)
        SEMI_VARIANCE['returns'].append(mu)
    else:
        VARIANCE['sigmas'].append(sigma)
        VARIANCE['returns'].append(mu)

def write_benches_dict(benchmark, out_sample):
    sigma = out_sample['efficient risk']['std'] / 100
    mu = out_sample['efficient risk']['return'] / 100
    if benchmark:
        BENCH['sigmas'].append(sigma)
        BENCH['returns'].append(mu)
    else:
        NO_BENCH['sigmas'].append(sigma)
        NO_BENCH['returns'].append(mu)

def write_mst_type_dict(joint, out_sample):
    sigma = out_sample['efficient risk']['std'] / 100
    mu = out_sample['efficient risk']['return'] / 100
    if joint:
        JOINT['sigmas'].append(sigma)
        JOINT['returns'].append(mu)
    else:
        SEPARATE['sigmas'].append(sigma)
        SEPARATE['returns'].append(mu)

def print_joint_separate_stats():
    print(f"JOINT stats: SIGMA: {round(mean(JOINT['sigmas']) * 100, 2)} ::: Returns: {round(mean(JOINT['returns']) * 100, 2)}")
    print(f"SEPARATE stats: SIGMA: {round(mean(SEPARATE['sigmas']) * 100, 2)} ::: Returns: {round(mean(SEPARATE['returns']) * 100, 2)}") 

def print_var_semivar_stats():
    print(f"VAR stats: SIGMA: {round(mean(VARIANCE['sigmas']) * 100, 2)} ::: Returns: {round(mean(VARIANCE['returns']) * 100, 2)}")
    print(f"SEMIVAR stats: SIGMA: {round(mean(SEMI_VARIANCE['sigmas']) * 100, 2)} ::: Returns: {round(mean(SEMI_VARIANCE['returns']) * 100, 2)}")

def print_benc_nobench_stats():
    print(f"BENCHMARK stats: SIGMA: {round(mean(BENCH['sigmas']) * 100, 2)} ::: Returns: {round(mean(BENCH['returns']) * 100, 2)}")
    print(f"OPT ETFs stats: SIGMA: {round(mean(NO_BENCH['sigmas']) * 100, 2)} ::: Returns: {round(mean(NO_BENCH['returns']) * 100, 2)}")

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
    pio.kaleido.scope.mathjax = None
    pio.write_image(f1, 'sr_filters_plot.pdf', width=700, height=500)

def print_markers_inputs():
    f1 = go.Figure(
    data = [
        go.Scatter(x=CHOSEN_NO_F[0]['sigmas'], y = CHOSEN_NO_F[0]['mus'], name=c.MODEL_INPUTS[0], mode='markers'),
        go.Scatter(x=CHOSEN_NO_F[1]['sigmas'], y = CHOSEN_NO_F[1]['mus'], name=c.MODEL_INPUTS[1], mode='markers'),
        go.Scatter(x=CHOSEN_NO_F[2]['sigmas'], y = CHOSEN_NO_F[2]['mus'], name=c.MODEL_INPUTS[2], mode='markers'),
        go.Scatter(x=CHOSEN_NO_F[3]['sigmas'], y = CHOSEN_NO_F[3]['mus'], name=c.MODEL_INPUTS[3], mode='markers'),
    ],
    layout = go.Layout(
    autosize=False,
    width=700,
    height=500,
    title=f"Comparison of input parameters {' and '.join(str(x) for x in c.START_TEST_DATES)}",
    xaxis=dict(title="Volatility"),
    yaxis=dict(title="Return")),

    )   
    f1.show()
    pio.kaleido.scope.mathjax = None
    pio.write_image(f1, 'inputs_plot.pdf', width=700, height=500)

def print_stats_inputs():
    sigmas_empty = CHOSEN_NO_F[0]['sigmas']
    returns_empty = CHOSEN_NO_F[0]['mus']
    sigmas_min_w = CHOSEN_NO_F[1]['sigmas']
    returns_min_w = CHOSEN_NO_F[1]['mus']
    sigmas_pen = CHOSEN_NO_F[2]['sigmas']
    returns_pen = CHOSEN_NO_F[2]['mus']
    sigmas_min_w_pen = CHOSEN_NO_F[3]['sigmas']
    returns_min_w_pen = CHOSEN_NO_F[3]['mus']

    print(f"{c.MODEL_INPUTS[0]} stats: SIGMA: {round(mean(sigmas_empty) * 100, 2)} ::: Returns: {round(mean(returns_empty) * 100, 2)}")
    print(f"{c.MODEL_INPUTS[1]} stats: SIGMA: {round(mean(sigmas_min_w) * 100, 2)} ::: Returns: {round(mean(returns_min_w) * 100, 2)}")
    print(f"{c.MODEL_INPUTS[2]} stats: SIGMA: {round(mean(sigmas_pen) * 100, 2)} ::: Returns: {round(mean(returns_pen) * 100, 2)}")
    print(f"{c.MODEL_INPUTS[3]} stats: SIGMA: {round(mean(sigmas_min_w_pen) * 100, 2)} ::: Returns: {round(mean(returns_min_w_pen) * 100, 2)}")

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

def write_markers_dict(out_sample:dict, mst_mode:str, i:str):
    sigma = out_sample['efficient risk']['std'] / 100
    returns = out_sample['efficient risk']['return'] / 100
    if not mst_mode:
        NO_F['sigmas'].append(sigma)
        NO_F['mus'].append(returns)

        CHOSEN_NO_F[i]['sigmas'].append(sigma)
        CHOSEN_NO_F[i]['mus'].append(returns)
    if mst_mode == "sr0":
        SR0_F['sigmas'].append(sigma)
        SR0_F['mus'].append(returns)
    elif mst_mode == "sr1":
        SR1_F['sigmas'].append(sigma)
        SR1_F['mus'].append(returns)

def etf_mst_optimizer(crypto_w:float, semivariance=False, benchmark=False):
    sector=False
    mst_mode=""
    mst_mode_print = mst_mode or 'No sr'
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        print(date)
        print(mst_mode_print)
        for mst_mode in c.MST_MODES:
            DICT_ETF_MST[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST[test_date][mst_mode_print]=[]
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            for i, bools in enumerate(bools_list):
            # bools = [False, False]
                returns = load_mst_data(date, mst_type=None, mst_mode=mst_mode, etf=True, benchmark=benchmark)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(returns=train, title=f"{date} {mst_mode_print}",l2_reg=bools[0], min_weights=bools[1])
                # print_correlation_heatmap(train, f"{date} etf_mst {mst_mode_print}  benchmark:{benchmark}")
                out_sample, non_zero_weights, weights = optimize(
                    train=train,
                    test=test,
                    l2_reg=bools[0],
                    min_weights=bools[1],
                    sector=sector,
                    semivariance=semivariance,
                    crypto_w=crypto_w
                    )

                DICT_ETF_MST[test_date][mst_mode_print].append({0: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                    "weights": non_zero_weights,"l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})
                if not benchmark:
                    write_markers_dict(out_sample, mst_mode, i)

                write_variances_dict(semivariance, out_sample)
                write_benches_dict(benchmark, out_sample)

                increment()

    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"etf_mst{semi_var_string}stats.json"
    if benchmark:
        filename = f"etf_bench_mst{semi_var_string}stats.json"

    write_json(DICT_ETF_MST, filename)

def etf_mst_crypto_mst_optimizer(crypto_w:float, semivariance=False, benchmark=False):
    sector=True
    mst_mode = ''
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            if benchmark and mst_type=="joint":
                continue
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            mst_mode_print = mst_mode or 'No SR filter'
            modes = f"{mst_type} {mst_mode_print}"
            print(f'{modes}')
            DICT_ETF_MST_CRYPTO_MST[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST_CRYPTO_MST[test_date][modes]=[]
            for i, bools in enumerate(bools_list):
                # bools = [False, False]
                returns = load_mst_data(date, mst_type, mst_mode, etf=True, crypto=True, benchmark=benchmark)
                train, test = train_test_split(returns, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(train, title=f"{date} {modes}",l2_reg=bools[0], min_weights=bools[1], crypto_w=crypto_w)
                # print_correlation_heatmap(train, f"{date} etf_mst_crypto_mst {mst_mode_print}  benchmark:{benchmark}")
                out_sample, non_zero_weights, weights = optimize(
                        train=train,
                        test=test,
                        l2_reg=bools[0],
                        min_weights=bools[1],
                        sector=sector,
                        semivariance=semivariance,
                        crypto_w=crypto_w
                        )
                DICT_ETF_MST_CRYPTO_MST[test_date][modes].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                    "weights": non_zero_weights,"l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})

                write_markers_dict(out_sample, mst_mode, i)
                write_variances_dict(semivariance, out_sample)
                write_benches_dict(benchmark, out_sample)
                if not benchmark:
                    write_mst_type_dict(mst_type=="joint", out_sample)

                increment()

    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"{1-crypto_w}_etf_mst_crypo_mst{semi_var_string}stats.json"
    if benchmark:
        filename = f"{1-crypto_w}_etf_bench_mst_crypo_mst{semi_var_string}stats.json"

    write_json(DICT_ETF_MST_CRYPTO_MST, filename)

                 
def etf_mst_crypto_mst_apy_optimizer(crypto_w:float, semivariance=False, benchmark=False):
    sector=True
    mst_mode = ''
    for index_date, date in enumerate(c.START_DATES):
        test_date = c.START_TEST_DATES[index_date]
        print(date)
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            if benchmark and mst_type=="joint":
                continue
            l = [False, True]
            bools_list = [list(i) for i in itertools.product(l, repeat=2)]
            mst_mode_print = mst_mode or 'No SR filter'
            modes = f"{mst_type} {mst_mode_print}"
            # print(f'{modes}')
            DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date]['semi_variance'] = semivariance
            DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date][modes]=[]
            for i, bools in enumerate(bools_list):
                # bools = [False, False]
                returns, returns_apy = load_mst_data(date, mst_type, mst_mode, etf=True, crypto=True, passive=True, benchmark=benchmark, dict_apy=DICT_CRYPTO_APY)
                train, _ = train_test_split(returns, train_size=0.3, shuffle=False)
                _, test_apy = train_test_split(returns_apy, train_size=0.3, shuffle=False)
                # print_efficient_frontiers_graph(train, title=f"{date} {modes}",l2_reg=bools[0], min_weights=bools[1], crypto_w=crypto_w)
                # print_correlation_heatmap(train, f"{date} etf_mst_crypto_mst_passive {mst_mode_print} benchmark:{benchmark} ")
                out_sample, non_zero_weights, weights = optimize(
                        train=train,
                        test=test_apy,
                        l2_reg=bools[0],
                        min_weights=bools[1],
                        sector=sector,
                        semivariance=semivariance,
                        crypto_w=crypto_w
                        )
                DICT_ETF_MST_CRYPTO_MST_PASSIVE[test_date][modes].append({i: {"nr_weights": len(non_zero_weights), "nr_0_weights": len(weights) - len(non_zero_weights),
                    "weights": non_zero_weights,"l2_reg": bools[0], "min_weights": bools[1], "test": out_sample }})

                write_markers_dict(out_sample, mst_mode, i)
                write_variances_dict(semivariance, out_sample)
                write_benches_dict(benchmark, out_sample)

                if not benchmark:
                    write_mst_type_dict(mst_type=="joint", out_sample)

                increment()


    semi_var_string = "_semi_" if semivariance else "_"
    filename =  f"{1-crypto_w}_etf_mst_crypo_mst{semi_var_string}passive_stats.json"
    if benchmark:
        filename = f"{1-crypto_w}_etf_bench_mst_crypo_mst{semi_var_string}passive_stats.json"

    write_json(DICT_ETF_MST_CRYPTO_MST_PASSIVE, filename)

if __name__ == '__main__':

    for i in range(2):
        print(f"\n Optimiser for {crypto_w[i]} crypto and {1-crypto_w[i]} etfs\n")
        l = [False, True]
        bools_list = [list(i) for i in itertools.product(l, repeat=2)]

        for bools in bools_list:
            if i == 0:
                etf_mst_optimizer(semivariance=bools[1], benchmark=bools[0], crypto_w=crypto_w[i])
            etf_mst_crypto_mst_optimizer(semivariance=bools[1], benchmark=bools[0], crypto_w=crypto_w[i])
            etf_mst_crypto_mst_apy_optimizer(semivariance=bools[1], benchmark=bools[0], crypto_w=crypto_w[i])
            DICT_ETF_MST = collections.defaultdict(dict)
            DICT_ETF_MST_CRYPTO_MST = collections.defaultdict(dict)
            DICT_ETF_MST_CRYPTO_MST_PASSIVE = collections.defaultdict(dict)

    print_var_semivar_stats()
    print_benc_nobench_stats()
    print_joint_separate_stats()

    # etf_benchmark()

    print_markers_inputs()
    print_stats_inputs()

    print_markers()
    print_stats_mst()

    print(f"{COUNTER_TESTS} number of portfolios tested.")
