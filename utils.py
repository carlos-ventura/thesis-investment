"""
File with multiple helper functions
"""
import numpy as np
from scipy.stats.mstats import gmean

PERIODS = 12  # Number of months per year (Assumption nr 1)
CRYPTO_DAYS = 365
ETF_DAYS = 252


def apy_to_apr(rate, percentage=False):
    """
    Params: annual percentage yield (APY)
    Function: Convert APY to APR
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = (1 + rate) ** (1 / PERIODS) - 1
    return periodic_rate * PERIODS


def apr_to_apy(rate, percentage=False):
    """
    Params: annual percentage rate (APR)
    Function: Convert APR to APY
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = float(rate) / PERIODS
    return (1 + periodic_rate) ** PERIODS - 1


def daily_to_annualy(rate, std=False, crypto=True, percentage=False):
    """
    Params:
        rate: daily rate
        crypto: true if crypto, false if ETF
        percentage: true if value in percentage
    Function: convert daily rate to annual rate
    Return: annualized rate
    """
    days = CRYPTO_DAYS
    if not crypto:
        days = ETF_DAYS
    rate = float(rate)
    if percentage:
        rate /= 100
    return np.sqrt(days) * rate if std else (1 + rate) ** days - 1


def annualy_to_daily(rate, std=False, crypto=True, percentage=False):
    """
    Params:
        rate: annual rate
        crypto: true if crypto, false if ETF
        percentage: true if value in percentage
    Function: convert annual rate to daily rate
    Return: daily rate
    """
    days = CRYPTO_DAYS
    if not crypto:
        days = ETF_DAYS
    rate = float(rate)
    if percentage:
        rate /= 100
    return np.sqrt(1 / days) * rate if std else (1 + rate) ** (1 / days) - 1

def get_passive_object(rates, returns, mode):
    """
    Params:
        rates: passive annual rates
        returns: returns for crypto
        mode: 'min', 'max' or 'mean'
    Function: generate crypto passive stats and returns
    Return: dict with passive stats and returns
    """
    if 'min' in mode:
        applied_returns = returns + annualy_to_daily(min(rates))
    if 'max' in mode:
        applied_returns = returns + annualy_to_daily(max(rates))
    if 'mean' in mode:
        applied_returns = returns + annualy_to_daily(np.mean(rates))

    daily_std = np.std(applied_returns.to_numpy()[1:])
    daily_return = gmean(1 + applied_returns.to_numpy()[1:]) - 1
    annual_return = daily_to_annualy(daily_return, crypto=True)

    return {
        'passive_rate': min(rates),
        'daily_return': daily_return,
        'annual_return': annual_return,
        'returns': applied_returns,
        'cum_returns': (1 + applied_returns).cumprod() - 1
    }


def print_stats(ticker, ticker_dict, crypto):
    """
    Params:
    ticker: ticker
    ticker_dict: dict for single ticker
    Function: Generate prints to compare stats
    """
    print(f"-----{ticker}-----")
    modes = ['min', 'mean', 'max'] if crypto else []
    for i in range(len(modes) + 1):
        if i == 0:
            print("NORMAL")
            print(f"daily return: {ticker_dict['daily_return'] * 100} %\nannual return: {ticker_dict['annual_return'] * 100} %")
            print(f"daily std: {ticker_dict['daily_std'] * 100} %\nannual std: {ticker_dict['annual_std'] * 100} %")
        else:
            mode = modes[i - 1]
            print(mode.upper())
            print(f"daily return: {ticker_dict['passive'][mode]['daily_return'] * 100} % \
                \nannual return: {ticker_dict['passive'][mode]['annual_return'] * 100} %")
