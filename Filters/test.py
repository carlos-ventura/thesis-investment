from cmc import coinmarketcap
from datetime import datetime

cryptos = ['bitcoin', 'ripple', 'ethereum']
start_date, end_date = datetime(2017, 6, 1), datetime(2018, 6, 1)

df_bitcoin = coinmarketcap.getDataFor(cryptos, start_date, end_date, fields=['High', 'Low', 'Close'])
print(df_bitcoin)
