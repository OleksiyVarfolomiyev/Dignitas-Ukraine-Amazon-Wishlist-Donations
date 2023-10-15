import pandas as pd

def format_money(value):
    return '${:,.0f}'.format(float(value))

def read_data(nrows = None):
    dtypes = {'Name' : 'str', 'Product': 'str', 'Quantity' : 'int', 'Cost' : 'str'}
    df = pd.read_csv('data/Amazon Wishlist - In-Kind Gift - Data.csv', 
                     usecols=['Date', 'Product', 'Quantity', 'Cost', 'Name'],
                     dtype=dtypes, parse_dates=['Date'])
    df.Cost = df['Cost'].str.strip('$').astype(float)
    return df

def extract_relevant_txs(df, start_date, end_date):
    """Main category mapping module"""
    if (start_date != None) | (end_date != None):
        df = df[df['Date'].dt.date >= start_date.date()]
        df = df[df['Date'].dt.date <= end_date.date()]

    values_to_check = ['Lifestraw', 'Water Tables']
    condition = df['Product'].str.contains('|'.join(values_to_check), case=False)
    df.loc[condition, 'Product'] = 'Water Purification'
    return df

def extract_top_donors(df):
    """Extract top donors"""
    top_donors = pd.DataFrame(df.groupby('Name')[['Total Cost', 'Quantity', ]].sum().sort_values(by='Total Cost', ascending=False).head(5))
    top_donors['Quantity'] = top_donors['Quantity'].astype(int)
    top_donors['Total Cost'] = top_donors['Total Cost'].map(format_money)
    return top_donors
    