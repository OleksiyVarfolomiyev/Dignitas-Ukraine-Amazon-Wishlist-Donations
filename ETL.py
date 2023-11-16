import pandas as pd

def format_money(value):
    '''Format money'''
    return '${:,.0f}'.format(float(value))

def read_data(nrows = None):
    '''Read data from csv file'''
    # dtypes = {'Name' : 'str', 'Product': 'str', 'Quantity' : 'int', 'Total Cost' : 'str'}
    # df = pd.read_csv('data/Amazon Wishlist - In-Kind Gift - Data.csv',
    #                  usecols=['Date', 'Product', 'Quantity', 'Total Cost', 'Name'],
    #                  dtype=dtypes, parse_dates=['Date'])
    import streamlit as st
    from streamlit_gsheets import GSheetsConnection

    # Create a connection object.
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    dtypes = {'Name' : 'str', 'Product': 'str', 'Total Cost' : 'str'}
    df = conn.read(
        worksheet="Data",
        ttl="10m",
        usecols=['Date', 'Product', 'Quantity', 'Total Cost', 'Name'],
                dtype=dtypes, parse_dates=['Date']
    )
    df = df.dropna(subset=['Total Cost'])
    df['Total Cost'] = df['Total Cost'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    return df

def extract_relevant_txs(df, start_date, end_date):
    """Main category mapping module"""
    if (start_date != None) | (end_date != None):
        df = df[df['Date'].dt.date >= start_date.date()]
        df = df[df['Date'].dt.date <= end_date.date()]
    # group Water Purification products
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
