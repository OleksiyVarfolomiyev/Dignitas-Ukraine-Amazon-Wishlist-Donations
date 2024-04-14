import pandas as pd
import datetime as dt

# def sum_category_by_date(category_value, period, data, category):
#     return pd.DataFrame(data[((
#             data[category] == category_value))]['Total Cost'].groupby(
#             data['Date'].dt.to_period(period)).sum().reset_index(name = category_value))


# def sum_by_period_by_category(categories_list, period, data, category):
#     data_frames = []
#     for category_value in categories_list:
#         data_frames.append(sum_category_by_date(category_value, period, data, category))

#     from functools import reduce
#     return reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), data_frames)

# def sum_by_period(data, col, period):
#     return pd.DataFrame(data[col].groupby(data['Date'].dt.to_period(period)).sum())

def sum_category_by_date(category_value, period, data, category):
    data['Date'] = pd.to_datetime(data['Date'])
    return pd.DataFrame(data[((
            data[category] == category_value))]['Total Cost'].groupby(
            data['Date'].dt.to_period(period)).sum().reset_index(name = category_value))

def sum_by_period_by_category(categories_list, period, data, category):
    data['Date'] = pd.to_datetime(data['Date'])
    data_frames = []
    for category_value in categories_list:
        data_frames.append(sum_category_by_date(category_value, period, data, category))

    from functools import reduce
    return reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), data_frames)

def sum_by_period(data, col, period):
    data['Date'] = pd.to_datetime(data['Date'])
    return pd.DataFrame(data[col].groupby(data['Date'].dt.to_period(period)).sum())