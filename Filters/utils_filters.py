import concurrent.futures
import json
import time
from itertools import repeat

import numpy as np
import requests_cache
import yfinance as yf

from MST import MinimumSpanningTree


def date_filter(filename:str, start_date:str, ticker_type:str, target_name:str):
    tickers = []
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')
    start_date = np.datetime64(start_date)
    tickers_data = yf.download(tickers,start=start_date, end=start_date + np.timedelta64(7, 'D'))
    print(tickers_data)
    new_tickers = [ticker for ticker in tickers if not tickers_data['Adj Close'][ticker].isnull().all()]

    with open(f'../data/{ticker_type}-{target_name}-f.txt', 'w', encoding='UTF-8') as txt_date_filtered:
        txt_date_filtered.write("\n".join(map(str, new_tickers)))


def volume_filter(filename:str, start_date:str, end_date:str, minimum:int, ticker_type:str):
    tickers = []
    new_tickers = []
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')

    tickers_data = yf.download(tickers, start=start_date, end=end_date).sort_index()
    print(tickers_data)
    if ticker_type == 'etf':
        new_tickers = [ticker for ticker in tickers if tickers_data['Volume'][ticker].mean() >= minimum]
    else:
        new_tickers = [ticker for ticker in tickers if (tickers_data['Volume'][ticker] / tickers_data['Close'][ticker]).mean() >= minimum]

    with open(f'../data/{ticker_type}-volume-f.txt', 'w', encoding='UTF-8') as txt_volume_filtered:
        txt_volume_filtered.write("\n".join(map(str, new_tickers)))

def rates_filter(filename:str):
    tickers = []
    rates_dict = {}
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')
    with open('../data/rates.json', 'r', encoding="UTF-8") as rates_file:
        rates_dict = json.load(rates_file)
    all_keys = rates_dict.keys()

    all_keys = [f'{key}-USD' for key in all_keys]
    new_tickers = [ticker for ticker in tickers if ticker in all_keys]

    with open('../data/crypto-rates-f.txt', 'w', encoding='UTF-8') as txt_rates_filtered:
        txt_rates_filtered.write("\n".join(map(str, new_tickers)))

def expense_ratio_filter_yf(filename:str, maximum:float, check_filtered=False, check_none=False):
    session = requests_cache.CachedSession('dns.cache')
    session.headers['User-agent'] = 'Opera/9.60 (Windows NT 6.0; U; en) Presto/2.1.1'
    tickers = []
    new_tickers = []
    none_tickers = []
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')
    if check_filtered:
        with open('../data/etf-er-f.txt', "r", encoding="UTF-8") as ticker_file:
            new_tickers = ticker_file.read().split('\n')
            if not check_none:
                tickers = list(set(tickers) - set(new_tickers))
    if check_none:
        with open('../data/etf-er-none.txt', "r", encoding="UTF-8") as ticker_file:
            tickers = ticker_file.read().split('\n')

    tickers_to_analyse = tickers
    chunk_size = 5
    chunks = [tickers_to_analyse[i:i+chunk_size] for i in range(0,len(tickers_to_analyse),chunk_size)]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(er_helper, chunks, repeat(maximum), repeat(session))
        for result in results:
            new_tickers.extend(result['new_tickers'])
            none_tickers.extend(result['none_tickers'])

    with open('../data/etf-er-f.txt', 'w', encoding='UTF-8') as txt_er_filtered:
        txt_er_filtered.write("\n".join(map(str, new_tickers)))

    with open('../data/etf-er-none.txt', 'w', encoding='UTF-8') as txt_er_filtered:
        txt_er_filtered.write("\n".join(map(str, none_tickers)))


def er_helper(chunk:list, maximum:float, session):
    new_tickers = []
    none_tickers = []
    tickers_data = [yf.Ticker(t, session=session) for t in chunk]
    for ticker in tickers_data:
        time.sleep(1)
        expense_ratio = ticker.info['annualReportExpenseRatio']
        print(f"{ticker.ticker} ::: {expense_ratio}")
        if expense_ratio is None:
            none_tickers.append(ticker.ticker)
            continue
        if expense_ratio <= maximum:
            new_tickers.append(ticker.ticker)
            continue
    return {'new_tickers': new_tickers, 'none_tickers': none_tickers}

def mst_filter(filename:str):
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')

    tickers_data = yf.download(tickers[:100], start="2021-01-01", end="2022-01-01", interval="1wk")["Adj Close"]
    tickers_data.dropna(inplace=True)
    tickers_return = tickers_data.pct_change()[1:] # Remove first row of NaN values
    print(tickers_return)
    new_tickers = []

    while tickers_return.shape[1] > 30:
        new_tickers,tickers_return,_,_ = MinimumSpanningTree(tickers_return)

    print(tickers_return)
    print(new_tickers)

mst_filter('../data/etf-date-f.txt')
