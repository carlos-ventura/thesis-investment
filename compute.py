"""
File with computation functions
"""
from scipy.stats.mstats import gmean
import pandas as pd
import numpy as np
from scraper import get_passive_crypto_data
from utils import daily_to_annualy, get_passive_object


def get_passive_investment_data(crypto_basket):
    """
    Argument: Basket of cryptos (ticker)
    Function: Generate types of passive investment on the basket of cryptocurrencies
    Return: Dictionary with options
    """

    crypto_passive_basket = {}

    for crypto in crypto_basket:

        crypto = str(crypto.upper())
        crypto_passive_data = get_passive_crypto_data(crypto)
        crypto_passive_basket.setdefault(crypto, crypto_passive_data)

    return crypto_passive_basket


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
    daily_geomean_return = gmean(1 + returns.to_numpy()[1:]) - 1
    annual_geomean_return = daily_to_annualy(daily_geomean_return, crypto=crypto)
    daily_std = np.std(returns.to_numpy()[1:])
    annual_std = daily_to_annualy(daily_std, crypto=crypto, std=True)
    return {
        'prices': prices,
        'returns': returns,
        'cum_returns': (1 + returns).cumprod() - 1,
        'daily_return': daily_geomean_return,
        'annual_return': annual_geomean_return,
        'daily_std': daily_std,
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
