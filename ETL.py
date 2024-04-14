import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime as dt

def format_money(value):
    '''Format money'''
    return '${:,.0f}'.format(float(value))

def read(start_date, end_date, nrows = None):
    '''Read data from gsheet and transform it'''

    conn = st.connection("gsheets", type=GSheetsConnection)

    dtypes = {'Name' : 'str', 'Product': 'str', 'Quantity': 'float', 'Total Cost' : 'str'}

    # Read data from the 2023 worksheet
    df_2023 = conn.read(worksheet="2023", ttl="10m",
        usecols=['Date', 'Name', 'Product', 'Quantity', 'Total Cost'],
        dtype = dtypes
    )
    df_2023['Date'] = pd.to_datetime(df_2023['Date'], format='%b %d, %Y')
    # Read data from the 2024 worksheet
    df_2024 = conn.read(worksheet="2024", ttl="10m",
        usecols=['Date', 'Name', 'Product', 'Quantity', 'Total Cost'],
        dtype = dtypes
    )
    df_2024['Date'] = pd.to_datetime(df_2024['Date'], format='%b %d, %Y')

    # Append the 2024 DataFrame to the 2023 DataFrame
    #df = df_2023.append(df_2024, ignore_index=True)
    df = pd.concat([df_2023, df_2024], ignore_index=True)

    # Drop incomplete rows
    df = df.dropna(subset = ['Total Cost'])
    df = df[(df['Total Cost'] != 0) & (df['Quantity'] > 0) ]

    df['Name'] = df['Name'].str.capitalize()

    if (start_date != None) | (end_date != None):
        df = df[df['Date'] >= start_date]
        df = df[df['Date'] <= end_date]

    # Anonymize data
    df['ID'] = pd.factorize(df['Name'])[0]
    # Extract first name
    df['Name'] = df['Name'].str.split().str[0]
    # transform Total Cost to float and Date to date type
    df['Total Cost'] = df['Total Cost'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['Date'] = df['Date'].dt.date
    # group donation by date, donator ID and product
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
