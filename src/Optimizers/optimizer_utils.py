import json
import math
from statistics import mean
import pandas as pd
from pypfopt import EfficientSemivariance, expected_returns, objective_functions, risk_models, plotting, HRPOpt
from pypfopt.efficient_frontier import EfficientFrontier
import plotly.graph_objects as go
import plotly_express as px
from sklearn.model_selection import train_test_split
import collections
import empyrical as ep

import src.constants as c
from src.utils import annualized_return, annualized_std

def optimize(returns, train, test, l2_reg=False, min_weights=False, sector=False, rebalance=False, rebalance_weeks=52, semivariance=False):
    in_sample_dict = collections.defaultdict(dict)
    out_sample_dict = collections.defaultdict(dict)
    for opt_mes in c.OPTIMIZER_MEASURES:
        if not rebalance:
            ef_train = generate_ef(train, sector=sector, l2_reg=l2_reg, l2_value=0.1, min_weights=min_weights, semivariance=semivariance)
            weights = optimizer_measures_weights(ef_train, opt_mes)
            cleaned_weights = ef_train.clean_weights()
            non_zero_weights = {x:y for x,y in cleaned_weights.items() if y!=0}
            print(non_zero_weights)
            print("Total weights: ", len(cleaned_weights), " :::  Weights not used: ", len(cleaned_weights) - len(non_zero_weights))

            mu_train, sigma_train, _= ef_train.portfolio_performance()

            in_sample_dict[opt_mes] = {'return': round(mu_train * 100, 2), 'std': round(sigma_train * 100, 2)}

            port_returns = pd.Series(weights) * test
            port_returns = port_returns.sum(axis=1).to_frame()

            ef_test = generate_ef(test, semivariance=semivariance)
            ef_test.set_weights(weights)
            mu_test, sigma_test , _ = ef_test.portfolio_performance(verbose=True)


        if rebalance:
            mu_test = 0
            rebalanced_port = pd.DataFrame()
            for count in chunks(test.shape[0], rebalance_weeks):
                ef_train = generate_ef(train, sector=sector, l2_reg=l2_reg, l2_value=0.1, min_weights=min_weights, semivariance=semivariance)
                weights = optimizer_measures_weights(ef_train, opt_mes)
                cleaned_weights = ef_train.clean_weights()
                non_zero_weights = {x:y for x,y in cleaned_weights.items() if y!=0}
                rebalanced_port = pd.concat([rebalanced_port, pd.Series(cleaned_weights) * test.head(count)])
                rebalanced_port = rebalanced_port
                train = pd.concat([train, test.head(count)])
                test = test.drop(test.index[range(count)])
            rebalanced_port = rebalanced_port.loc[:, (rebalanced_port != 0).any(axis=0)]
            non_zero_weights = rebalanced_port.columns.values
            rebalanced_returns = rebalanced_port.sum(axis=1)
            sigma_test = float(ep.annual_volatility(rebalanced_returns, period="weekly"))
        
        # print("ep Downside Risk", round(float(ep.downside_risk(port_returns, period="weekly"))* 100, 3), "%")
        std_string = "down std" if semivariance else "std"

        out_sample_dict[opt_mes] = {'return': round(mu_test * 100, 2), std_string: round(float(ep.annual_volatility(port_returns, period="weekly"))* 100, 2)}

    return {}, out_sample_dict, non_zero_weights, weights

def generate_ef(returns:pd.DataFrame, sector:bool = False, l2_reg = False, min_weights = False, l2_value=0.1, verbose=False, semivariance=False):
    mu = expected_returns.mean_historical_return(returns, returns_data=True, compounding=True, frequency=52)
    
    if semivariance:
        S = risk_models.semicovariance(returns, returns_data=True, frequency=52)
        ef = EfficientSemivariance(mu, returns, verbose=verbose, solver="SCS", frequency=52, solver_options={"max_iters": 9999999})
    else:
        S = risk_models.sample_cov(returns, returns_data=True, frequency=52)
        ef = EfficientFrontier(mu, S, verbose=verbose, solver="SCS", solver_options={"max_iters": 999999})

    sector_mapper = {asset: 'crypto' if '-USD' in asset else 'etf' for asset in returns.columns.values}
    if sector:
        sector_lower = {'etf': c.ETF_WEIGHT}  
        sector_upper = {'crypto': c.CRYPTO_WEIGHT }
        ef.add_sector_constraints(sector_mapper=sector_mapper, sector_upper=sector_upper, sector_lower=sector_lower)

    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=l2_value) # Reduce 0% weights

    if min_weights:
        ef.add_constraint(lambda x : x >= 0.001)

    return ef

