"""
Scrape all crypto tickers from yahoo finance
"""

import itertools
import requests


def get_all_crypto_tickers():
    """
    Function: Scrape all crypto tickers from yahoo finance
              Create file with all crypto tickers
    """

    print("Fetching all crypto tickers...")

    max_size_request = 1

    cookies = {
        'B': 'f7i1kt5h5sqj5&b=3&s=te',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0',
    }

    params = {
        'crumb': '5rQZsj6YTeI',
    }

    crypto_tickers = []

    for top_offset in range(max_size_request, 10000 + max_size_request, max_size_request):
        json_data = {
            'offset': top_offset - max_size_request,
            'size': max_size_request,
            'sortType': 'desc',
            'sortField': 'ticker',
            'quoteType': 'CRYPTOCURRENCY',
            'query': {
                'operator': 'and',
                'operands': [
                    {
                        'operator': 'eq',
                        'operands': [
                            'currency',
                            'USD',
                        ],
                    },
                    {
                        'operator': 'eq',
                        'operands': [
                            'exchange',
                            'CCC',
                        ],
                    },
                ],
            },
            'userId': '',
            'userIdType': 'guid',
        }
        response = requests.post('https://query2.finance.yahoo.com/v1/finance/screener',
                                 headers=headers, params=params, cookies=cookies, json=json_data)
        json_response = response.json()
        print(json_response)
        crypto_tickers.extend(
            quote['symbol'] for quote in json_response['finance']['result'][0]['quotes'])

    with open('../data/new_crypto_tickers.txt', 'w', encoding='UTF-8') as txt_crypto_tickers:
        txt_crypto_tickers.write("\n".join(map(str, crypto_tickers)))

    print(f'{len(crypto_tickers)} crypto tickers were scraped from Yahoo Finance')


get_all_crypto_tickers()
