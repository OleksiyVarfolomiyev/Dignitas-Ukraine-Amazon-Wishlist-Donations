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
@st.cache_data
def etl_data():
    """ETL data"""
    start_date = None
    end_date =  None
    df = etl.etl(start_date, end_date)

    donations_by_category = df.groupby(['Date', 'Product'])['Total Cost'].sum().reset_index()
    donations_by_category_quantity = df.groupby(['Date', 'Product'])['Quantity'].sum().reset_index()
    return df, donations_by_category, donations_by_category_quantity, start_date, end_date

df, donations_by_category, donations_by_category_quantity, start_date, end_date = etl_data()

def show_metrics(df, start_date):
    """ Show metrics"""
    if start_date == None:
        start_date = df['Date'].min()

    days = (dt.date.today() - start_date).days
    donors = df['ID'].nunique()

    # donations today
    max_date = df['Date'].max()
    donated_today = etl.format_money(df[df.Date == max_date]['Total Cost'].sum())
    # new donors today
    max_date_names = pd.DataFrame({'ID' : df[df.Date == max_date]['ID'].unique()})
    before_max_date_names = pd.DataFrame({'ID': df[df['Date'] < max_date]['ID'].unique()})
    new_donors_today = len(max_date_names.merge(before_max_date_names, on='ID', how='left', indicator=True))
    # new multiple donors
    name_count = df['ID'].value_counts()
    multiple_donors = pd.DataFrame(name_count[name_count > 1])
    name_count_before_today = df[df['Date'] < max_date]['ID'].value_counts()
    multiple_donors_before_today = pd.DataFrame(name_count_before_today[name_count_before_today > 1])
    new_multiple_donors = len(multiple_donors) - len(multiple_donors_before_today)

    if new_multiple_donors == 0:
        new_multiple_donors = ''
    if new_donors_today == 0:
        new_donors_today = ''

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Days", days, "1", delta_color="normal")
    col2.metric("Donations Value", etl.format_money(df['Total Cost'].sum()) , donated_today, delta_color="normal")
    col3.metric("Products Donated", int(df.Quantity.sum()), int(df[df.Date == max_date]['Quantity'].sum()), delta_color="normal")
    col4.metric("Donors", donors, new_donors_today, delta_color="normal")
    col5.metric("Donated multiple products", len(multiple_donors), new_multiple_donors, delta_color="normal")

show_metrics(df, start_date)

def show_donations_by_period(df, donations_by_category):
    """Stack bar plot of Donations by Category by Period"""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col5:
        timespan = st.selectbox(' ',['Since launch', '1 Year ', '1 Month ', '3 Months ', '6 Months '])
    with col1:
        selected_period = st.selectbox(' ', ['Monthly', 'Weekly', 'Daily', 'Yearly'])

    if timespan == '1 Month ':
        donations_by_category = donations_by_category[donations_by_category['Date'] > pd.Timestamp.now().floor('D') - pd.DateOffset(months=1)]
    elif timespan == '3 Months ':
        donations_by_category = donations_by_category[donations_by_category['Date'] > pd.Timestamp.now().floor('D') - pd.DateOffset(months=3)]
    elif timespan == '6 Months ':
        donations_by_category = donations_by_category[donations_by_category['Date'] > pd.Timestamp.now().floor('D') - pd.DateOffset(months=6)]
    elif timespan == '1 Year ':
        donations_by_category = donations_by_category[donations_by_category['Date'] > pd.Timestamp.now().floor('D') - pd.DateOffset(years=1)]
    else:
        donations_by_category = donations_by_category
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
# Donations list
df['Total Cost'] = '$' + df['Total Cost'].astype(str)
df.set_index('Date', inplace=True)
st.dataframe(df[[ 'Name', 'Product', 'Quantity', 'Total Cost']].sort_values(by= 'Date', ascending=False), use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Donate button
import webbrowser
url_to_open = "https://www.dignitas.fund/amazon"
col1, col2, col3 = st.columns(3)

import streamlit.components.v1 as components

# def ChangeButtonColour(wgt_txt, wch_hex_colour = '12px'):
#     htmlstr = """<script>var elements = window.parent.document.querySelectorAll('*'), i;
#                 for (i = 0; i < elements.length; ++i)
#                     { if (elements[i].innerText == |wgt_txt|)
#                         { elements[i].style.color ='""" + wch_hex_colour + """'; } }</script>  """

#     htmlstr = htmlstr.replace('|wgt_txt|', "'" + wgt_txt + "'")
#     components.html(f"{htmlstr}", height=0, width=0)

# # Create the "Donate" button
if col2.button("Donate", key="donate_button", help="Click to donate"):
     webbrowser.open_new_tab(url_to_open)
# Change the button colour to green
#ChangeButtonColour('Donate', '#4E9F3D')

# Links
st.write("---")
col1, col2, col3 = st.columns(3)
with col1: st.markdown("[Dignitas Ukraine Site](https://dignitas.fund/)")
with col2: st.markdown("[Dignitas Ukraine Financials](https://dignitas-ukraine.streamlit.app/)")
with col3: st.markdown(f"[{'Contact'}](mailto:{'info@dignitas.fund'})")