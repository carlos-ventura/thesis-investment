import yfinance as yf
import numpy as np

def date_filter(filename:str, start_date:str, ticker_type:str):
    tickers = []
    with open(filename, "r", encoding="UTF-8") as ticker_file:
        tickers = ticker_file.read().split('\n')
    start_date = np.datetime64(start_date)
    tickers_data = yf.download(tickers,start=start_date, end=start_date + np.timedelta64(7, 'D'))
    print(tickers_data)
    new_tickers = [ticker for ticker in tickers if not tickers_data['Adj Close'][ticker].isnull().all()]

    with open(f'../data/{ticker_type}_tickers_date_filtered.txt', 'w', encoding='UTF-8') as txt_date_filtered:
        txt_date_filtered.write("\n".join(map(str, new_tickers)))

    return new_tickers


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

    with open(f'../data/{ticker_type}_tickers_volume_filtered.txt', 'w', encoding='UTF-8') as txt_volume_filtered:
        txt_volume_filtered.write("\n".join(map(str, new_tickers)))

    return new_tickers
