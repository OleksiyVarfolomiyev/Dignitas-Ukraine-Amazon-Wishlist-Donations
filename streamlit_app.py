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

st.title("Dignitas Ukraine Amazon Wishlist Donations")

df = etl.read_data()
df.Cost = df.Cost.astype(int)
start_date = df['Date'].min()
end_date = df['Date'].max()
df = etl.extract_relevant_txs(df, start_date, end_date)

days = (dt.date.today() - start_date.date()).days

df['Total Cost'] = df['Quantity'] * df['Cost']
value_counts = df['Name'].value_counts()
multiple_donors = pd.DataFrame(value_counts[value_counts > 1])
multiple_donors.to_excel('data/multiple_donors.xlsx', index=False)

st.dataframe(pd.DataFrame({
    'Donors': [ df['Name'].nunique() ],
    'Multiple Donors': [ len(multiple_donors) ],
    'Donations Value': [ etl.format_money(df['Total Cost'].sum()) ],
    'Donations Count': [ df['Total Cost'].count() ],
    'Products Donated': [ df['Quantity'].sum() ],
    'Days' : [ days ]
}))

donations_by_cat_Cost = pd.DataFrame(df.groupby('Product')['Total Cost'].sum().sort_values(ascending=False))
donations_by_cat_Quantity = pd.DataFrame(df.groupby('Product')['Quantity'].sum())
donations_by_cat = donations_by_cat_Cost.merge(donations_by_cat_Quantity, on='Product')

fig1 = charting_tools.pie_plot(donations_by_cat_Quantity.sort_values(by='Quantity', ascending=False).head(5), 'Quantity', 'Donations by Main Products (Count)', False)
fig2 = charting_tools.pie_plot(donations_by_cat_Cost.head(5), 'Total Cost', 'Donations by Main Cost Categories', False)
fig = charting_tools.subplot_horizontal(fig1, fig2, 1, 2, 'domain', 'domain', 'Donations by Main Products (Count)', 'Donations by Main Products (Cost)', False)

st.plotly_chart(fig, use_container_width=True)

main_donation_categories = donations_by_cat_Quantity.sort_values(by='Quantity', ascending=False).head(5).index.tolist()

monthly_donations_by_category = da.sum_by_period_by_account_name(main_donation_categories, 'M', df, 'Product').fillna(0)
monthly_donations_by_category['Date'] = monthly_donations_by_category['Date'].astype(str).str.split('/').str[0]
fig1 = charting_tools.stack_bar_plot(monthly_donations_by_category, 'Monthly Donations by main products', False)

weekly_donations_by_category = da.sum_by_period_by_account_name(main_donation_categories, 'W', df, 'Product').fillna(0)
weekly_donations_by_category['Date'] = weekly_donations_by_category['Date'].astype(str).str.split('/').str[0]
fig2 = charting_tools.stack_bar_plot(weekly_donations_by_category, 'Weekly Donations by main products', False)

fig = charting_tools.subplot_vertical(pd.DataFrame(), fig1, fig2, 2, 1, 'xy', 'xy', 'stack', 'Monthly Donations by main products', 'Weekly Donations by main products', False)

st.plotly_chart(fig, use_container_width=True)

df['Date'] = pd.to_datetime(df['Date'])
donations_by_weekday = pd.DataFrame(df.groupby([df['Date'].dt.day_name()])['Quantity'].count().sort_values(ascending = False))

fig = px.bar(donations_by_weekday, x = donations_by_weekday.index, y = 'Quantity', 
            color = 'Quantity', color_continuous_scale = 'Bluered',
            text_auto = '.2s',
            title='Donations by day of week (count)')

st.plotly_chart(fig, use_container_width=True)

st.markdown("Visit [Dignitas Ukraine](https://dignitas.fund/)")

