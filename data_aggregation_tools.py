import pandas as pd
import datetime as dt

def sum_acc_by_date(account_name, period, data, category):
    return pd.DataFrame(data[((
            data[category] == account_name))]['Cost'].groupby(
            data['Date'].dt.to_period(period)).sum().reset_index(name = account_name))

def sum_by_period_by_account_name(account_names, period, data, category):
    data_frames = []
    for account_name in account_names:
        data_frames.append(
            sum_acc_by_date(account_name, period, data, category)
            )    
    from functools import reduce
    return reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), data_frames)

def sum_by_period(data, col, period):
    return pd.DataFrame(data[col].groupby(data['Date'].dt.to_period(period)).sum())