"""
Constants to generate different results with different models
"""

from compute import get_passive_investment_data


PORTFOLIO_INDEX_WEIGHT = 0.8
PORTFOLIO_CRYPTO_WEIGHT = 1 - PORTFOLIO_INDEX_WEIGHT
FUNNEL_APPROACH = False

# Options of Crypto to choose
CRYPTO_OPTIONS = ['DAI', 'BTC', 'ETH']

CRYPTO_BASKET = ['DAI', 'BTC']

INITIAL_INVESTMENT = 100
DCA_MONTHLY = 0  # default

APPLIED_CRYPTO_RATES = get_passive_investment_data(CRYPTO_BASKET)
print(APPLIED_CRYPTO_RATES)

PLATFORMS = ['Binance', 'Crypto.com', 'DeFiRate', 'Kraken', 'OKX', 'KuCoin', 'BlockFi', 'Gemini', 'gate.io', 'Huobi']

WEBSITES = [
    "https://www.binance.com/en", "https://crypto.com/eea/", "https://defirate.com/", "https://www.kraken.com/", "https://www.okx.com/",
    "https://www.kucoin.com/", "https://www.blockfi.com/", "https://www.gemini.com/eu", "https://www.gate.io/", "https://www.huobi.com/en-us/"
]
