import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🛠️ Feature Engineering")

st.subheader("Dataset Preview")

@st.cache_data
def load_data():
    df = pd.read_csv("data_for_st/final_with_indexes.csv")  
    return df

try:
    df = load_data()
    st.dataframe(df.head(50), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Feature Engineered Data",
                       data=csv,
                       file_name="final_with_indexes.csv",
                       mime="text/csv")

    st.subheader("Feature Engineered Dataset Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Countries", df["ISO3"].nunique())
    c2.metric("Years", f"{int(df['Year'].min())}-{int(df['Year'].max())}")
    c3.metric("Rows", len(df))
    c4.metric("Columns", df.shape[1])

    st.subheader("Feature Distributions")
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    if len(num_cols) > 0:
        selected_col = st.selectbox("Select a feature to visualize:", num_cols)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df[selected_col], kde=True, bins=30, ax=ax, color="skyblue")
        ax.set_title(f"Distribution of {selected_col}")
        st.pyplot(fig)
    else:
        st.info("No numeric columns found for distribution plots.")

    st.subheader("📑 Summary Statistics")
    st.dataframe(df.describe().T, use_container_width=True)

except FileNotFoundError:
    st.warning("Feature engineered dataset not found. Please generate it first.")
