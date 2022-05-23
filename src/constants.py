"""
Constants to generate different results with different models
"""

WORLD_ETF_TICKERS = [ "IWDA.AS", "ACWI", 'VWCE.DE']
BENCHMARK_RISK = 0.2

ETF_WEIGHT = 0.95
CRYPTO_WEIGHT = 1 - ETF_WEIGHT

START_DATES = ['2017-11-06', '2019-05-01']
END_DATE = '2022-05-01'

MST_MODES = ['', 'sr0', 'sr1']
MST_TYPES = ['separate', 'joint']

OPTIMIZER_MEASURES = ['efficient risk'] # efficient risk, min volatility

MINIMUM_DAILY_VOLUME = 2000000 # Dollars
MAXIMUM_EXPENSE_RATIO = 0.005
MAXIMUM_ANNUAL_STD = 2

