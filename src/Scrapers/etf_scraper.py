"""
Scrape all ETF tickers from yahoo finance
"""

import itertools
import requests


def get_all_etf_tickers():
    """
    Function: Scrape all ETF tickers from yahoo finance
              Create file with all ETF tickers
    """

    print("Fetching all ETF tickers...")

    max_size_request = 250

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

    for intra_range, top_offset in itertools.product(intraday_filters, range(max_size_request, 10249, max_size_request)):
        json_data = {
            'size': max_size_request,
            'offset': top_offset - max_size_request,
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

    with open('../data/etf-tickers.txt', 'w', encoding='UTF-8') as txt_etf_tickers:
        txt_etf_tickers.write("\n".join(map(str, etf_tickers)))

    print(f'{len(etf_tickers)} ETF tickers were scraped from Yahoo Finance')
