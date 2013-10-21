import pandas as pd
import pandas.io.parsers as pd_par
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

startCash = 1000000
orderFile = "orders2.csv"
valueFile = "values2.csv"

if __name__ == '__main__':
    orderDF = pd_par.read_csv(orderFile, header=None)
    
    # Getting the Symbols from the .csv file
    ls_symbols = list(set(orderDF[3].values))
    
    # Need to sort the trades DF by increasing date
    orderDF = orderDF.sort([0, 1, 2])
    
    # Getting the start and end dates from the .csv file
    df_lastrow = len(orderDF) - 1
    dt_start = dt.datetime( orderDF.get_value(0, 0), orderDF.get_value(0, 1), orderDF.get_value(0, 2))
    dt_end = dt.datetime( orderDF.get_value(df_lastrow, 0), orderDF.get_value(df_lastrow, 1), orderDF.get_value(df_lastrow, 2) + 1 )
    
    
    # Getting market data
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['close', 'actual_close']
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Adding CASH to our symbols and creating our trades table
    ls_symbols.append("_CASH")
    trades_data = pd.DataFrame(index=list(ldt_timestamps), columns=list(ls_symbols))
    
    curr_cash = startCash
    trades_data["_CASH"][ldt_timestamps[0]] = startCash
    
    curr_stocks = dict()
    print curr_stocks
    for sym in ls_symbols:
            curr_stocks[sym] = 0
            trades_data[sym][ldt_timestamps[0]] = 0
    
    for row in orderDF.iterrows():
            row_data = row[1]
            curr_date = dt.datetime(row_data[0], row_data[1], row_data[2], 16 )
            sym = row_data[3]
            stock_value = d_data['close'][sym][curr_date]
            stock_amount = row_data[5]
    
            if row_data[4] == "Buy":
                    curr_cash = curr_cash - (stock_value * stock_amount)
                    trades_data["_CASH"][curr_date] = curr_cash
                    curr_stocks[sym] = curr_stocks[sym] + stock_amount
                    trades_data[sym][curr_date] = curr_stocks[sym]
            else:
                    curr_cash = curr_cash + (stock_value * stock_amount)
                    trades_data["_CASH"][curr_date] = curr_cash
                    curr_stocks[sym] = curr_stocks[sym] - stock_amount
                    trades_data[sym][curr_date] = curr_stocks[sym]
    
    trades_data = trades_data.fillna(method = "pad")
    
    value_data = pd.DataFrame(index=list(ldt_timestamps), columns=list("V"))
    value_data = value_data.fillna(0)
    
    for day in ldt_timestamps:
            value = 0
    
            for sym in ls_symbols:
                    if sym == "_CASH":
                            value = value + trades_data[sym][day]
                    else:
                            value = value + trades_data[sym][day] * d_data['close'][sym][day]
    
            value_data["V"][day] = value
    
    file_out = open( valueFile, "w" )
    for row in value_data.iterrows():
            file_out.writelines(str(row[0].strftime('%Y,%m,%d')) + ", " + str(row[1]["V"].round()) + "\n" )
    file_out.close()
    
