from src.Filters.utils_filters import mst_filter
import src.constants as c

if __name__ == '__main__':
    for date in c.START_DATES:
        target_name=date.split('-', maxsplit=1)[0]
        _ = mst_filter('', start_date=date, end_date=c.END_DATE, target_name=target_name, ticker_type='etfs-benchmark', min_sr=False, benchmark=True)