"""
File with multiple helper functions
"""
import numpy as np


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
    return (1 + rate) ** days - 1 if not std else np.sqrt(days) * rate


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
    return (1 + rate) ** (1 / days) - 1 if not std else np.sqrt(1 / days) * rate
