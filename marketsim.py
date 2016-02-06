"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import os
import csv
from datetime import datetime as dt
import datetime

from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data

def compute_portvals(start_date, end_date, orders_file, start_val):
    """Compute daily portfolio value given a sequence of orders in a CSV file.

    Parameters
    ----------
        start_date: first date to track
        end_date: last date to track
        orders_file: CSV file to read orders from
        start_val: total starting cash available

    Returns
    -------
        portvals: portfolio value for each trading day from start_date to end_date (inclusive)
    """
    # TODO: Your code here
    read = csv.reader(open(orders_file,'rU'))
    dates = []
    symbols = []
    i=True
    stored_orders = []

    for oneLine in read:
        if i:
            i=False
            continue
        dates.append(oneLine[0])
        symbols.append(oneLine[1])
        stored_orders.append(oneLine)

    dates = list(set(dates))
    symbols = list(set(symbols))

    '''
    initial_end_date = end_date
    end_date = dt.strptime(end_date,'%Y-%m-%d')
    print type(end_date)

    end_date = end_date + datetime.timedelta(days=1)
    end_date = end_date.date()
    print type(end_date)
    print end_date

    end_date = dt.strftime(end_date,'%Y-%m-%d')
    '''

    index_dates = pd.date_range(start_date, end_date)

    df_prices = get_data(symbols,index_dates, False)

    #Made if full-proof by dropping a row only if it has all NaNs (so trading did not happen). If a few values are NaN, then set them to 0 to guarantee proper calculations ahead.
    for index, oneRow in df_prices.iterrows():
        count_nan = 0
        k = 0
        for oneVal in oneRow:
            if np.isnan(oneVal):
                oneRow[k]=0
                k+=1
                count_nan = count_nan+1

        if count_nan == len(symbols):
            df_prices = df_prices.drop([index])


    df_trade = pd.DataFrame(0.0, index=df_prices.index, columns=symbols)


    for oneOrder in stored_orders:
        if oneOrder[0] in df_trade.index:
            if oneOrder[2] == 'BUY':
                df_trade[oneOrder[1]][oneOrder[0]] += float(oneOrder[3])
            else:
                df_trade[oneOrder[1]][oneOrder[0]] += float(oneOrder[3]) * (-1)

    print "Final Trade Frame:"
    print df_trade

    df_prices["Cash"] = 1.0

    df_holdings = pd.DataFrame(0.0,index=df_prices.index,columns=symbols)
    df_holdings["Cash"] = 0.0

    df_holdings['Cash'][start_date] = float(start_val)

    i = 0
    j = 0
    for index, oneRow in df_trade.iterrows():

        j = 0
        sum_change = 0.0
        for shareCount in oneRow:
            if i == 0:
                df_holdings.iloc[i,j] = 0 + float(shareCount)
            else:
                df_holdings.iloc[i,j] = float(df_holdings.iloc[i-1,j]) + (shareCount)

            sum_change = sum_change + float(shareCount * (df_prices.iloc[i,j]))
            j = j+1
            if i==0:
                df_holdings["Cash"][index] = float(start_val) - sum_change
            else:
                df_holdings["Cash"][index] = df_holdings.iloc[i-1,len(symbols)] - sum_change
        i = i+1

    print "Holdings DataFrame:"
    print df_holdings

    df_values = df_holdings * df_prices

    port_vals = df_values.sum(axis=1)

    print "The final portfolio values are:"
    print port_vals

    return port_vals


def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2011-01-05'
    end_date = '2011-01-20'
    orders_file = os.path.join("", "orders_ML4T-399_train.csv")
    start_val = 1000000

    #TestCase-2 Passing perfectly
    #start_date = '2011-01-10'
    #end_date = '2011-12-20'
    #orders_file = os.path.join("orders", "orders.csv")
    #start_val = 1000000

    #TestCase-3 Passing perfectly
    #start_date = '2011-01-14'
    #end_date = '2011-12-14'
    #orders_file = os.path.join("orders", "orders2.csv")
    #start_val = 1000000

    # Process orders
    portvals = compute_portvals(start_date, end_date, orders_file, start_val)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # if a DataFrame is returned select the first column to get a Series
    
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
    df_temp = pd.concat([portvals, prices_SPX['$SPX']], keys=['Portfolio', '$SPX'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value and $SPX")


if __name__ == "__main__":
    test_run()
