"""
Constants to generate different results with different models
"""

WORLD_ETF_TICKERS = ["VWCE.DE", "MSCI", "ACWI"]

ETF_WEIGHT = 0.95
CRYPTO_WEIGHT = 1 - ETF_WEIGHT

START_DATES = ['2017-11-06', '2018-05-01', '2019-05-01', '2020-05-01', '2021-05-01']
END_DATE = '2022-05-01'

MST_MODES = ['', 'sr0', 'sr1']
MST_TYPES = ['separate', 'joint']

OPTIMIZER_MEASURES = ['min volatility', 'efficient return', 'efficient risk']

MINIMUM_DAILY_VOLUME = 50000
MAXIMUM_EXPENSE_RATIO = 0.005

START_TEST_DATE = 0  #TODO
END_TEST_DATE = 0  #TODO

DCA_MONTHLY = 0  # default
