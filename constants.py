"""
Constants to generate different results with different models
"""

from compute import get_passive_investment_data

WORLD_ETF_TICKERS = ["VWCE.DE", "MSCI", "ACWI"]

PORTFOLIO_INDEX_WEIGHT = 0.8
PORTFOLIO_CRYPTO_WEIGHT = 1 - PORTFOLIO_INDEX_WEIGHT
FUNNEL_APPROACH = False

START_TEST_DATE = 0  # TODO
END_TEST_DATE = 0  # TODO

# Options of Crypto to choose
CRYPTO_OPTIONS = ['DAI', 'BTC', 'ETH']

CRYPTO_BASKET = ['BTC']

INITIAL_INVESTMENT = 100
DCA_MONTHLY = 0  # default

APPLIED_CRYPTO_RATES = get_passive_investment_data(CRYPTO_BASKET)

PLATFORMS = ['Binance', 'Crypto.com', 'DeFiRate', 'OKX', 'KuCoin', 'Kraken', 'Gemini', 'gate.io', 'Huobi']

WEBSITES = [
    "https://www.binance.com/en/savings", "https://www.binance.com/en/pos", "https://www.binance.com/en/defi-staking",
    "https://crypto.com/eea/earn",
    "https://defirate.com/lend/",
    "https://www.okx.com/earn",
    "https://www.kucoin.com/margin/lend", "https://www.kucoin.com/earn/finance/list?type=DEMAND",
    "https://www.kucoin.com/earn/finance/list?type=STAKING",
    "https://www.kraken.com/features/staking-coins/",
    "https://www.gemini.com/earn",
    "https://www.gate.io/hodl", "https://www.gate.io/margin/lend/", "https://www.gate.io/lending/liquidity#market"
    "https://www.huobi.com/en-us/staking/vote/", "https://www.huobi.com/en-us/staking/eth2/", "https://www.huobi.com/en-us/financial/earn/?type=limit"
]
