"""
File with multiple helper functions
"""


def apy_to_apr(rate):
    pass


def apr_to_apy(rate):
    pass


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
