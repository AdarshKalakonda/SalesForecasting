import streamlit as st
import pandas as pd
from sqlalchemy import text
from db import get_engine
from charts import plot_forecast, plot_rolling_avg, plot_metrics_table

st.set_page_config(page_title="Sales Forecasting Dashboard", layout="wide")
st.title("Sales Forecasting Dashboard")

engine = get_engine()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    store_options = pd.read_sql(
        text("SELECT DISTINCT store_nbr FROM mart.forecasts ORDER BY store_nbr"),
        engine,
    )['store_nbr'].tolist()
    store_nbr = st.selectbox("Store Number", store_options, index=store_options.index(44) if 44 in store_options else 0)

    horizon = st.select_slider("Forecast Horizon (days)", options=[30, 60, 90], value=90)

    date_bounds = pd.read_sql(
        text("SELECT MIN(date) AS min_d, MAX(date) AS max_d FROM mart.daily_sales WHERE store_nbr = :s"),
        engine,
        params={"s": store_nbr},
    ).iloc[0]
    date_range = st.date_input(
        "Date Range",
        value=(date_bounds['min_d'], date_bounds['max_d']),
        min_value=date_bounds['min_d'],
        max_value=date_bounds['max_d'],
    )

start_date, end_date = (date_range[0], date_range[1]) if len(date_range) == 2 else (date_bounds['min_d'], date_bounds['max_d'])

# ── Data queries ─────────────────────────────────────────────────────────────
actuals = pd.read_sql(
    text("""
        SELECT date, SUM(total_sales) AS total_sales, AVG(rolling_30d_avg) AS rolling_30d_avg
        FROM mart.daily_sales
        WHERE store_nbr = :s AND date BETWEEN :start AND :end
        GROUP BY date
        ORDER BY date
    """),
    engine,
    params={"s": store_nbr, "start": start_date, "end": end_date},
)

forecasts = pd.read_sql(
    text("""
        SELECT forecast_date, predicted_sales, lower_ci, upper_ci
        FROM mart.forecasts
        WHERE store_nbr = :s
        ORDER BY forecast_date
    """),
    engine,
    params={"s": store_nbr},
)

top_stores = pd.read_sql(
    text("""
        SELECT store_nbr, city, state,
               TO_CHAR(total_revenue, 'FM$999,999,999.00') AS total_revenue,
               rank_overall
        FROM mart.store_performance
        ORDER BY rank_overall
        LIMIT 5
    """),
    engine,
)

# ── Metric cards ─────────────────────────────────────────────────────────────
total_forecast = pd.read_sql(
    text("SELECT COALESCE(SUM(predicted_sales), 0) AS total FROM mart.forecasts WHERE store_nbr = :s"),
    engine,
    params={"s": store_nbr},
).iloc[0]['total']
model_version  = "sarima_v1"
mape_val       = 8.58

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Forecasted Revenue", f"${total_forecast:,.0f}")
col2.metric("MAPE", f"{mape_val}%")
col3.metric("Model Version", model_version)
col4.metric("Forecast Horizon", f"{horizon} days")

st.divider()

# ── Charts ───────────────────────────────────────────────────────────────────
if forecasts.empty:
    st.warning("No forecast data found for this store. Run models/write_forecasts.py first.")
else:
    st.plotly_chart(plot_forecast(actuals, forecasts), use_container_width=True)

st.plotly_chart(plot_rolling_avg(actuals), use_container_width=True)

st.subheader("Model Accuracy")
st.plotly_chart(plot_metrics_table(mae=4178.35, rmse=5519.42, mape=mape_val), use_container_width=True)

st.subheader("Top 5 Stores by Revenue")
st.dataframe(
    top_stores.rename(columns={
        'store_nbr': 'Store', 'city': 'City', 'state': 'State',
        'total_revenue': 'Total Revenue', 'rank_overall': 'Rank',
    }),
    use_container_width=True,
    hide_index=True,
)
