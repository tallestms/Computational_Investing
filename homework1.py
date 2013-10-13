import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

dt_start = dt.datetime(2011, 1, 1)
dt_end = dt.datetime(2011, 12, 31)
ls_symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT'] 

def simulate(startDate, endDate, symbolsEq, allocationEq) :
    
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]

    symbolSP = ["$SPX"]
    sp_data = c_dataobj.get_data(ldt_timestamps, symbolSP, ls_keys)
    sp_d_data = dict(zip(ls_keys, sp_data))
    sp_price = sp_d_data['close'].values
    sp_price_normalized = sp_price / sp_price[0, :]
    dailyReturnSP = sp_price_normalized.copy()
    tsu.returnize0(dailyReturnSP)
    
    na_normalizedPriceAllocation = na_normalized_price*allocationEq
    na_sumRows = na_normalizedPriceAllocation.sum(axis=1)
    na_sumRows.shape = (na_sumRows.size(),1)
    dailyReturn = na_sumRows.copy()
    tsu.returnize0(dailyReturn)
    avgDailyReturn = np.average(dailyReturn)    
    dailyReturnStdDev = np.std(dailyReturn)

    sharpeRatio = np.sqrt(252)*avgDailyReturn/dailyReturnStdDev
    excessReturn = dailyReturn - dailyReturnSP
    
    avgExcessReturn = np.average(excessReturn)
    excessReturnStdDev = np.std(excessReturn)
    cumulativeReturn = na_sumRows[-1]

    return dailyReturnStdDev, avgDailyReturn, sharpeRatio, cumulativeReturn  

optimalSharpeRatio = 0.0
optimalAllocation = [0, 0, 0, 0]
for a in range (0, 10):
    for b in range (0, 10):
        for c in range (0, 10):
            for d in range (0, 10):
                if(a + b + c + d == 10):
                    allocation = [float(a)/10, float(b)/10, float(c)/10, float(d)/10]
                    volatility, dailyReturn, sharpeRatio, cumulativeReturn = simulate(dt_start, dt_end, ls_symbols, allocation) 
                    if(sharpeRatio > optimalSharpeRatio):
                        optimalSharpeRatio = sharpeRatio
                        optimalAllocation = allocation


