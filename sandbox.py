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
    'Donations Value': [ etl.format_money(df['Total Cost'].sum()) ],
    'Donations Count': [ df['Total Cost'].count() ],
    'Multiple Donors': [ len(multiple_donors) ],
    'Products Donated': [ df['Quantity'].sum() ],
    'Days' : [ days ]
}))

donations_by_cat_Cost = pd.DataFrame(df.groupby('Product')['Total Cost'].sum().sort_values(ascending=False))
st.dataframe(donations_by_cat_Cost)