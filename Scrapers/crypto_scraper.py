"""
Scrape all crypto tickers from yahoo finance
"""
import time
import requests

MAX_REQUEST_YAHOO_FINANCE = 10000


def get_all_crypto_tickers():
    """
    Function: Scrape all crypto tickers from yahoo finance
              Create file with all crypto tickers
    """

    print("Fetching all crypto tickers...")

    max_size_request = 100

    cookies = {
        'B': '3t00p3th5u5k9&b=3&s=s2',
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    }

    params = {
        'crumb': 'u8JdN/0.c1I',
    }

    crypto_tickers = ['XVC-USD']  # Bug in yahoo finance
    for offset in range(0, MAX_REQUEST_YAHOO_FINANCE, max_size_request):
        json_data = {
            'offset': offset if offset < MAX_REQUEST_YAHOO_FINANCE else 0,
            'size': max_size_request,
            'sortType': 'asc' if offset < 10000 else 'desc',
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
        time.sleep(10)
        json_response = response.json()
        for quote in json_response['finance']['result'][0]['quotes']:
            try:
                crypto_tickers.append(quote['symbol'])
            except Exception as e:
                print(e)

    with open('../data/crypto-tickers.txt', 'w', encoding='UTF-8') as txt_crypto_tickers:
        txt_crypto_tickers.write("\n".join(map(str, set(crypto_tickers))))

    print(f'{len(crypto_tickers)} crypto tickers were scraped from Yahoo Finance')


get_all_crypto_tickers()
