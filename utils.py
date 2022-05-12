import numpy as np
from scipy.stats.mstats import gmean

PERIODS = 12  # Number of months per year (Assumption nr 1)
CRYPTO_DAYS = 365
ETF_DAYS = 252
WEEKS = 52
PERIODS_TYPES = ['d', 'w', 'm', 'y']


def apy_to_apr(rate, percentage=False):
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = (1 + rate) ** (1 / PERIODS) - 1
    return periodic_rate * PERIODS


def apr_to_apy(rate, percentage=False):
    rate = float(rate)
    if percentage:
        rate /= 100
    periodic_rate = float(rate) / PERIODS
    return (1 + periodic_rate) ** PERIODS - 1

def convert_to_annual(rate, period, std=False, crypto=False, percentage=False):
    if period not in PERIODS_TYPES:
        raise ValueError('Period type not accepted')
    rate = float(rate)
    if percentage:
        rate /= 100
    if period == 'w':
        period_number = WEEKS
    if period =='d':
        period_number = ETF_DAYS
        if crypto:
            period_number = CRYPTO_DAYS
    if period =='m':
        period_number = PERIODS
    return np.sqrt(period_number) * rate if std else (1 + rate) ** period_number - 1

def convert_annual_to_week(rate, std=False, percentage=False):
    periods = WEEKS
    rate = float(rate)
    if percentage:
        rate /= 100
    return np.sqrt(1 / periods) * rate if std else (1 + rate) ** (1 / periods) - 1

def get_passive_object(rates, returns, mode):
    if 'min' in mode:
        annual_rate = min(rates)
    if 'max' in mode:
        annual_rate = max(rates)
    if 'mean' in mode:
        annual_rate = np.mean(rates)
    applied_returns = returns + convert_annual_to_week(annual_rate)

    weekly_return = gmean(1 + applied_returns.to_numpy()[1:]) - 1
    annual_return = convert_to_annual(weekly_return, 'w')

    return {
        'passive_rate': annual_rate,
        'weekly_return': weekly_return,
        'annual_return': annual_return,
        'returns': applied_returns,
        'cum_returns': (1 + applied_returns).cumprod() - 1
    }


def print_stats(ticker, ticker_dict, crypto):
    print(f"-----{ticker}-----")
    modes = ['min', 'mean', 'max'] if crypto else []
    for i in range(len(modes) + 1):
        if i == 0:
            print("NORMAL")
            print(f"weekly return: {ticker_dict['weekly_return'] * 100} %\nannual return: {ticker_dict['annual_return'] * 100} %")
            print(f"weekly std: {ticker_dict['weekly_std'] * 100} %\nannual std: {ticker_dict['annual_std'] * 100} %")
        else:
            mode = modes[i - 1]
            print(mode.upper())
            print(f"weekly return: {ticker_dict['passive'][mode]['weekly_return'] * 100} % \
                \nannual return: {ticker_dict['passive'][mode]['annual_return'] * 100} %")

def sharpe_ratio(returns, risk_free=0):
    weekly_geomean= gmean(1 + returns.to_numpy()[1:]) - 1
    annual_geomean= convert_to_annual(weekly_geomean, 'w')
    weekly_std = np.std(returns.to_numpy()[1:])
    annual_std = convert_to_annual(weekly_std, 'w', std=True)

    return (annual_geomean - risk_free)/ annual_std
