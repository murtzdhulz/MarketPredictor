__author__ = 'Murtaza'
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from util import get_data
from analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data
from marketsim import compute_portvals
import csv

#Returns the Bollinger Bands and the SMA
def get_bands(df,window):
    sma_band = pd.rolling_mean(df,window=window)
    rolling_std = pd.rolling_std(df,window=window)
    upper_band = sma_band + 2*rolling_std
    lower_band = sma_band - 2*rolling_std

    return sma_band, upper_band, lower_band

def write_orders(df, transition_array_upper, transition_array_sma, transition_array_lower, orders_file):
    short = False
    long = False

    with open(orders_file,'wb') as my_file:
        csv_wrie_order = csv.writer(my_file)

        csv_wrie_order.writerow(['Date','Symbol','Order','Shares'])

        for i in range(20,len(transition_array_upper)):
            date = str(df.ix[i].name.year)+"-"+str(df.ix[i].name.month)+"-"+str(df.ix[i].name.day)

            #Generate the entries in the Order file one by one by traversing the transition arrays
            if transition_array_upper[i] == -1 and not(short):
                short = True
                print 'Sell-Short Entry',date
                write_list = [date,"IBM","SELL","100"]
                csv_wrie_order.writerow(write_list)
                plt.axvline(x=df.ix[i].name,color='R')
            if transition_array_sma[i] == -2 and short:
                short = False
                print 'Buy here-Short Exit',date
                write_list = [date,"IBM","BUY","100"]
                csv_wrie_order.writerow(write_list)
                plt.axvline(x=df.ix[i].name,color='K')
            if transition_array_lower[i] == 3 and not(long):
                long = True
                print 'Buy here-Long entry',date
                write_list = [date,"IBM","BUY","100"]
                csv_wrie_order.writerow(write_list)
                plt.axvline(x=df.ix[i].name,color='G')
            if transition_array_sma[i] == 2 and long:
                long= False
                print 'Sell here-Long exit',date
                write_list = [date,"IBM","SELL","100"]
                csv_wrie_order.writerow(write_list)
                plt.axvline(x=df.ix[i].name,color='K')

    return


def test_run():

    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    orders_file = os.path.join("orders", "current_order.csv")
    dates = pd.date_range(start_date, end_date)
    symbols = ['IBM']
    df = get_data(symbols, dates, True)

    window_size = 20

    sma_band, upper_band, lower_band = get_bands(df['IBM'],window=window_size)

    #+1 going out, -1 coming in
    transition_array_upper = np.pad(np.diff(np.array(df['IBM'] > upper_band).astype(int)),
                    (1,0), 'constant', constant_values = (0,))

    #+2 stock price going up,-2 stock price going down
    transition_array_sma = np.pad(np.diff(np.array(df['IBM'] > sma_band).astype(int)*2),
                    (1,0), 'constant', constant_values = (0,))

    #+3 stock price going up from lower_band,-3 stock price going down from lower_band
    transition_array_lower = np.pad(np.diff(np.array(df['IBM'] > lower_band).astype(int)*3),
                    (1,0), 'constant', constant_values = (0,))

    write_orders(df,transition_array_upper,transition_array_sma,transition_array_lower, orders_file)

    ax = df['IBM'].plot(title="Bollinger Bands", label='IBM')
    sma_band.plot(label='SMA', ax=ax, color = 'Goldenrod')
    upper_band.plot(label='Upper Bollinger Band', ax=ax, color = 'Turquoise')
    lower_band.plot(label='Lower Bollinger Band', ax=ax, color = 'Turquoise')
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()

    portvals = compute_portvals(start_date, end_date, orders_file, 10000)

    # Get portfolio stats
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(portvals)

    # Simulate a $SPX-only reference portfolio to get stats
    prices_SPX = get_data(['$SPX'], pd.date_range(start_date, end_date))
    prices_SPX = prices_SPX[['$SPX']]  # remove SPY
    portvals_SPX = get_portfolio_value(prices_SPX, [1.0])
    cum_ret_SPX, avg_daily_ret_SPX, std_daily_ret_SPX, sharpe_ratio_SPX = get_portfolio_stats(portvals_SPX)

    # Compare portfolio against $SPX
    print "Data Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of $SPX: {}".format(sharpe_ratio_SPX)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of $SPX: {}".format(cum_ret_SPX)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of $SPX: {}".format(std_daily_ret_SPX)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of $SPX: {}".format(avg_daily_ret_SPX)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

    # Plot computed daily portfolio value
    df_temp = pd.concat([portvals, prices_SPX['$SPX']], keys=['Portfolio', 'SPY'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value")

if __name__ == "__main__":
    test_run()
