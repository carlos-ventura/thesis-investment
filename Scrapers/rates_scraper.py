"""
Scrape data from platforms for crypto lending, staking and savings
"""
import sys
import os
import time
import concurrent.futures
import urllib
import urllib.request
import urllib.parse
import json
import hashlib
import hmac
import base64
import collections
import pandas as pd
import requests

sys.path.append('../')
import utils as u # pylint: disable=import-error $disable=wrong-import-position
sys.path.pop()

RATES_CRYPTO_DICT = collections.defaultdict(list)

def add_to_dict(token, rates: list):
    rates = [float(r) for r in rates]
    token = str(token)
    RATES_CRYPTO_DICT[token].extend(rates)

def scraper_print(platform):
    print(f"Scraping rates from ::: {platform} :::")

def binance_savings():
    url_flex = "https://www.binance.com/bapi/earn/v1/friendly/lending/daily/product/list?pageSize=200&pageIndex=1"
    url_fixed = 'https://www.binance.com/bapi/earn/v1/friendly/lending/project/customizedFixedProject/list?pageSize=100&pageIndex=1&status=ALL'
    json_data_flex = requests.request("GET", url_flex).json()['data']
    json_data_fixed = requests.request("GET", url_fixed).json()['data']

    for asset in json_data_flex:
        token = asset['asset']
        flex_rates = []
        if asset['tierAnnualInterestRateList']:
            flex_rates.extend(new_rate['annualInterestRate'] for new_rate in asset['tierAnnualInterestRateList'])
        else:
            flex_rates.append(asset['latestAnnualInterestRate'])
        add_to_dict(token, flex_rates)

    for asset in json_data_fixed:
        token = asset['asset']
        fixed_rates = [u.apr_to_apy(rate['interestRate']) for rate in asset['list']]
        add_to_dict(token, fixed_rates)

def binance_staking():
    url = "https://www.binance.com/bapi/earn/v1/friendly/pos/union?pageSize=200&pageIndex=1&status=ALL"
    url_defi = 'https://www.binance.com/bapi/earn/v2/friendly/defi-pos/groupByAssetAndPartnerNameList?pageSize=50&pageIndex=1&status=ALL'
    time.sleep(1)
    json_data = requests.request("GET", url).json()['data']
    time.sleep(1)
    json_data_defi = requests.request("GET", url_defi).json()['data']
    complete_data = json_data + json_data_defi

    for asset in complete_data:
        rates = []
        token = asset['asset']
        if asset['projects']:
            rates.extend(proj['config']['annualInterestRate'] for proj in asset['projects'])
        else:
            rates.append(asset['annualInterestRate'])
        add_to_dict(token , rates)

def binance():
    scraper_print('Binance')
    binance_savings()
    binance_staking()

def crypto_com():
    scraper_print('Crypto.com')

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
            passive_rates_apr_pd[i] = passive_rates_apr_pd[i].apply(u.apr_to_apy)

    crypto_com_passive_data = passive_rates_apr_pd.set_index(0).T.to_dict('list')

    stablecoins_values = crypto_com_passive_data.pop('Stablecoins')
    stablecoins = ['USDT', 'USDC', 'DAI', 'PAX', 'TUSD', 'TAUD', 'TCAD', 'TGBP']
    for stable in stablecoins:
        crypto_com_passive_data[stable] = stablecoins_values
    for key in crypto_com_passive_data.copy().keys():
        if ',' in key:
            rates = crypto_com_passive_data.pop(key)
            keys = key.replace(' ', '').split(',')
            for new_key in keys:
                crypto_com_passive_data[new_key] = rates
    del crypto_com_passive_data['Other tokens']

    for key in crypto_com_passive_data.keys():
        add_to_dict(key, crypto_com_passive_data[key])


def defirate():
    scraper_print('DeFi Rate')

    url = 'https://defirate.com/lend/'
    html = requests.get(url).content
    df_list = pd.read_html(html)
    passive_rates_pd = df_list[1]
    passive_rates_pd = passive_rates_pd.T.reset_index(drop=True).T
    for i in range(11):
        passive_rates_pd[i+1] = passive_rates_pd[i + 1].str.strip('%').replace('–', '0').astype('float') / 100
    defirate_passive_data = passive_rates_pd.set_index(0).T.to_dict('list')

    for key in defirate_passive_data.keys():
        defirate_passive_data[key] = list(filter(lambda num: num != 0, defirate_passive_data[key]))
        add_to_dict(key, defirate_passive_data[key])

def okx():
    scraper_print('OKX')

    url = "https://www.okx.com/v2/asset/balance/project-currency"
    response = requests.request("GET", url)
    json_data = json.loads(response.text)

    for data in json_data['data']:
        token = data['currencyName']
        temp_apy = [proj['rateRangeMaxCompar'] / 100 for proj in data['projectList'] if 'dual' not in proj['url']]
        add_to_dict(token, temp_apy)


def kucoin_earn():
    url="https://www.kucoin.com/_pxapi/pool-staking/v3/products/currencies?lang=en_US"
    json_data = requests.request('GET', url).json()
    for asset in json_data['data']:
        token = asset['currency']
        rates = []
        for prod in asset['products']:
            try:
                apy = u.apr_to_apy(float(prod['apr']) + float(prod['pol_apr']), percentage=True)
            except Exception:
                continue
            rates.append(apy)
        add_to_dict(token, rates)

def kucoin_lending():
    url = 'https://www.kucoin.com/_api/margin-config/loan-currencies?lang=en_US'
    json_data = requests.request('GET', url).json()
    url = "https://www.kucoin.com/_api/margin-loan/loan/order/query-min-int-rate?lang=en_US"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(kucoin_lending_helper, asset, url) for asset in json_data['data']]
        for future in concurrent.futures.as_completed(results):
            add_to_dict(future.result()['token'], future.result()['rates'])

