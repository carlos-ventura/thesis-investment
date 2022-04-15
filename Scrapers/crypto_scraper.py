"""
Scrape all crypto tickers from CoinMarketCap
"""

import json
import requests


def get_all_crypto_tickers():
    """
    Function: Scrape all crypto tickers from coinmarketcap
              Create file with all crypto tickers
    Return: All the crypto tickers
    """

    print("Fetching all crypto tickers...")

    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=999999&convert=USD&cryptoType=all&tagType=all"
    response = requests.request("GET", url)
    json_data = json.loads(response.text)
    crypto_tickers = [crypto['symbol'] for crypto in json_data['data']['cryptoCurrencyList']]

    with open('../data/crypto_tickers.txt', 'w', encoding='UTF-8') as txt_crypto_tickers:
        txt_crypto_tickers.write("\n".join(map(str, crypto_tickers)))

    print(f'{len(crypto_tickers)} cryptocurrency tickers were scraped from coinmarketcap')

get_all_crypto_tickers()
