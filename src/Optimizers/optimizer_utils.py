import json
from statistics import mean
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from pypfopt import EfficientSemivariance, expected_returns, objective_functions, risk_models, plotting, HRPOpt
from pypfopt.efficient_frontier import EfficientFrontier
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly_express as px
from pandas.testing import assert_frame_equal
from sklearn.model_selection import train_test_split
import collections
import empyrical as ep

import src.constants as c
from src.utils import annualized_return, annualized_std

def load_mst_data(date:str, mst_type:str, mst_mode:str):
    year = date.split('-', maxsplit=1)[0]
    path = '../data/mst/pickle/'
    mode_path = f'-{mst_mode}-' if mst_mode else '-'
    if mst_type == 'joint':
        return pd.read_pickle(f'{path}etf-crypto{mode_path}{year}.pkl')

    returns_crypto = pd.read_pickle(f'{path}crypto{mode_path}{year}.pkl')
    returns_etf = pd.read_pickle(f'{path}etf{mode_path}{year}.pkl')

    return pd.concat([returns_etf, returns_crypto], axis=1, join='inner')

def optimize_variance(returns, train, test, max_return:float, min_risk:float, l2_reg = False):
    for opt_mes in c.OPTIMIZER_MEASURES:
        ef = generate_ef(train, sector=True, l2_reg=l2_reg)
        weights = optimizer_measures_weights(ef, opt_mes, max_return, min_risk)
        cleaned_weights = ef.clean_weights()

        # print(cleaned_weights)
        print({x:y for x,y in cleaned_weights.items() if y!=0})

        print_performance_title(opt_mes)
        ef.portfolio_performance(verbose=True)

def optimize_semivariance(returns):
    pass

def print_performance_title(title:str):
    print('\n---------- OPTIMIZER ----------')
    print(f'---------- {title.upper()} ----------\n')

def optimizer_measures_weights(ef: EfficientFrontier, opt_mes:str, max_return = 0, min_risk = c.BENCHMARK_RISK):
    if opt_mes == 'max sharpe':
        return ef.max_sharpe()
    if opt_mes == 'min volatility':
        return ef.min_volatility()
    if opt_mes == 'efficient return':
        return ef.efficient_return(max_return)
    if opt_mes == 'efficient risk':
        return ef.efficient_risk(min_risk)

def print_efficient_frontiers_graph(returns:pd.DataFrame, title:str):
    asset_names = returns.columns.values
    crypto = []
    etf = []
    for asset in asset_names:
        if '-USD' in asset:
             crypto.append(asset)
        else:
             etf.append(asset)

    returns_crypto = returns[crypto]
    returns_etf = returns[etf]

    ef_crypto = generate_ef(returns_crypto, sector=False, l2_reg=True)
    ef_etf = generate_ef(returns_etf, sector=False, l2_reg=True)
    ef_combined = generate_ef(returns, sector=True, l2_reg=True)

    _, mus_crypto , sigmas_crypto, assets_crypto = plotting.plot_efficient_frontier(ef_crypto, ef_param='return')
    _, mus_etf , sigmas_etf, assets_etf = plotting.plot_efficient_frontier(ef_etf, ef_param='return')
    _, mus_combined , sigmas_combined, _ = plotting.plot_efficient_frontier(ef_combined, ef_param='return', show_assets=False)

    f1 = go.Figure(
    data = [
        go.Scatter(x=sigmas_crypto,y=mus_crypto, name='Efficient Frontier Crypto'),
        go.Scatter(x=sigmas_etf, y=mus_etf, name="Efficient Frontier ETF"),
        go.Scatter(x=sigmas_combined, y=mus_combined, name='Efficient Frontier Crypto + ETF'),
        go.Scatter(x=assets_crypto['sigmas'], y = assets_crypto['mus'], name='Cryptos', mode='markers'),
        go.Scatter(x=assets_etf['sigmas'], y = assets_etf['mus'], name='ETFs', mode='markers'),
    ],
    layout = go.Layout(
    title=f"Comparison of Efficient Frontiers {title}",
    xaxis=dict(title="Volatility"),
    yaxis=dict(title="Return"))
    )   
    f1.show()

def print_correlation_heatmap(returns:pd.DataFrame, title:str):
    fig = px.imshow(returns.corr(), title=f"Heatmap Correlation : {title}")
    fig.show()

def generate_ef(returns:pd.DataFrame, sector:bool = True, l2_reg = False, l2_value = 0.1, verbose=False):
    mu = expected_returns.mean_historical_return(returns, returns_data=True ,compounding=True, frequency=52)
    S = risk_models.sample_cov(returns, returns_data=True, frequency=52)

    ef = EfficientFrontier(mu, S, verbose=verbose, solver="SCS")

    if sector:
        sector_mapper = {asset: 'crypto' if '-USD' in asset else 'etf' for asset in returns.columns.values}
        sector_lower = {'etf': c.ETF_WEIGHT}  
        sector_upper = {'crypto': c.CRYPTO_WEIGHT }
        ef.add_sector_constraints(sector_mapper=sector_mapper, sector_upper=sector_upper, sector_lower=sector_lower)

    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=l2_value) # Reduce 0% weights

    return ef

def load_benchmark(date):
    year = date.split('-', maxsplit=1)[0]
    path = f'../data/mst/pickle/etfs-benchmark-{year}.pkl'
    return pd.read_pickle(path)

def benchmark_stats(returns):
    train, test = train_test_split(returns, train_size=0.3, shuffle=False)
    individual = {}
    return_train, return_test, std_train, std_test, return_all, std_all = [], [], [], [], [], []
    for bench in c.WORLD_ETF_TICKERS:
        ret_train = annualized_return(train[bench])
        ret_test = annualized_return(test[bench])
        vol_train = annualized_std(train[bench])
        vol_test = annualized_std(test[bench])
        individual[bench] = {"train": {"return": round(ret_train, 3), "std": round(vol_train, 3)},
         "test": {"return": round(ret_test, 3), "std": round(vol_test, 3)}}
        return_train.append(ret_train)
        return_test.append(ret_test)
        std_train.append(vol_train)
        std_test.append(vol_test)
    average = {'train': {'return': round(mean(return_train), 3), 'std': round(mean(std_train), 3)},'test': {'return': round(mean(return_test), 3), 'std': round(mean(std_test), 3)}}

    return {"individual": individual, "average": average}


def write_json(dict:dict, name:str):
    with open(f"../data/{name}", "w") as outfile:
        json.dump(dict, outfile, indent=4)