def kucoin_lending_helper(asset, url):
    time.sleep(1)
    token = asset['currencyName']
    form_data = {'currency': token}
    json_data = requests.request("POST", url, data=form_data,).json()
    rates = []
    for daily_rates in json_data['data']:
        apy = u.apr_to_apy(u.daily_to_annualy(daily_rates['interestRate']))
        rates.append(apy)
    return {'token': token, 'rates': rates}

def kucoin():
    scraper_print('Kucoin')
    kucoin_earn()
    kucoin_lending()

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sec, api_url):
    headers = {'API-Key': api_key, 'API-Sign': get_kraken_signature(uri_path, data, api_sec)}
    return requests.post((api_url + uri_path), headers=headers, data=data)

def kraken():
    scraper_print('Kraken')
    api_key = os.environ.get('kraken-api-key')
    api_sec = os.environ.get('kraken-secret')
    api_url = "https://api.kraken.com"
    resp = kraken_request('/0/private/Staking/Assets', {"nonce": str(int(1000*time.time()))}, api_key, api_sec, api_url).json()
    for res in resp['result']:
        token=res['asset']
        rates = res['rewards']['reward']
        if '-' in rates:
            rates = rates.split('-')
            rates = [float(r)/100 for r in rates]
        else :
            rates = [float(rates) / 100]
        add_to_dict(token, rates)

def gemini():
    scraper_print('Gemini')

    url = 'https://exchange.gemini.com/earn/maxInterestRates'
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)

    for rate in json_data_rates:
        add_to_dict(rate[0], [rate[1]])

def gateio_earn():
    url='https://www.gate.io/zmlend/pools'
    json_data = requests.request("GET", url).json()['data']
    for item in json_data:
        add_to_dict(item['asset'], [item['annualized_7d_rate']/100])

    url_lock = 'https://www.gate.io/hodl/get_lock_list'
    json_data_lock = requests.request("GET", url_lock).json()['data']
    lock_data = json_data_lock['underway'] + json_data_lock['preheat']
    for item in lock_data:
        add_to_dict(item['interest_coin'], [float(item['year_rate'])/100])

def gateio_liquidity_mining():
    url = 'https://www.gate.io/zmlend/pools'
    json_data = requests.request("GET", url).json()
    for asset in  json_data['data']:
        token = asset['asset']
        rate = asset['annualized_7d_rate'] / 100
        add_to_dict(token, [rate])

def gateio_lending_helper(asset):
    """
    Params: crypto (ticker)
    Function: Scrap APY for ticker in gate.io Lending
    Return: gate.io Lending rates for ticker
    """
    url = "https://www.gate.io/json_svr/get_lend_orderbook"
    form_data = {'asset': asset}
    response = requests.request("POST", url, data=form_data).json()
    json_data_rates = response['data']

    rates = []
    if json_data_rates:
        number_rates = min(3, len(json_data_rates))
        rates.extend(u.apr_to_apy(float(json_data_rates[i]['year_rate'].replace('%', '')) / 100) for i in range(number_rates))

    return {'token': asset, 'rates': rates}

def gateio_lending():
    url = r'https://www.gate.io/margin/lend/'
    header= {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    req = requests.get(url, headers=header)
    assets = pd.read_html(req.text)[0][0].values
    new_assets = [asset.split(' ')[0] for asset in assets]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(gateio_lending_helper, asset) for asset in new_assets]
        for future in concurrent.futures.as_completed(results):
            add_to_dict(future.result()['token'], future.result()['rates'])

def gateio():
    scraper_print('gate.io')
    gateio_earn()
    gateio_lending()
    gateio_liquidity_mining()

def huobi_staking():
    url = "https://www.huobi.com/-/x/hbg/v1/hbps/vote/product/list?r=cyold"
    response = requests.request("GET", url)
    json_data_rates = json.loads(response.text)['data']
    for rate in json_data_rates:
        add_to_dict(rate['currency'], [float(rate['annualizedRate'])])

def huobi_savings():
    url = "https://www.huobi.com/-/x/hbg/v3/saving/mining/project/steady_financial/search"
    url_limited = "https://www.huobi.com/-/x/hbg/v3/saving/mining/project/limit_time/search"
    json_data = requests.request("GET", url).json()['data']
    json_data_limited = requests.request("GET", url_limited).json()['data']
    completed_list = json_data + json_data_limited

    for item in completed_list:
        rates = []
        token = item['currency']
        if 'projects' in item:
            rates.extend(float(rate['viewYearRate']) for rate in item['projects'])
        else:
            rates.append(float(item['viewYearRate']))
        add_to_dict(token, rates)
def huobi():
    scraper_print('Huobi')
    huobi_savings()
    huobi_staking()

def create_files():
    with open('../data/rates.json', 'w', encoding='utf8') as crypto_dict_rates:
        json.dump(RATES_CRYPTO_DICT, crypto_dict_rates, indent=4)
    with open('../data/crypto-ticker-rates.txt', 'w', encoding='utf8') as crypto_dict_rates:
        crypto_dict_rates.write("\n".join(map(str, RATES_CRYPTO_DICT.keys())))

if __name__ == "__main__":
    start_time = time.time()

    binance()
    crypto_com()
    defirate()
    okx()
    kucoin()
    kraken()
    gemini()
    gateio()
    huobi()

    create_files()

    print(f"Scraping rates took --- {time.time() - start_time} seconds ---")
