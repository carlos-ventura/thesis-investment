import collections
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import generate_portfolio, generate_portfolio_stats, load_mst_data, optimize, write_json
import src.constants as c
import plotly.express as px
import plotly.io as pio

DICT_CRYPTO_APY = collections.defaultdict(dict)

with open('../data/rates.json') as json_file:
    DICT_CRYPTO_APY = json.load(json_file)

CRYPTO_W=[0.05, 0.1]

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

def helper_optimize(title:str, top=False, stable=False, weighted=False, assets = 0):
    for date, i in itertools.product(c.START_DATES, range(2)):
        portfolios_stats = {f"{date}{CRYPTO_W[i]}": {}}
        portfolios:pd.DataFrame = pd.DataFrame()
        print(f"\n Optimiser for {CRYPTO_W[i]} crypto and {1-CRYPTO_W[i]} etfs\n")

        portfolios['ETF'], out_sample = etf_mst_optimizer(date=date, crypto_w=CRYPTO_W[i])
        portfolios_stats[f"{date}{CRYPTO_W[i]}"]['ETF'] = out_sample['efficient risk']

        if weighted:
            portfolios[f'ETF+Top{assets}Crypto'], out_sample = helper_weighted(date=date, crypto_w=CRYPTO_W[i], assets=assets)
            portfolios_stats[f"{date}{CRYPTO_W[i]}"][f'ETF+Top{assets}Crypto'] = out_sample['efficient risk']
        else:
            portfolios['ETF+OptCrypto'], out_sample = etf_mst_crypto_mst_optimizer(date=date, crypto_w=CRYPTO_W[i], top=top, stable=stable)
            portfolios_stats[f"{date}{CRYPTO_W[i]}"]['ETF+OptCrypto'] = out_sample['efficient risk']

        for passive_mode in c.PASSIVE_MODES:
            if weighted:
                portfolios[f'ETF+Top{assets}Crypto+Apy({passive_mode})'], out_sample = helper_weighted(
                    date=date, crypto_w=CRYPTO_W[i], assets=assets, passive=True, passive_mode=passive_mode)
                portfolios_stats[f"{date}{CRYPTO_W[i]}"][f'ETF+Top{assets}Crypto+Apy({passive_mode})'] = out_sample['efficient risk']
            else:
                portfolios[f'ETF+OptCrypto+Apy({passive_mode})'], out_sample = etf_mst_crypto_mst_apy_optimizer(
                    date=date, crypto_w=CRYPTO_W[i], passive_mode=passive_mode, top=top, stable=stable)
                portfolios_stats[f"{date}{CRYPTO_W[i]}"][f'ETF+OptCrypto+Apy({passive_mode})'] = out_sample['efficient risk']


        fig = px.line(portfolios, title=f'Portfolios comparison {date} ({CRYPTO_W[i]} crypto)',
            labels={'value': 'Portfolio evolution', 'variable': 'Portfolio style'})

        fig.show()
        # pio.kaleido.scope.mathjax = None
        # pio.write_image(fig, f'{date}-{crypto_w[i]}-performance.pdf', width=700, height=500)
        write_json(portfolios_stats, f"{date}-{CRYPTO_W[i]}-{title}-stats.json")

def helper_weighted(assets:int, date:str, crypto_w:float, passive=False, passive_mode="mean" ):
    returns = load_mst_data(
        date, None, None, etf=True, crypto=True, benchmark=True, top=True, passive=passive, passive_mode=passive_mode, dict_apy=DICT_CRYPTO_APY)
    if passive:
        _, returns = load_mst_data(
            date, None, None, etf=True, crypto=True, benchmark=True, top=True, passive=passive, passive_mode=passive_mode, dict_apy=DICT_CRYPTO_APY)

    with open(f"../data/crypto-top30-{date.split('-')[0]}-f.txt", "r", encoding="UTF-8") as crypto_top_file:
        top_cryptos = crypto_top_file.read().split('\n')

    if isinstance(assets, int):
        top_cryptos = top_cryptos[:assets]

    equal_w = crypto_w / len(top_cryptos)

    weights = {"ACWI": 1 - crypto_w}
    for crypto in top_cryptos:
        weights[crypto] = equal_w

    _, test = train_test_split(returns, train_size=0.3, shuffle=False)
    port = generate_portfolio(test, weights, 100)
    stats = generate_portfolio_stats(port)
    stats['efficient risk']['weights'] = weights

    return port, stats

def opt_mst():
    helper_optimize(title='opt-mst')

def opt_top():
    helper_optimize(title='opt-top', top=True)

def opt_stable():
    helper_optimize(title="opt-stable", stable=True)

def weighted_top(assets): # 2, 3, 5, 10, all
    helper_optimize(title=f"top{assets}", top=True ,weighted=True, assets=assets)

import itertools
if __name__ == '__main__':
    # opt_mst()
    # opt_top()
    # opt_stable()
    weighted_top(2)
    weighted_top(3)
    weighted_top(5)
    # weighted_top(10)
    # weighted_top("all")


