"""
Constants to generate different results with different models
"""

from compute import get_passive_investment_data


PORTFOLIO_INDEX_WEIGHT = 0.8
PORTFOLIO_CRYPTO_WEIGHT = 1 - PORTFOLIO_INDEX_WEIGHT
FUNNEL_APPROACH = False

# Options of Crypto to choose
CRYPTO_OPTIONS = ['DAI', 'BTC', 'ETH']

CRYPTO_BASKET = ['DAI', 'BTC', 'ETH']

INITIAL_INVESTMENT = 100
DCA_MONTHLY = 0  # default

APPLIED_CRYPTO = get_passive_investment_data(CRYPTO_BASKET)
print(APPLIED_CRYPTO)

PLATFORMS = {
    'DeFi': ['Binance', 'Crypto.com', 'Coinbase', 'Kraken', 'OKX', 'KuCoin', 'BlockFi', 'Gemini', 'gate.io', 'Huobi'],
    'CeFi': ['PancakeSwap (v2)', 'Uniswap (v3)']
}
