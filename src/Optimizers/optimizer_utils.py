import json
import math
from statistics import mean
from matplotlib.pyplot import axis
import numpy as np
import pandas as pd
from pypfopt import EfficientSemivariance, expected_returns, objective_functions, risk_models, plotting, HRPOpt
from pypfopt.efficient_frontier import EfficientFrontier
import plotly.graph_objects as go
import plotly_express as px
from sklearn.model_selection import train_test_split
import collections
import empyrical as ep
import plotly.io as pio

import src.constants as c
from src.utils import annualized_return, annualized_std, convert_annual_to_week

def optimize(train, test, crypto_w:float, l2_reg=False, min_weights=False, sector=False, semivariance=False):
    min_var_measure = c.OPTIMIZER_MEASURES[0]
    risk_measure = c.OPTIMIZER_MEASURES[1]
    out_sample_dict = collections.defaultdict(dict)

    # Calculate real min variance and compare with benchmark risk

    ef_train = generate_ef(train, sector=sector, l2_reg=l2_reg, l2_value=0.1, min_weights=min_weights, semivariance=semivariance, crypto_w=crypto_w)
    _ = optimizer_measures_weights(ef_train, min_var_measure, semivariance=semivariance)
    _, sigma_train, _= ef_train.portfolio_performance()

    min_risk = sigma_train + 0.0001 if sigma_train > c.BENCHMARK_RISK else c.BENCHMARK_RISK

    ef_train = generate_ef(train, sector=sector, l2_reg=l2_reg, l2_value=0.1, min_weights=min_weights, semivariance=semivariance, crypto_w=crypto_w)
    weights = optimizer_measures_weights(ef_train, risk_measure, min_risk)
    cleaned_weights = ef_train.clean_weights()
    non_zero_weights = {x:y for x,y in cleaned_weights.items() if y!=0}
    print(non_zero_weights)
    print("Total weights: ", len(cleaned_weights), " :::  Weights not used: ", len(cleaned_weights) - len(non_zero_weights))

    port_returns = pd.Series(weights) * test
    port_returns = port_returns.sum(axis=1).to_frame()

    ef_test = generate_ef(test, sector=sector, l2_reg=l2_reg, l2_value=0.1, min_weights=min_weights, semivariance=semivariance, crypto_w=crypto_w)
    ef_test.set_weights(weights)
    mu_test, _ , _ = ef_test.portfolio_performance(verbose=True)

    out_sample_dict[risk_measure] = {'return': round(mu_test * 100, 2), 'std': round(float(ep.annual_volatility(port_returns, period="weekly")) * 100, 2)}

    return out_sample_dict, non_zero_weights, weights

def generate_ef(returns:pd.DataFrame, crypto_w:float, sector:bool = False, l2_reg = False, min_weights = False, l2_value=0.1, verbose=False, semivariance=False):
    mu = expected_returns.mean_historical_return(returns, returns_data=True, compounding=True, frequency=52)
    
    if semivariance:
        S = risk_models.semicovariance(returns, returns_data=True, frequency=52)
        ef = EfficientSemivariance(mu, returns, verbose=verbose, solver="SCS", frequency=52, solver_options={"max_iters": 99999999})
    else:
        S = risk_models.sample_cov(returns, returns_data=True, frequency=52)
        ef = EfficientFrontier(mu, S, verbose=verbose, solver="SCS", solver_options={"max_iters": 99999999})

    sector_mapper = {asset: 'crypto' if '-USD' in asset else 'etf' for asset in returns.columns.values}
    if sector:
        sector_lower = {'etf': 1 - crypto_w, "crypto": crypto_w}  
        sector_upper = {'crypto': crypto_w }
        ef.add_sector_constraints(sector_mapper=sector_mapper, sector_upper=sector_upper, sector_lower=sector_lower)

    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=l2_value) # Reduce 0% weights

    if min_weights:
        ef.add_constraint(lambda x : x >= 0.001)

    return ef

def get_crypto_returns_passive(returns:pd.DataFrame, passive_mode, apy_dict:dict):
    tickers = returns.columns.values
    cryptos = [t for t in tickers if '-USD' in t]
    apy = 0
    for crypto in cryptos:
        crypto_search = crypto.split("-")[0]
        apy_list = apy_dict[crypto_search]
        if passive_mode == "mean":
            apy = mean(apy_list)
        if passive_mode == "min":
            apy = min(apy_list)
        if passive_mode == "max":
            apy = max(apy_list)

        weekly_apy = convert_annual_to_week(apy)

        returns[crypto] += weekly_apy
    return returns


