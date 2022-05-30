import collections
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import generate_portfolio, load_mst_data, optimize, write_json
import src.constants as c
import plotly.express as px
import plotly.io as pio

DICT_CRYPTO_APY = collections.defaultdict(dict)

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

crypto_w=[0.05, 0.1]

MONEY_INVESTMENT = 100

DICT_STATS = {}

def etf_mst_optimizer(date:str, crypto_w:float):
    sector=False
    mst_mode=""
    returns = load_mst_data(date, mst_type=None, mst_mode=mst_mode, etf=True, benchmark=True)
    train, test = train_test_split(returns, train_size=0.3, shuffle=False)
    out_sample, _, weights = optimize(
        train=train,
        test=test,
        sector=sector,
        crypto_w=crypto_w
        )
    return generate_portfolio(test, weights, MONEY_INVESTMENT), out_sample

def etf_mst_crypto_mst_optimizer(date:str, crypto_w:float, top=False, stable=False):
    sector=True
    mst_mode = ''
    returns = load_mst_data(date, None, mst_mode, etf=True, crypto=True, benchmark=True, top=top, stable=stable)
    train, test = train_test_split(returns, train_size=0.3, shuffle=False)
    out_sample, _, weights = optimize(
        train=train,
        test=test,
        sector=sector,
        semivariance=False,
        crypto_w=crypto_w
    )

    return generate_portfolio(test, weights, MONEY_INVESTMENT), out_sample

                 
def etf_mst_crypto_mst_apy_optimizer(date:str, crypto_w:float, passive_mode="mean", top=False, stable=False):
    sector=True
    mst_mode = ''
    returns, returns_apy = load_mst_data(
        date, None, mst_mode, etf=True, crypto=True, passive=True, benchmark=True, dict_apy=DICT_CRYPTO_APY, passive_mode=passive_mode, top=top, stable=stable)
    train, _ = train_test_split(returns, train_size=0.3, shuffle=False)
    _, test_apy = train_test_split(returns_apy, train_size=0.3, shuffle=False)
    out_sample, _, weights = optimize(
        train=train,
        test=test_apy,
        sector=sector,
        semivariance=False,
        crypto_w=crypto_w
    )
    return generate_portfolio(test_apy, weights, MONEY_INVESTMENT), out_sample

def helper_optimize(title:str, top=False, stable=False):
    for date, i in itertools.product(c.START_DATES, range(2)):
        portfolios_stats = {f"{date}{crypto_w[i]}": {}}
        portfolios:pd.DataFrame = pd.DataFrame()
        print(f"\n Optimiser for {crypto_w[i]} crypto and {1-crypto_w[i]} etfs\n")

        portfolios['ETF'], out_sample = etf_mst_optimizer(date=date, crypto_w=crypto_w[i])
        portfolios_stats[f"{date}{crypto_w[i]}"]['ETF'] = out_sample['efficient risk']
        portfolios['ETF+OptCrypto'], out_sample = etf_mst_crypto_mst_optimizer(date=date, crypto_w=crypto_w[i], top=top, stable=stable)
        portfolios_stats[f"{date}{crypto_w[i]}"]['ETF+OptCrypto'] = out_sample['efficient risk']

        for passive_mode in c.PASSIVE_MODES:
            portfolios[f'ETF+OptCrypto+Apy({passive_mode})'], out_sample = etf_mst_crypto_mst_apy_optimizer(
                date=date, crypto_w=crypto_w[i], passive_mode=passive_mode, top=top, stable=stable)
            portfolios_stats[f"{date}{crypto_w[i]}"][f'ETF+OptCrypto+Apy({passive_mode})'] = out_sample['efficient risk']
        fig = px.line(portfolios, title=f'Portfolios comparison {date} ({crypto_w[i]} crypto)',
            labels={'value': 'Portfolio evolution', 'variable': 'Portfolio style'})

        # fig.show()
        # pio.kaleido.scope.mathjax = None
        # pio.write_image(fig, f'{date}-{crypto_w[i]}-performance.pdf', width=700, height=500)
        write_json(portfolios_stats, f"{date}-{crypto_w[i]}-{title}-stats.json",)

def opt_mst():
    helper_optimize(title='opt-mst')

def opt_top():
    helper_optimize(title='opt-top', top=True)

def opt_stable():
    helper_optimize(title="opt-stable", stable=True)

def weighted_top():
    pass

import itertools
if __name__ == '__main__':
    opt_mst()
    opt_top()
    opt_stable()
    # weighted_top()


