"""
Scrape all ETF tickers from lib
"""


import itertools
import requests

MAX_SIZE_REQUEST = 250
ETF_LENGTH = 39716  # from yahoo finance etfs Price intraday > 0

intraday_filters = [[-9999, 20], [20.001, 47], [47.001, 125], [125.001, 10000], [10000.001, 999999]]

cookies = {
    'B': 'c8h9uoth5lrkc&b=3&s=k2',
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
}

params = {
    'crumb': 'MMTZFySYw5h',
}

etf_tickers = []

for intra_range, top_offset in itertools.product(intraday_filters, range(MAX_SIZE_REQUEST, 10249, MAX_SIZE_REQUEST)):
    json_data = {
        'size': MAX_SIZE_REQUEST,
        'offset': top_offset - MAX_SIZE_REQUEST,
        'sortField': 'fundnetassets',
        'quoteType': 'ETF',
        'query': {
            'operator': 'AND',
            'operands': [
                {
                    'operator': 'btwn',
                    'operands': [
                        'intradayprice',
                        intra_range[0],
                        intra_range[1],
                    ],
                },
            ],
        },
    }
    response = requests.post('https://query2.finance.yahoo.com/v1/finance/screener',
                             headers=headers, params=params, cookies=cookies, json=json_data)
    json_response = response.json()
    etf_tickers.extend(quote['symbol'] for quote in json_response['finance']['result'][0]['quotes'])

with open('../data/etf_tickers.txt', 'w', encoding='UTF-8') as txt_crypto_tickers:
    txt_crypto_tickers.write("\n".join(map(str, etf_tickers)))

print(f'{len(etf_tickers)} ETF tickers were scraped from Yahoo Finance')

print(len(etf_tickers))
