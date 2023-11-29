import pandas as pd

def format_money(value):
    '''Format money'''
    return '${:,.0f}'.format(float(value))

def etl(start_date, end_date, nrows = None):
    '''Read data from csv file'''
    import streamlit as st
    from streamlit_gsheets import GSheetsConnection
    import datetime as dt

    conn = st.connection("gsheets", type=GSheetsConnection)

    dtypes = {'Name' : 'str', 'Product': 'str', 'Total Cost' : 'str'}
    df = conn.read(
        worksheet="Data",
        ttl="10m",
        usecols=['Date', 'Name', 'Product', 'Quantity', 'Total Cost'],
                dtype=dtypes, parse_dates=['Date']
        )

    df = df.dropna(subset=['Total Cost'])
    df = df[(df['Total Cost'] != 0) & (df['Quantity'] > 0) ]
    df['Name'] = df['Name'].str.capitalize()
    if (start_date != None) | (end_date != None):
        df = df[df['Date'] >= start_date]
        df = df[df['Date'] <= end_date]

    # Anonymize data
    df['ID'] = pd.factorize(df['Name'])[0]
    # Extract first name
    df['Name'] = df['Name'].str.split().str[0]

    df['Total Cost'] = df['Total Cost'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['Date'] = df['Date'].dt.date

    df_grouped = df.groupby(['Date', 'ID', 'Product'])[['Quantity', 'Total Cost']].sum().reset_index()
    df = df_grouped.merge(df[['ID', 'Name']].drop_duplicates(), on=['ID'], how='left')

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