def load_mst_data(date:str, mst_type:str, mst_mode:str, etf=True, crypto=False, passive=False, passive_mode = "min", benchmark = False, dict_apy = None):
    year = date.split('-', maxsplit=1)[0]
    path = '../data/mst/pickle/'
    mode_path = f'-{mst_mode}-' if mst_mode else '-'
    if mst_type == 'joint':
        returns_combined = pd.read_pickle(f'{path}etf-crypto{mode_path}{year}.pkl')
        if passive:
           return get_crypto_returns_passive(returns_combined, passive_mode, dict_apy)
        else:    
            return returns_combined

    if benchmark:
        returns_etf = pd.read_pickle(f"{path}etfs-benchmark-{year}.pkl")["ACWI"].to_frame()
    else:
        returns_etf = pd.read_pickle(f'{path}etf{mode_path}{year}.pkl')

    if etf and not crypto:
        return returns_etf
    if crypto:
        returns_crypto = pd.read_pickle(f'{path}crypto{mode_path}{year}.pkl')
        if passive:
            return pd.concat([returns_etf , get_crypto_returns_passive(returns_crypto, passive_mode, dict_apy)], axis=1, join="inner") 
        return pd.concat([returns_etf, returns_crypto], axis=1, join='inner')

def load_benchmark(date):
    year = date.split('-', maxsplit=1)[0]
    path = f'../data/mst/pickle/etfs-benchmark-{year}.pkl'
    return pd.read_pickle(path)

def benchmark_stats(returns):
    _, test = train_test_split(returns, train_size=0.3, shuffle=False)
    individual = {}
    return_test, std_test = [], []
    for bench in c.WORLD_ETF_TICKERS:
        ret_test = annualized_return(test[bench])
        vol_test = annualized_std(test[bench])
        individual[bench] = {"test": {"return": round(ret_test * 100, 2), "std": round(vol_test * 100, 2)}}
        return_test.append(ret_test)
        std_test.append(vol_test)
    average = {'test': {'return': round(mean(return_test * 100), 2), 'std': round(mean(std_test * 100), 2)}}

    return {"individual": individual, "average": average}


def write_json(dict:dict, name:str):
    with open(f"../data/{name}", "w") as outfile:
        json.dump(dict, outfile, indent=4)

def chunks(n:int, size:int):
    division = math.floor(n / size)
    rest = n % size
    out = [size for _ in range(division - 1)]
    if rest != 0:
        out.append(rest)
    return out

def optimizer_measures_weights(ef: EfficientFrontier, opt_mes:str, min_risk = c.BENCHMARK_RISK, max_return = 0, semivariance=False):
    if opt_mes == 'max sharpe':
        return ef.max_sharpe()
    if opt_mes == 'min volatility':
        return ef.min_semivariance() if semivariance else ef.min_volatility()
    if opt_mes == 'efficient return':
        return ef.efficient_return(max_return)
    if opt_mes == 'efficient risk':
        return ef.efficient_risk(min_risk)

def print_correlation_heatmap(returns:pd.DataFrame, title:str):
    fig = px.imshow(returns.corr(), title=title)
    print(title, returns.corr().values[np.triu_indices_from(returns.corr().values,1)].mean())
    fig.show()

def print_efficient_frontiers_graph(returns:pd.DataFrame, title:str, l2_reg:bool, min_weights:bool, crypto_w:float):
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

    ef_crypto = generate_ef(returns_crypto, sector=False, l2_reg=l2_reg, min_weights=min_weights, crypto_w=crypto_w)
    ef_etf = generate_ef(returns_etf, sector=False, l2_reg=l2_reg, min_weights=min_weights, crypto_w=crypto_w)
    ef_combined = generate_ef(returns, sector=True, l2_reg=l2_reg, min_weights=min_weights, crypto_w=crypto_w)

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
    xaxis=dict(title="Volatility", range=[-0.05, 0.2]),
    yaxis=dict(title="Return", range=[-0.07, 0.4]))
    )   
    f1.show()

    # pio.kaleido.scope.mathjax = None
    # pio.write_image(f1, 'efficient_frontiers_unzommed.pdf')