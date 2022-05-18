import pandas as pd
from pypfopt import expected_returns, objective_functions, risk_models, plotting
from pypfopt.efficient_frontier import EfficientFrontier
from sklearn.model_selection import train_test_split

import src.constants as c

def load_mst_data(date:str, mst_type:str, mst_mode:str):
    year = date.split('-', maxsplit=1)[0]
    path = '../data/mst/pickle/'
    mode_path = f'-{mst_mode}-' if mst_mode else '-'
    if mst_type == 'joint':
        return pd.read_pickle(f'{path}etf-crypto{mode_path}{year}.pkl')

    returns_crypto = pd.read_pickle(f'{path}crypto{mode_path}{year}.pkl')
    returns_etf = pd.read_pickle(f'{path}etf{mode_path}{year}.pkl')

    return pd.concat([returns_etf, returns_crypto], axis=1, join='inner')

def optimize_variance(returns, max_return:float, min_risk:float, l2_reg = False):

    train, test = train_test_split(returns, test_size=0.5, train_size=0.5, shuffle=False)

    for opt_mes in c.OPTIMIZER_MEASURES:

        ef = genereate_ef(returns, l2_reg=True)
        weights = optimizer_measures_weights(ef, opt_mes, max_return, min_risk)
        cleaned_weights = ef.clean_weights()

        # print(cleaned_weights)
        print({x:y for x,y in cleaned_weights.items() if y!=0})

        print_performance_title(opt_mes)
        ef.portfolio_performance(verbose=True)

        # Show weights to 0 how many show only normal weights #TODO
    # exit()

def optimize_semivariance(returns):
    pass

def print_performance_title(title:str):
    print('\n---------- OPTIMIZER ----------')
    print(f'---------- {title.upper()} ----------\n')

def optimizer_measures_weights(ef: EfficientFrontier, opt_mes:str, max_return = 0, min_risk = 0):
    if opt_mes == 'max sharpe':
        return ef.max_sharpe()
    if opt_mes == 'min volatility':
        return ef.min_volatility()
    if opt_mes == 'efficient return':
        return ef.efficient_return(max_return)
    if opt_mes == 'efficient risk':
        return ef.efficient_risk(min_risk)

def generate_efficient_frontiers_graph(returns:pd.DataFrame):
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

def genereate_ef(returns:pd.DataFrame, l2_reg = False, l2_value = 0.1):
    mu = expected_returns.mean_historical_return(returns, returns_data=True ,compounding=True, frequency=52)
    S = risk_models.sample_cov(returns, returns_data=True, frequency=52)

    ef = EfficientFrontier(mu, S)

    sector_mapper = {asset: 'crypto' if '-USD' in asset else 'etf' for asset in returns.columns.values}
    sector_lower = {'etf': c.ETF_WEIGHT}  
    sector_upper = {'crypto': c.CRYPTO_WEIGHT }

    ef.add_sector_constraints(sector_mapper=sector_mapper, sector_upper=sector_upper, sector_lower=sector_lower)

    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=l2_value) # Reduce 0% weights

    return ef



