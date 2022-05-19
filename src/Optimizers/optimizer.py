import itertools

from sklearn.model_selection import train_test_split
from src.Optimizers.optimizer_utils import print_correlation_heatmap, print_efficient_frontiers_graph, load_mst_data, optimize_variance, optimize_semivariance

import src.constants as c

if __name__ == '__main__':

    for date in c.START_DATES:
        for mst_type, mst_mode in itertools.product(c.MST_TYPES, c.MST_MODES):
            mst_mode_print = mst_mode or 'No SR filter'
            title = f"{date} {mst_type} {mst_mode_print}"
            print(f'\n {title} \n')
            returns = load_mst_data(date, mst_type, mst_mode)
            train, test = train_test_split(returns, test_size=0.5, train_size=0.5, shuffle=False)
            # print_efficient_frontiers_graph(train, title)
            # print_correlation_heatmap(train, title)
            # optimize_variance(returns=returns, train=train, test=test, max_return = 0.1, min_risk = 0.1, l2_reg=False)
            # optimize_semivariance()