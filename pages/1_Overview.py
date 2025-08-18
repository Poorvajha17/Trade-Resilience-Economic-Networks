import streamlit as st
import pandas as pd
from utils.io_helpers import path_in_data, load_csv_safe

st.title("📁 Overview")

df = load_csv_safe(path_in_data("final_cleaned_dataset.csv"))
if df is None:
    st.error("final_cleaned_datasetf.csv not found in /data/")
    st.stop()

st.subheader("Dataset Preview")
st.dataframe(df.head(50), use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries", df["ISO3"].nunique())
c2.metric("Years", f"{int(df['Year'].min())}-{int(df['Year'].max())}")
c3.metric("Rows", len(df))
c4.metric("Columns", df.shape[1])

# Download option
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Dataset",
                       data=csv,
                       file_name="final_cleaned_dataset.csv",
                       mime="text/csv")



