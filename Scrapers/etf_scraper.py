"""
Scrape all ETF tickers from lib
"""
import yfinance as yf

vwce = yf.Ticker('VWCE.DE')
print(vwce.info['annualReportExpenseRatio'])
