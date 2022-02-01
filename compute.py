"""
File with utils and computation functions
"""

from scraper import get_passive_crypto_data


def get_passive_investment_data(crypto_basket):
    """
    Argument: Basket of cryptos (ticker)
    Function: Generate types of passive investment on the basket of cryptocurrencies
    Return: Dictionary with options
    """

    crypto_passive_basket = {}

    for crypto in crypto_basket:

        crypto = str(crypto.upper())
        crypto_passive_data = get_passive_crypto_data(crypto)
        crypto_passive_basket.setdefault(crypto, crypto_passive_data)

    return crypto_passive_basket