def get_crypto_returns_passive(returns:pd.DataFrame, passive_mode):
    cryptos = returns.columns.values
    for crypto in cryptos:
        apy_list = get_crypto_apys(crypto)

def load_mst_data(date:str, mst_type:str, mst_mode:str, etf=True, crypto=False, passive=False, passive_mode = "mean"):
    year = date.split('-', maxsplit=1)[0]
    path = '../data/mst/pickle/'
    mode_path = f'-{mst_mode}-' if mst_mode else '-'
    if mst_type == 'joint':
        return pd.read_pickle(f'{path}etf-crypto{mode_path}{year}.pkl')

    returns_etf = pd.read_pickle(f'{path}etf{mode_path}{year}.pkl')

    if etf:
        return returns_etf
    if crypto:
        returns_crypto = pd.read_pickle(f'{path}crypto{mode_path}{year}.pkl')
        if passive:
            return pd.concat([returns_etf ,get_crypto_returns_passive(returns_crypto, passive_mode)], axis=1, join="inner") 
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

def optimizer_measures_weights(ef: EfficientFrontier, opt_mes:str, max_return = 0, min_risk = c.BENCHMARK_RISK):
    if opt_mes == 'max sharpe':
        return ef.max_sharpe()
    if opt_mes == 'min volatility':
        return ef.min_volatility()
    if opt_mes == 'efficient return':
        return ef.efficient_return(max_return)
    if opt_mes == 'efficient risk':
        return ef.efficient_risk(min_risk)

def print_correlation_heatmap(returns:pd.DataFrame, title:str):
    fig = px.imshow(returns.corr(), title=f"Heatmap Correlation : {title}")
    fig.show()

def print_efficient_frontiers_graph(returns:pd.DataFrame, title:str, l2_reg:bool, min_weights:bool):
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

    # ef_crypto = generate_ef(returns_crypto, sector=False, l2_reg=l2_reg, min_weights=min_weights)
    ef_etf = generate_ef(returns_etf, sector=True, l2_reg=l2_reg, min_weights=min_weights)
    # ef_combined = generate_ef(returns, sector=False, l2_reg=l2_reg, min_weights=min_weights)

    # _, mus_crypto , sigmas_crypto, assets_crypto = plotting.plot_efficient_frontier(ef_crypto, ef_param='return')
    _, mus_etf , sigmas_etf, assets_etf = plotting.plot_efficient_frontier(ef_etf, ef_param='return')
    # _, mus_combined , sigmas_combined, _ = plotting.plot_efficient_frontier(ef_combined, ef_param='return', show_assets=False)

    f1 = go.Figure(
    data = [
      #  go.Scatter(x=sigmas_crypto,y=mus_crypto, name='Efficient Frontier Crypto'),
        go.Scatter(x=sigmas_etf, y=mus_etf, name="Efficient Frontier ETF"),
       # go.Scatter(x=sigmas_combined, y=mus_combined, name='Efficient Frontier Crypto + ETF'),
        #go.Scatter(x=assets_crypto['sigmas'], y = assets_crypto['mus'], name='Cryptos', mode='markers'),
        go.Scatter(x=assets_etf['sigmas'], y = assets_etf['mus'], name='ETFs', mode='markers'),
    ],
    layout = go.Layout(
    title=f"Comparison of Efficient Frontiers {title}",
    xaxis=dict(title="Volatility"),
    yaxis=dict(title="Return"))
    )   
    f1.show()