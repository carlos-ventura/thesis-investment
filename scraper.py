"""
Scrape data from platforms for crypto lending, staking and savings
"""

import os
import urllib
import urllib.request
import json
import re
import shutil
import requests
import pandas as pd
import bs4


from utils import apr_to_apy, daily_to_annualy


def get_passive_crypto_data(crypto):
    """
    Argument: crypto (ticker)
    Function: Scrape rates in platforms website
    Return: All rates for the crypto (ticker)
    """

    print("Fetching passive rates data...")

    binance_passive_data = binance_data(crypto)
    crypto_com_passive_data = crypto_com_data(crypto)
    defirate_passive_data = defirate_data(crypto)
    okx_passive_data = okx_data(crypto)
    kucoin_passive_data = kucoin_data(crypto)
    kraken_passive_data = kraken_data(crypto)
    gemini_passive_data = gemini_data(crypto)
    gateio_passive_data = gateio_data(crypto)
    huobi_passive_data = huobi_data(crypto)

    crypto_passive = [*binance_passive_data, *crypto_com_passive_data, *defirate_passive_data, *okx_passive_data,
                      *kucoin_passive_data, *kraken_passive_data, *gemini_passive_data, *gateio_passive_data, *huobi_passive_data]

    # crypto_passive = [*binance_passive_data]
    crypto_passive = [float(rate) for rate in crypto_passive]
    crypto_passive.sort()
    # print(crypto_passive)
    return crypto_passive


