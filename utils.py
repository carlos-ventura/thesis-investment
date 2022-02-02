"""
File with multiple helper functions
"""

PERIODS = 12  # Number of months per year (Assumption nr 1)
DAYS = 365  # Number of days per year (Cryptocurrency)


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


def daily_to_annualy(rate, percentage=False):
    """
    Params: daily rate
    Function: convert daily rate to annual rate
    Return: annualized rate
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    return (1 + rate) ** DAYS - 1


def annualy_to_daily(rate, percentage=False):
    """
    Params: annual rate
    Function: convert annual rate to daily rate
    Return: daily rate
    """
    rate = float(rate)
    if percentage:
        rate /= 100
    return (1 + rate) ** (1 / DAYS) - 1
