"""
Constants to generate different results with different models
"""

WORLD_ETF_TICKERS = [ "IWDA.AS", "ACWI", 'VWCE.DE']
BENCHMARK_RISK = 0.2

START_DATE = '2017-11-06'
#START_DATES = ['2017-11-06'] 
#START_DATES = ['2019-05-01']

END_DATE = '2022-05-01'

START_TEST_DATE = '2019-03-11'
#START_TEST_DATES = ['2019-03-11']
#START_TEST_DATES = ['2020-03-23']

MST_MODES = ['', 'sr0', 'sr1']
MST_TYPES = ['separate','joint'] 

OPTIMIZER_MEASURES = ['min volatility','efficient risk'] # efficient risk, min volatility

MODEL_INPUTS = ['Empty', 'Min w', "Penalty", "Min w and Penalty"]

PASSIVE_MODES = ["min", "mean", "max"]

MINIMUM_DAILY_VOLUME = 2000000 # Dollars
MAXIMUM_EXPENSE_RATIO = 0.005
MAXIMUM_ANNUAL_STD = 2

MONEY_INVESTMENT = 100
