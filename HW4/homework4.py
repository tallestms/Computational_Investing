import pandas as pd
import pandas.io.parsers as pd_par
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

eventAmount = 5.0
symbolList = 'sp5002012'
orderFile = 'orderEventFile.csv'

def find_events(ls_symbols, d_data, ldt_timestamps, eventAmount):
    df_close = d_data['actual_close']
    
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NaN
    
    for symbols in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            f_symprice_today = df_close[symbols].ix[ldt_timestamps[i]]
            f_symprice_yesterday = df_close[symbols].ix[ldt_timestamps[i-1]]
            
            if(f_symprice_today >= eventAmount and f_symprice_yesterday < eventAmount):
                df_events[symbols].ix[ldt_timestamps[i]] = 1
                
    return df_events

def create_events_orders(ldt_timestamps):
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(symbolList)
    ls_symbols.append('SPY')

    ls_keys = ['actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
        
    define_events = find_events(ls_symbols, d_data, ldt_timestamps, eventAmount)
    
    file_out = open(orderFile, 'w')
    for symbols in define_events.columns:
        for i in range(0, len(ldt_timestamps)):
            actualDate = ldt_timestamps[i]
            if not np.isnan(define_events[symbols].ix[actualDate]):
                if i+5 >= len(ldt_timestamps):
                    finalDate = ldt_timestamps[len(ldt_timestamps) - 1]
                else:
                    finalDate = ldt_timestamps[i+5]
                file_out.writelines(actualDate.strftime('%Y,%m,%d') + "," + symbols + ",Buy,100\n")
                file_out.writelines(finalDate.strftime('%Y,%m,%d') + "," + symbols + ",Sell,100\n")                
    file_out.close()        

if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    create_events_orders(ldt_timestamps)