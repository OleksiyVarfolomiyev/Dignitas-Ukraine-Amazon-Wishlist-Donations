import streamlit as st; st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .reportview-container {
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

df = etl.read_data()
df.Cost = df.Cost.astype(int)
start_date = df['Date'].min()
end_date = df['Date'].max()
df = etl.extract_relevant_txs(df, start_date, end_date)

# metrics
days = (dt.date.today() - start_date.date()).days

df['Total Cost'] = df['Quantity'] * df['Cost']
value_counts = df['Name'].value_counts()
multiple_donors = pd.DataFrame(value_counts[value_counts > 1])
multiple_donors.to_excel('data/multiple_donors.xlsx', index=False)

max_date_row = df[df['Date'] == df['Date'].max()]
donations_today = etl.format_money(max_date_row['Total Cost'].iloc[0])
max_date_names = max_date_row['Name'].unique()
returning_donors_max_date = len(set(max_date_names).intersection(multiple_donors))

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Days", days, "1", delta_color="normal")
col2.metric("Donations", etl.format_money(df['Total Cost'].sum()) , donations_today, delta_color="normal")
col3.metric("Donations Count", df['Total Cost'].count(), int(max_date_row['Date'].count()), delta_color="normal")
col4.metric("Products Donated", df['Quantity'].sum(), int(max_date_row['Quantity'].sum()), delta_color="normal")
col5.metric("Returning Donors", len(multiple_donors), returning_donors_max_date, delta_color="normal")

# Stack bar plot of Donations by Category by Period

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    selected_period = st.selectbox(' ', ['Monthly Donations', 'Weekly Donations', 'Daily Donations'])

donations_by_category = df.groupby(['Date', 'Product'])['Total Cost'].sum().reset_index()
fig = charting_tools.chart_by_period(donations_by_category, donations_by_category.Product.unique(), selected_period[0], '')
st.plotly_chart(fig, use_container_width=True)

# Ring plots of Donations by Category

donations_by_cat_Cost = pd.DataFrame(df.groupby('Product')['Total Cost'].sum().sort_values(ascending=False))
donations_by_cat_Quantity = pd.DataFrame(df.groupby('Product')['Quantity'].sum())
donations_by_cat = donations_by_cat_Cost.merge(donations_by_cat_Quantity, on='Product')

fig1 = charting_tools.pie_plot(donations_by_cat_Quantity.sort_values(by='Quantity', ascending=False).head(5), 'Quantity', 'Donations by Main Products (Count)', False)
fig2 = charting_tools.pie_plot(donations_by_cat_Cost.head(5), 'Total Cost', 'Donations by Main Cost Categories', False)
fig = charting_tools.subplot_horizontal(fig1, fig2, 1, 2, 'domain', 'domain', 'Donations by Main Products (Count)', 'Donations by Main Products (Cost)', False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("Visit [Dignitas Ukraine](https://dignitas.fund/)")

