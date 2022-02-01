"""
File with multiple helper functions
"""

PERIODS = 12  # Number of months per year (Assumption nr 1)


def apy_to_apr(rate, percentage=False):
    """
    Params: annual percentage yield (APY)
    Function: Convert APY to APR
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = (1 + rate)**(1/PERIODS) - 1
    return (periodic_rate * PERIODS) * 100


def apr_to_apy(rate, percentage=False):
    """
    Params: annual percentage rate (APR)
    Function: Convert APR to APY
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = float(rate) / PERIODS
    return ((1 + periodic_rate)**PERIODS - 1) * 100


def daily_to_annualy(rate, percentage=False):
    """
    Params: daily rate
    Function: convert daily rate to annual rate (365 days in 1 year - crypto)
    Return: annualized  rate
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    return (1 + rate) ** 365 - 1
