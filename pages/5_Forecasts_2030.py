import streamlit as st
import pandas as pd
import plotly.express as px
from utils.io_helpers import path_in_data, load_csv_safe, has_forecasts

st.set_page_config(page_title="2030 Scenario Forecasting", page_icon="🔮", layout="wide")

st.title("🔮 2030 Scenario Forecasting")


if not has_forecasts():
    st.warning("⚠️ No forecast files found in /data/. Run tren_modeling_forecasting.py first.")
    st.stop()

scenarios = {
    "Baseline": "forecast_2030_baseline.csv",
    "Social Spending": "forecast_2030_social_spending.csv",
    "Trade Diversification": "forecast_2030_trade_diversification.csv",
    "Global Crisis": "forecast_2030_global_crisis.csv"
}

scenario = st.selectbox("Select scenario", list(scenarios.keys()))
df = load_csv_safe(path_in_data(scenarios[scenario]))

metric = st.selectbox("Select metric to visualize", 
                      ["gdp_growth_2030", "poverty_2030", "resilience_2030"])

st.subheader(f"🌍 Global Map of {metric} – {scenario}")
fig = px.choropleth(df, locations="ISO3", color=metric, hover_name="ISO3",
                    projection="natural earth", color_continuous_scale="RdYlGn")
fig.update_layout(height=500, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig, use_container_width=True)

st.subheader(f"📊 Country ranking by {metric}")
top = df.sort_values(metric, ascending=False).head(15)
fig_bar = px.bar(top, x="ISO3", y=metric, color=metric, 
                 color_continuous_scale="RdYlGn",
                 title=f"Top 15 countries – {scenario}")
fig_bar.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📑 Forecast data")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download this forecast as CSV",
    data=csv,
    file_name=f"forecast_2030_{scenario.lower().replace(' ', '_')}.csv",
    mime="text/csv",
)
