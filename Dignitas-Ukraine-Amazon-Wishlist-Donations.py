import streamlit as st; st.set_page_config(layout="wide")

import ETL as etl
import data_aggregation_tools as da
import charting_tools
import pandas as pd
import datetime as dt

import plotly.express as px
from plotly.offline import iplot
import plotly.figure_factory as ff
import plotly.io as pio
from plotly.subplots import make_subplots

st.title("Dignitas Ukraine **Amazon Wishlist Donations**")
def etl_data():
    df = etl.read_data()
    #Anonymize data
    df['Name'] = pd.factorize(df['Name'])[0]
    #df.to_csv('data/Amazon Wishlist - In-Kind Gift - Data.csv', index=False)

    start_date = df['Date'].min()
    #start_date = pd.to_datetime('2023-10-01')
    end_date = df['Date'].max()
    df = etl.extract_relevant_txs(df, start_date, end_date)

    donations_by_category = df.groupby(['Date', 'Product'])['Total Cost'].sum().reset_index()
    donations_by_category_quantity = df.groupby(['Date', 'Product'])['Quantity'].sum().reset_index()
    return df, donations_by_category, donations_by_category_quantity, start_date, end_date

# first run anonymizes the data
df, donations_by_category, donations_by_category_quantity, start_date, end_date = etl_data()

def show_metrics(df, start_date):
    """ Show metrics"""
    days = (dt.date.today() - start_date.date()).days
    donors = df['Name'].nunique()
    # multiple donors
    name_count = df['Name'].value_counts()
    multiple_donors = pd.DataFrame(name_count[name_count > 1])
    # donations today
    max_date = df[df['Date'] == df['Date'].max()]
    donors_today = max_date['Name'].nunique()
    donated_today = etl.format_money(max_date['Total Cost'].sum())
    # new donors today
    max_date_names = pd.DataFrame({'Name' : max_date['Name'].unique()})
    before_max_date_names = pd.DataFrame({'Name': df[df['Date'] < df['Date'].max()]['Name'].unique()})
    merged_df = max_date_names.merge(before_max_date_names, on='Name', how='left', indicator=True)
    new_donors_today = len( merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge') )
    # new multiple donors
    name_count = df[df['Date'] < df['Date'].max()]['Name'].value_counts()
    multiple_donors_before_today = pd.DataFrame(name_count[name_count > 1])
    new_multiple_donors = len(multiple_donors) - len(multiple_donors_before_today)

    if new_multiple_donors == 0:
        new_multiple_donors = ''
    if new_donors_today == 0:
        new_donors_today = ''

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Days", days, "1", delta_color="normal")
    col2.metric("Donations", etl.format_money(df['Total Cost'].sum()) , donated_today, delta_color="normal")
    col3.metric("Products Donated", len(df), len(max_date), delta_color="normal")
    col4.metric("Donors", donors, new_donors_today, delta_color="normal")
    col5.metric("Donated multiple products", len(multiple_donors), new_multiple_donors, delta_color="normal")

show_metrics(df, start_date)

def show_donations_by_period(df, donations_by_category):
    """Stack bar plot of Donations by Category by Period"""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        selected_period = st.selectbox(' ', ['Monthly', 'Weekly', 'Daily', 'Yearly'])
    fig = charting_tools.chart_by_period(donations_by_category, donations_by_category.Product.unique(), selected_period[0], '')
    st.plotly_chart(fig, use_container_width=True)

show_donations_by_period(df, donations_by_category)

def show_donations_by_category(donations_by_category, donations_by_category_quantity):
    """ Show donations by category"""
    col0, col1, col2, col3, col4 = st.columns(5)
    with col2:
            period = st.selectbox(' ', ['Month', 'Week', 'Day', 'Year'])

    if period == 'Month':
        donations = donations_by_category[donations_by_category['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(months=1)]
        donations_quantity = donations_by_category_quantity[donations_by_category_quantity['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(months=1)]

    elif period == 'Week':
        donations = donations_by_category[donations_by_category['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(weeks=1)]
        donations_quantity = donations_by_category_quantity[donations_by_category_quantity['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(weeks=1)]
    elif period == 'Day':
        day = donations_by_category['Date'].max()
        donations = donations_by_category[donations_by_category['Date'] == donations_by_category.Date.max()]
        donations_quantity = donations_by_category_quantity[donations_by_category_quantity['Date'] == donations_by_category_quantity.Date.max()]
    elif period == 'Year':
        donations = donations_by_category[donations_by_category['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(years=1)]
        donations_quantity = donations_by_category_quantity[donations_by_category_quantity['Date'] >= pd.Timestamp.now().floor('D') - pd.DateOffset(years=1)]
    else:
        donations = donations_by_category
        donations_quantity = donations_by_category_quantity

    donations_cost_by_cat_by_period = donations.groupby('Product')['Total Cost'].sum().reset_index()
    donations_quantity_by_cat_by_period = donations_quantity.groupby('Product')['Quantity'].sum().reset_index()

    fig1 = charting_tools.pie_plot(donations_quantity_by_cat_by_period,
                                   'Quantity', 'Product',
                                   'Donations (Count)', False)

    fig2 = charting_tools.pie_plot(donations_cost_by_cat_by_period,
                                   'Total Cost', 'Product',
                                   'Donations (Cost)', False)
    fig = charting_tools.subplot_horizontal(fig1, fig2, 1, 2, 'domain', 'domain', 'Donations (Count)', 'Donations (Cost)', False)
    st.plotly_chart(fig, use_container_width=True)

show_donations_by_category(donations_by_category, donations_by_category_quantity)

col0, col1, col2, col3 = st.columns(4)
with col1: st.markdown("[Dignitas Ukraine Site](https://dignitas.fund/)")
with col2: st.markdown("[Dignitas Ukraine Financials](https://dignitas-ukraine.streamlit.app/)")