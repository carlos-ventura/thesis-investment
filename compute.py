"""
File with computation functions
"""
from scipy.stats.mstats import gmean
import pandas as pd
import numpy as np
from utils import convert_to_annual, get_passive_object

def generate_asset_data(prices, crypto):
    """
    Params:
        prices: prices of an asset (panda Series)
        crypto: boolean True if crypto False if ETF
    Function: Generate data and stats for asset
    Return: dict with data and stats
    """
    prices = prices[pd.notna(prices)]
    returns = prices.pct_change()
    weekly_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
    annual_geomean_return = convert_to_annual(weekly_geomean_return, 'w', crypto=crypto)
    weekly_std = np.std(returns.to_numpy()[1:])
    annual_std = convert_to_annual(weekly_std, 'w', crypto=crypto, std=True)
    return {
        'prices': prices,
        'returns': returns,
        'cum_returns': (1 + returns).cumprod() - 1,
        'weekly_return': weekly_geomean_return,
        'annual_return': annual_geomean_return,
        'weekly_std': weekly_std,
        'annual_std': annual_std
    }


def generate_passive_data(crypto_dict):
    """
    Params: crypto dictionary
    Function: generates returns and stats
    Return: object with data from min, max and mean rates
    """
    rates = crypto_dict['annual_passive_rates']
    returns = crypto_dict['returns']

    min_obj = get_passive_object(rates, returns, 'min')
    mean_obj = get_passive_object(rates, returns, 'mean')
    max_obj = get_passive_object(rates, returns, 'max')

    return {
        'min': min_obj,
        'mean': mean_obj,
        'max': max_obj,
    }
