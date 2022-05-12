import concurrent.futures
import json
import time
from itertools import repeat
import os

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

    tickers_data = yf.download(tickers, start=start_date, end=end_date, interval='1d')
    tickers_data.dropna(how='all', inplace=True)
    print(tickers_data)
    if ticker_type == 'etf':
        new_tickers = [ticker for ticker in tickers if tickers_data['Volume'][ticker].mean() >= minimum]
    else:
        new_tickers = [ticker for ticker in tickers if (tickers_data['Volume'][ticker] / tickers_data['Close'][ticker]).mean() >= minimum]

    with open(filename, 'w', encoding='UTF-8') as txt_volume_filtered:
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

def expense_ratio_filter_yf(filename:str, maximum:float):
    session = requests_cache.CachedSession('yahoo_finance.cache')
    session.headers['User-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41'
    new_tickers = []
    none_tickers = []
    above_tickers= []

    with open(filename, "r", encoding="UTF-8") as ticker_file:
        none_tickers = ticker_file.read().split('\n')

    if not os.path.exists('../data/etf-er-none.txt'):
        with open('../data/etf-er-none.txt', "w", encoding="UTF-8") as ticker_none_file:
            ticker_none_file.write("\n".join(map(str, none_tickers)))
    else:
         with open('../data/etf-er-none.txt', 'r', encoding='UTF-8') as ticker_none_file:
             none_tickers = ticker_none_file.read().split("\n")

    if os.path.exists('../data/etf-er-above.txt'):
        with open('../data/etf-er-above.txt', 'r', encoding='UTF-8') as ticker_above_file:
            above_tickers = ticker_above_file.read().split("\n")

    if os.path.exists('../data/etf-er-f.txt'):
        with open('../data/etf-er-f.txt', 'r', encoding='UTF-8') as ticker_f_file:
            new_tickers = ticker_f_file.read().split("\n")

    none_tickers = none_tickers[25:]
    tickers_to_analyse = none_tickers[:25]

    chunk_size = 5
    chunks = [tickers_to_analyse[i:i+chunk_size] for i in range(0,len(tickers_to_analyse),chunk_size)]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(er_helper, chunks, repeat(maximum), repeat(session))
        temp_none = []
        for result in results:
            print(f" new tickers : {len(result['new_tickers'])} \n none tickers : {len(result['none_tickers'])} \n above tickers : {len(result['above_tickers'])}")
            new_tickers.extend(result['new_tickers'])
            temp_none.extend(result['none_tickers'])
            above_tickers.extend(result['above_tickers'])

    none_tickers.extend(temp_none)

    print("\nWritting to files...\n")
    time.sleep(1)

    with open('../data/etf-er-f.txt', 'w', encoding='UTF-8') as txt_er_filtered:
        txt_er_filtered.write("\n".join(map(str, new_tickers)))

    with open('../data/etf-er-none.txt', 'w', encoding='UTF-8') as txt_er_filtered:
        txt_er_filtered.write("\n".join(map(str, none_tickers)))

    with open('../data/etf-er-above.txt', 'w', encoding='UTF-8') as txt_er_filtered:
        txt_er_filtered.write("\n".join(map(str, above_tickers)))


def er_helper(chunk:list, maximum:float, session):
    new_tickers = []
    none_tickers = []
    above_tickers = []
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
        above_tickers.append(ticker.ticker)
    return {'new_tickers': new_tickers, 'none_tickers': none_tickers, 'above_tickers': above_tickers}

def mst_filter(filename:str, start_date:str, end_date:str, target_name:str, ticker_type:str):
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')

    tickers_data = yf.download(tickers, start=start_date, end=end_date, interval="1wk")["Adj Close"]
    tickers_data.dropna(how='all', inplace=True)
    print(tickers_data)
    tickers_return = tickers_data.pct_change()[1:] # Remove first row of NaN values
    new_tickers = []

    while tickers_return.shape[1] > 20:
        print('Applying mst...')
        new_tickers,tickers_return,_,_ = MinimumSpanningTree(tickers_return)
        print(len(new_tickers))

    with open(f"../data/{ticker_type}-{target_name}-mst-f", 'w', encoding='UTF-8') as txt_mst_filtered:
        txt_mst_filtered.write("\n".join(map(str, new_tickers)))

    print(new_tickers)

# mst_filter('../data/etf-date-f.txt')
