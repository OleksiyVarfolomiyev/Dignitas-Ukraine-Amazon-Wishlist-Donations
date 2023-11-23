import pandas as pd

def sum_category_by_date(category_value, period, data, category):
    import datetime as dt
    data['Date'] = pd.to_datetime(data['Date'])
    filtered_data = data[data[category] == category_value]
    filtered_data['Date'] = pd.to_datetime(filtered_data['Date']).dt.to_period(period)
    return filtered_data.groupby('Date')['Total Cost'].sum().reset_index(name=category_value)

def sum_by_period_by_category(categories_list, period, data, category):
    data_frames = []
    for category_value in categories_list:
        data_frames.append(sum_category_by_date(category_value, period, data, category))

    from functools import reduce
    return reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), data_frames)

def sum_by_period(data, col, period):
    return pd.DataFrame(data[col].groupby(data['Date'].dt.to_period(period)).sum())