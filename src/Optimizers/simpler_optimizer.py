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

def helper_optimize(title:str, date:str, i:int, top=False, stable=False, weighted=False, assets = 0):
    portfolios_stats = {f"{date}-{CRYPTO_W[i]}": {}}
    portfolios:pd.DataFrame = pd.DataFrame()
    print(f"\n Optimiser for {CRYPTO_W[i]} crypto and {1-CRYPTO_W[i]} etfs\n")

    portfolios['ETF'], out_sample = etf_mst_optimizer(date=date, crypto_w=CRYPTO_W[i])
    portfolios_stats[f"{date}-{CRYPTO_W[i]}"]['ETF'] = out_sample['efficient risk']

    if weighted:
        portfolios[f'ETF+Top{assets}Crypto'], out_sample = helper_weighted(date=date, crypto_w=CRYPTO_W[i], assets=assets)
        portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF+Top{assets}Crypto'] = out_sample['efficient risk']
    else:
        portfolios[f'ETF+{title}Crypto'], out_sample = etf_mst_crypto_mst_optimizer(date=date, crypto_w=CRYPTO_W[i], top=top, stable=stable)
        portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF{title}Crypto'] = out_sample['efficient risk']

    for passive_mode in c.PASSIVE_MODES:
        if weighted:
            portfolios[f'ETF+Top{assets}Crypto+Apy({passive_mode})'], out_sample = helper_weighted(
                date=date, crypto_w=CRYPTO_W[i], assets=assets, passive=True, passive_mode=passive_mode)
            portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF+Top{assets}Crypto+Apy({passive_mode})'] = out_sample['efficient risk']
        else:
            portfolios[f'ETF+{title}Crypto+Apy({passive_mode})'], out_sample = etf_mst_crypto_mst_apy_optimizer(
                date=date, crypto_w=CRYPTO_W[i], passive_mode=passive_mode, top=top, stable=stable)
            portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF+{title}Crypto+Apy({passive_mode})'] = out_sample['efficient risk']


    fig = px.line(portfolios, title=f'Portfolios comparison {date} {title} ({CRYPTO_W[i]} crypto)',
        labels={'value': 'Portfolio evolution', 'variable': 'Portfolio style'})

    if not weighted:
        fig.show()
    # pio.kaleido.scope.mathjax = None
    # pio.write_image(fig, f'{date}-{crypto_w[i]}-performance.pdf', width=700, height=500)
    write_json(portfolios_stats, f"{date}-{CRYPTO_W[i]}-{title}-stats.json")

    return portfolios

def helper_weighted(assets:int, date:str, crypto_w:float, passive=False, passive_mode="mean"):
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

def opt_mst(date, i):
    return helper_optimize(title='Opt-Mst', date=date, i=i)

def opt_top(date, i):
    return helper_optimize(title='Opt-Top', top=True, date=date, i=i)

def opt_stable(date, i):
    return helper_optimize(title="Opt-Stable", stable=True, date=date, i=i)

def weighted_top(assets, date, i): # 2, 3, 5, 10, all
    return helper_optimize(title=f"Top{assets}", top=True ,weighted=True, assets=assets, date=date, i=i)

def solo_top(date, i):
    crypto_w = CRYPTO_W[i]
    etf_crypto = True
    for passive_mode in c.PASSIVE_MODES:
        returns, returns_apy = load_mst_data(
            date, None, None, etf=True, crypto=True, benchmark=True, top=True, passive=True, passive_mode=passive_mode, dict_apy=DICT_CRYPTO_APY)
        _,test = train_test_split(returns, train_size=0.3, shuffle=False)
        _,test_apy= train_test_split(returns_apy, train_size=0.3, shuffle=False)
        if etf_crypto:
            portfolios_stats = {f"{date}-{CRYPTO_W[i]}": {}}
            df = pd.DataFrame()
            df['ETF'], out_sample = etf_mst_optimizer(date=date, crypto_w=CRYPTO_W[i])
            portfolios_stats[f"{date}-{CRYPTO_W[i]}"]['ETF'] = out_sample['efficient risk']
            for crypto in test.columns.values:
                if "USD" in crypto:
                    weights = {"ACWI": 1 - crypto_w, crypto: crypto_w}
                    crypto = crypto.split('-')[0]
                    port = generate_portfolio(returns=test, weights=weights, money_investment=c.MONEY_INVESTMENT)
                    df[f'ETF+{crypto}'] = port
                    port_stats = generate_portfolio_stats(port)
                    portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF+{crypto}'] = port_stats['efficient risk']
            etf_crypto = False
            fig = px.line(df, title=f'Portfolios comparison {date} Solo ({CRYPTO_W[i]} crypto)',
            labels={'value': 'Portfolio evolution', 'variable': 'Portfolio style'})
            fig.show()
        df = pd.DataFrame()
        df['ETF'], out_sample = etf_mst_optimizer(date=date, crypto_w=CRYPTO_W[i])
        for crypto in test_apy.columns.values:
            if "USD" in crypto:
                weights = {"ACWI": 1 - crypto_w, crypto: crypto_w}
                crypto = crypto.split('-')[0]
                port = generate_portfolio(returns=test_apy, weights=weights, money_investment=c.MONEY_INVESTMENT)
                df[f'ETF+{crypto}+Apy({passive_mode})'] = port
                port_stats = generate_portfolio_stats(port)
                portfolios_stats[f"{date}-{CRYPTO_W[i]}"][f'ETF+{crypto}+Apy({passive_mode})'] = port_stats['efficient risk']
        write_json(portfolios_stats, f"{date}-{CRYPTO_W[i]}-solo-stats.json")


def graph_weighted(df_array, passive_mode):
    df_compare_weighted = pd.DataFrame()
    passive_title = f"+Apy({passive_mode})" if passive_mode else ""

    passive_to_columns = {"": 1, "min": 2, "mean":3, "max":4}

    df_compare_weighted['ETF'] = df_array[0]['ETF']

    print(df_array[0])

    titles = [f'ETF+Top2Crypto{passive_title}', f'ETF+Top3Crypto{passive_title}',f'ETF+Top5Crypto{passive_title}'
    ,f'ETF+Top10Crypto{passive_title}',f'ETF+TopAllCrypto{passive_title}']

    df_compare_weighted[titles[0]]= df_array[0].iloc[:,passive_to_columns[passive_mode]]
    df_compare_weighted[titles[1]]= df_array[1].iloc[:,passive_to_columns[passive_mode]]
    df_compare_weighted[titles[2]]= df_array[2].iloc[:,passive_to_columns[passive_mode]]
    df_compare_weighted[titles[3]]= df_array[3].iloc[:,passive_to_columns[passive_mode]]
    df_compare_weighted[titles[4]]= df_array[4].iloc[:,passive_to_columns[passive_mode]]

    fig = px.line(df_compare_weighted, title=f'Portfolios comparison {date} ({CRYPTO_W[i]} crypto)',
        labels={'value': 'Portfolio evolution', 'variable': 'Portfolio style'})

    fig.show()
    

import itertools
if __name__ == '__main__':
    for date, i in itertools.product(c.START_DATES, range(1)):
        # opt_mst(date, i)
        # opt_top(date, i)
        # opt_stable(date, i)

        # dfs_2 = weighted_top(2, date, i)
        # dfs_3 = weighted_top(3,date, i)
        # dfs_5 = weighted_top(5, date, i)
        # dfs_10 = weighted_top(10, date, i)
        # dfs_all = weighted_top("All", date, i)

        # graph_weighted([dfs_2, dfs_3, dfs_5, dfs_10,dfs_all], "")

        solo_top(date, i)