def binance_data(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Binance
    Return: Binance rates for ticker
    """

    platform = "Binance"

    # print(f'Fetching passive data for {crypto} in {platform}')

    rates = [*binance_staking(crypto), *binance_savings(crypto)]

    return return_function(crypto, platform, rates, api=True)


def binance_savings(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Binance Savings
    Return: Binance savings rates for ticker
    """

    url_flex = f"https://www.binance.com/bapi/earn/v1/friendly/lending/daily/product/list?&asset={crypto}"
    url_fixed = f'https://www.binance.com/bapi/earn/v1/friendly/lending/project/customizedFixedProject/list?status=ALL&asset={crypto}'
    response_flex = requests.request("GET", url_flex)
    response_fixed = requests.request("GET", url_fixed)
    json_data_flex = json.loads(response_flex.text)
    json_data_fixed = json.loads(response_fixed.text)

    rates = []
    flex_rates = []
    fixed_rates_apr = []

    if json_data_flex['data']:
        if json_data_flex['data'][0]['tierAnnualInterestRateList']:
            flex_rates.extend(json_data_flex['data'][0]['tierAnnualInterestRateList'])
        else:
            rates.append(json_data_flex['data'][0]['latestAnnualInterestRate'])

    if json_data_fixed['data']:
        fixed_rates_apr.extend(json_data_fixed['data'][0]['list'])

    rates.extend(flex_rate['annualInterestRate'] for flex_rate in flex_rates)
    rates.extend(apr_to_apy(fixed_rate_apr['interestRate']) for fixed_rate_apr in fixed_rates_apr)

    return rates


def binance_staking(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Binance Staking
    Return: Binance staking rates for ticker
    """

    url = f"https://www.binance.com/bapi/earn/v1/friendly/pos/union?asset={crypto}"
    url_defi = f'https://www.binance.com/bapi/earn/v1/friendly/defi-pos/groupByAssetAndPartnerNameList?asset={crypto}'
    response = requests.request("GET", url)
    response_defi = requests.request("GET", url_defi)
    json_data = json.loads(response.text)
    json_data_defi = json.loads(response_defi.text)

    rates = []
    projects = []

    if json_data['data']:
        if json_data['data'][0]['projects']:
            projects.extend(json_data['data'][0]['projects'])
        else:
            rates.append(json_data['data'][0]['annualInterestRate'])

    if json_data_defi['data']:
        if json_data_defi['data'][0]['projects']:
            projects.extend(json_data_defi['data'][0]['projects'])
        else:
            rates.append(json_data_defi['data'][0]['annualInterestRate'])

    rates.extend(proj['config']['annualInterestRate'] for proj in projects)
    return rates


def crypto_com_data(crypto):
    """
    Params: Crypto token/coin
    Function: Scrap Crypto.com for the "earn" program
    Return: Rates available for available coins/tokens
    """

    platform = "Crypto.com"
    data_path_file = 'data/crypto_com_passive.json'

    if not os.path.isfile(data_path_file):
        # print(f'Fetching passive data for {crypto} in {platform}')
        url = 'https://help.crypto.com/en/articles/2996965-crypto-earn-how-does-it-work'
        html = requests.get(url).content
        df_list = pd.read_html(html)
        passive_rates_apr_pd = df_list[1]
        passive_rates_apr_pd.drop(passive_rates_apr_pd.columns[[2, 4, 6]], axis=1, inplace=True)
        passive_rates_apr_pd.drop([0, 1], inplace=True)
        passive_rates_apr_pd = passive_rates_apr_pd.T.reset_index(drop=True).T

        for i in range(4):
            if i == 0:
                passive_rates_apr_pd[0] = passive_rates_apr_pd[0].str.rstrip('*')
            else:
                passive_rates_apr_pd[i] = passive_rates_apr_pd[i].str.rstrip('%').astype('float') / 100
                passive_rates_apr_pd[i] = passive_rates_apr_pd[i].apply(apr_to_apy)

        crypto_com_passive_data = passive_rates_apr_pd.set_index(0).T.to_dict('list')

        with open("data/crypto_com_passive.json", mode="w", encoding="UTF-8") as crypto_com_data_json:
            json.dump(crypto_com_passive_data, crypto_com_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open("data/crypto_com_passive.json", mode="r", encoding="UTF-8") as json_crypto_passive:
            crypto_com_passive_data = json.load(json_crypto_passive)

    return return_function(crypto, platform, crypto_com_passive_data)


def defirate_data(crypto):
    """
    Params: Crypto token/coin
    Function: Scrap DeFi Rate
    Assumption: All rates are APY
    Return: Rates available for available coins/tokens
    """

    platform = "DeFi Rate"
    data_path_file = 'data/defirate_passive.json'

    if not os.path.isfile(data_path_file):
        # print(f'Fetching passive data for {crypto} in {platform}')
        url = 'https://defirate.com/lend/'
        html = requests.get(url).content
        df_list = pd.read_html(html)
        passive_rates_pd = df_list[1]
        passive_rates_pd = passive_rates_pd.T.reset_index(drop=True).T
        for i in range(11):
            passive_rates_pd[i+1] = passive_rates_pd[i + 1].str.strip('%').replace('–', '0').astype('float') / 100
        defirate_passive_data = passive_rates_pd.set_index(0).T.to_dict('list')

        for key in defirate_passive_data.keys():
            defirate_passive_data[key] = list(
                filter(lambda num: num != 0, defirate_passive_data[key]))

        with open("data/defirate_passive.json", mode="w", encoding="UTF-8") as defirate_data_json:
            json.dump(defirate_passive_data, defirate_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open("data/defirate_passive.json", mode="r", encoding="UTF-8") as json_defirate_passive:
            defirate_passive_data = json.load(json_defirate_passive)

    return return_function(crypto, platform, defirate_passive_data)


def okx_data(crypto):
    """
    Params: Crypto token/coin
    Function: Scrap OKX for rates
    Return: Rates for coin/token if available
    """

    platform = "OKX"
    data_path_file = "data/okx_passive.json"

    if not os.path.isfile(data_path_file):
        # print(f'Fetching passive data for {crypto} in {platform}')

        url = "https://www.okx.com/v2/asset/balance/project-currency"
        response = requests.request("GET", url)
        json_data = json.loads(response.text)

        okx_passive_data = {}

        for data in json_data['data']:
            token = data['currencyName']
            temp_apy = [proj['rateRangeMaxCompar'] / 100 for proj in data['projectList']]
            okx_passive_data.setdefault(token, temp_apy)
        with open(f"data/{platform.lower()}_passive.json", mode="w", encoding="UTF-8") as okx_data_json:
            json.dump(okx_passive_data, okx_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open(f"data/{platform.lower()}_passive.json", mode="r", encoding="UTF-8") as json_okx_passive:
            okx_passive_data = json.load(json_okx_passive)

    return return_function(crypto, platform, okx_passive_data)


def kucoin_data(crypto):
    """
    Params: Crypto token/coin
    Function: Scrap KuCoin for rates
    Return: Rates for coin/token if available
    """

    platform = "KuCoin"

    # print(f'Fetching passive data for {crypto} in {platform}')

    rates = [*kucoin_staking(crypto), *kucoin_savings(crypto), *kucoin_lending(crypto)]

    return return_function(crypto, platform, rates, api=True)


def kucoin_staking(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in KuCoin Staking
    Return: KuCoin staking rates for ticker
    """

    url = f"https://www.kucoin.com/_pxapi/pool-staking/v2/products/stakings?keyword={crypto}"
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)['items']
    return [apr_to_apy((float(rate['apr']) + float(rate['pol_apr'])) / 100) for rate in json_data_rates]


def kucoin_savings(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in KuCoin Savings
    Return: KuCoin savings rates for ticker
    """

    url = f"https://www.kucoin.com/_pxapi/pool-staking/v2/products/demands?keyword={crypto}"
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)['items']

    rates = []
    for rate in json_data_rates:
        rates.extend([float(rate['avg7_return']) / 100, float(rate['staking_return']) / 100])

    return rates


def kucoin_lending(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in KuCoin Lending
    Return: KuCoin lending rates for ticker
    """

    form_data = {'currency': crypto}

    url = "https://www.kucoin.com/_api/margin-loan/loan/order/query-min-int-rate?lang=en_US"
    response = requests.request("POST", url, data=form_data)
    json_data__daily_rates = json.loads(response.text)['data']
    return [apr_to_apy(daily_to_annualy(daily_rates['interestRate'])) for daily_rates in json_data__daily_rates]


def kraken_data(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Kraken Staking
    Return: Kraken staking rates for ticker
    """

    platform = 'Kraken'
    data_path_file = "data/kraken_passive.json"

    if not os.path.isfile(data_path_file):
        # print(f'Fetching passive data for {crypto} in {platform}')
        url = 'https://www.kraken.com/features/staking-coins/'
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(url).read()
        soup = bs4.BeautifulSoup(response, "lxml")
        div = soup.find("div", {"class": "fc-11323bab-1 fc-11323bab-6 fc-11323bab-2 fc-11323bab-7 fc-11323bab-3 fc-11323bab-8"})
        div_text = div.get_text().split('\n')

        tokens = []
        rates = []
        staking_list = [x for x in div_text if '(' in x or '%' in x]
        for i in range(0, len(staking_list), 2):
            tokens.append(re.search('\(([^([^0-9)]+)', staking_list[i])[1].replace(' ', ''))
            rates.append(staking_list[i + 1].rstrip('%').split('-'))

        rates = [[apr_to_apy(float(rate) / 100) for rate in rate_list] for rate_list in rates]
        kraken_passive_data = dict(zip(tokens, rates))
        with open(f"data/{platform.lower()}_passive.json", mode="w", encoding="UTF-8") as kraken_data_json:
            json.dump(kraken_passive_data, kraken_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open(f"data/{platform.lower()}_passive.json", mode="r", encoding="UTF-8") as json_kraken_passive:
            kraken_passive_data = json.load(json_kraken_passive)

    return return_function(crypto, platform, kraken_passive_data)


def gemini_data(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Gemini Earn
    Return: Gemini Earn staking rates for ticker
    """

    platform = "Gemini"
    data_path_file = "data/gemini_passive.json"

    if not os.path.isfile(data_path_file):
        # print(f'Fetching passive data for {crypto} in {platform}')
        gemini_passive_data = {}

        url = 'https://exchange.gemini.com/earn/maxInterestRates'
        response = requests.request("GET", url)
        json_data_rates = json.loads(response.text)

        for rate in json_data_rates:
            gemini_passive_data.setdefault(rate[0], [rate[1]])
        with open(f"data/{platform.lower()}_passive.json", mode="w", encoding="UTF-8") as gemini_data_json:
            json.dump(gemini_passive_data, gemini_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open(f"data/{platform.lower()}_passive.json", mode="r", encoding="UTF-8") as json_gemini_passive:
            gemini_passive_data = json.load(json_gemini_passive)

    return return_function(crypto, platform, gemini_passive_data)


def gateio_data(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in gate.io
    Return: gate.io rates for ticker
    """

    platform = "gate.io"
    # print(f'Fetching passive data for {crypto} in {platform}')

    rates = [*gateio_staking(crypto), *gateio_lending(crypto), *gateio_liquidity_mining(crypto)]

    return return_function(crypto, platform, rates, api=True)


def gateio_staking(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in gate.io Earn
    Return: gate.io Earn staking rates for ticker
    """
    rates = []
    url = f'https://www.gate.io/hodl/hold_finances_search?search={crypto}'
    response = requests.request("GET", url)
    if json_data_rates := json.loads(response.text)['data']:
        rates.extend(apr_to_apy(float(rates_data['year_rate']) / 100) for rates_data in json_data_rates if rates_data['status'] != 3)

    return rates


def gateio_liquidity_mining(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in gate.io Liquidity Mining
    Return: gate.io Liquidity Mining latest rate for ticker
    """

    url = f"https://www.gate.io/zmlend/trend?asset={crypto}"
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)['data']
    return [json_data_rates[0]['annualized_return_rate'] / 100] if json_data_rates else []


def gateio_lending(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in gate.io Lending
    Return: gate.io Lending rates for ticker
    """

    form_data = {'asset': crypto}
    url = "https://www.gate.io/json_svr/get_lend_orderbook"
    response = requests.request("POST", url, data=form_data)
    json_data_rates = json.loads(response.text)['data']

    rates = []
    if json_data_rates:
        number_rates = 3
        rates.extend(apr_to_apy(float(json_data_rates[i]['year_rate'].replace('%', '')) / 100) for i in range(number_rates))

    return rates


def huobi_data(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Huobi
    Return: Huobi rates for ticker
    """

    platform = "Huobi"
    # print(f'Fetching passive data for {crypto} in {platform}')

    staking_rates = return_function(crypto, platform, huobi_staking())
    savings_rates = return_function(crypto, platform, huobi_savings(crypto), api=True)

    return [*staking_rates, *savings_rates]


def huobi_staking():
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Huobi Staking
    Return: Huobi staking rates for ticker
    """
    platform = "Huobi"

    data_path_file = "data/huobi_passive.json"

    if not os.path.isfile(data_path_file):
        huobi_passive_data = {}

        url = "https://www.huobi.com/-/x/hbg/v1/hbps/vote/product/list?r=cyold"
        url_v2 = "https://pool.huobi.cg/hbp/eth2/v1/staking/eth2/profit?r=ogr1b"
        response = requests.request("GET", url)
        response_v2 = requests.request("GET", url_v2)
        json_data_rates = json.loads(response.text)['data']
        json_data_rates_v2 = json.loads(response_v2.text)['data']
        for rate in json_data_rates:
            huobi_passive_data.setdefault(rate['currency'], [float(rate['annualizedRate'])])
        huobi_passive_data.setdefault('BETH', [apr_to_apy(float(json_data_rates_v2['b']))])

        with open(f"data/{platform.lower()}_passive.json", mode="w", encoding="UTF-8") as huobi_data_json:
            json.dump(huobi_passive_data, huobi_data_json, indent=4)
    else:
        # print(f"Fetching passive data for {crypto} in json file {platform}...")
        with open(f"data/{platform.lower()}_passive.json", mode="r", encoding="UTF-8") as json_huobi_passive:
            huobi_passive_data = json.load(json_huobi_passive)

    return huobi_passive_data


def huobi_savings(crypto):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in Huobi Earn
    Return: Huobi earn rates for ticker
    """

    rates = []

    url = f"https://www.huobi.com/-/x/hbg/v3/saving/mining/project/steady_financial/search?currency={crypto}"
    url_limited = f"https://www.huobi.com/-/x/hbg/v3/saving/mining/project/limit_time/search?currency={crypto}"
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)['data']
    response_limited = requests.request("GET", url_limited)
    json_data_rates_limited = json.loads(response_limited.text)['data']

    if json_data_rates:
        rates.extend(rate['viewYearRate'] for rate in json_data_rates[0]['projects'])
    if json_data_rates_limited:
        rates.append(json_data_rates_limited[0]['viewYearRate'])

    return rates


def return_function(crypto, platform, data, api=False):
    """
    Params:
        crypto: token/coin
        platform: name of the platform
        data: data used to fetch crypto data
        api: boolean for "api" support
    Function: template for returns
    Return: print message and fetched data
    """

    if not api:
        if data.get(crypto) is not None:
            # print(f'{list(data.get(crypto))}\n')
            return list(data.get(crypto))
    elif data:
        # print(f'{list(data)}\n')
        return list(data)
    # print(f'NOT FOUND: No data for {crypto} in {platform}\n')
    return []


def refresh_data():
    """
    Function: Delete all data files and rerun all scraping functions
    """
    path = "data"
    filelist = [f for f in os.listdir(path) if f.endswith(".json")]
    for file in filelist:
        os.remove(os.path.join(path, file))

    get_passive_crypto_data('data refresh')


def backup_data():
    """
    Function: Create a backup folder for the data in case refresh can't find data for platforms
    """
    destination_dir = 'backup_data'
    source_dir = 'data'
    if os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)
    shutil.copytree(source_dir, destination_dir)
