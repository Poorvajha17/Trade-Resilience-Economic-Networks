import streamlit as st
import pandas as pd
from utils.io_helpers import path_in_data, load_csv_safe
from utils.visuals import trade_network

st.title("🕸️ Trade Networks")

df = load_csv_safe(path_in_data("final_with_indexes.csv"))
if df is None: st.stop()

iso3 = st.selectbox("Country", sorted(df["ISO3"].unique()))
year = st.selectbox(
    "Year",
    sorted(df["Year"].dropna().unique())
)
fig = trade_network(df, iso3, year)
if fig is not None:
    st.pyplot(fig)
else:
    st.warning("No trade data available for this selection.")
