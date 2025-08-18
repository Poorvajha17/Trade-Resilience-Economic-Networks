import streamlit as st
import pandas as pd
from utils.io_helpers import path_in_data, load_csv_safe
from utils.visuals import shock_panels

st.title("🌪️ Shock Analysis")

df = load_csv_safe(path_in_data("final_with_indexes.csv"))
if df is None: st.stop()

iso3 = st.selectbox("Country", sorted(df["ISO3"].unique()))
fig = shock_panels(df, iso3)
st.pyplot(fig)
