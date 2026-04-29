import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
import os

from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("📊 Retail Sales Dashboard (SQL + RFM + ML)")

# 🔹 MySQL Connection (optional)
def get_connection():
    return mysql.connector.connect(
        host="localhost",   # change if using cloud DB
        user="root",
        password="your_password",
        database="retail_db"
    )

# 🔹 Load Data (SAFE VERSION)
@st.cache_data
def load_data():
    # Try SQL
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM sales_data", conn)
        conn.close()
        st.success("✅ Data loaded from SQL")
        return df
    except:
        st.warning("⚠️ SQL not connected, using CSV...")

    # Try CSV (ROOT FOLDER)
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        st.success("✅ Data loaded from CSV")
        return df

    # Final fallback
    st.error("❌ data.csv file not found!")
    return pd.DataFrame()

df = load_data()

# Stop if no data
if df.empty:
    st.stop()

# 🔹 Preprocessing
df.columns = df.columns.str.lower().str.replace(' ', '_')
df["orderdate"] = pd.to_datetime(df["orderdate"])
df["month"] = df["orderdate"].dt.strftime("%b")

# 🔹 Sidebar Filters
st.sidebar.header("🔍 Filters")

month = st.sidebar.multiselect("Month", df["month"].unique(), default=df["month"].unique())
country = st.sidebar.multiselect("Country", df["country"].unique(), default=df["country"].unique())
productline = st.sidebar.multiselect("Product Line", df["productline"].unique(), default=df["productline"].unique())

df = df[
    (df["month"].isin(month)) &
    (df["country"].isin(country)) &
    (df["productline"].isin(productline))
]

# 🔹 KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", df["ordernumber"].nunique())
col2.metric("Total Sales", f"{df['sales'].sum():,.2f}")
col3.metric("Total Quantity", int(df["quantityordered"].sum()))

# 🔹 Charts
col4, col5 = st.columns(2)

with col4:
    st.subheader("Sales by Territory")
    fig1 = px.pie(df, names="territory", values="sales", hole=0.5)
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("Top Customers")
    cust = df.groupby("customername")["sales"].sum().reset_index().sort_values(by="sales", ascending=False).head(10)
    fig2 = px.bar(cust, x="customername", y="sales")
    st.plotly_chart(fig2, use_container_width=True)

# 🔹 Row 2
col6, col7 = st.columns(2)

with col6:
    st.subheader("Sales by Product Line")
    prod = df.groupby("productline")["sales"].sum().reset_index()
    fig3 = px.bar(prod, x="productline", y="sales", color="productline")
    st.plotly_chart(fig3, use_container_width=True)

with col7:
    st.subheader("Sales Trend")
    trend = df.groupby("orderdate")["sales"].sum().reset_index()
    fig4 = px.line(trend, x="orderdate", y="sales")
    st.plotly_chart(fig4, use_container_width=True)

# 🔹 Map
st.subheader("🌍 Sales by Country")

fig5 = px.scatter_geo(
    df,
    locations="country",
    locationmode="country names",
    size="sales"
)

st.plotly_chart(fig5, use_container_width=True)

# 🔥 🔹 RFM Analysis
st.subheader("📊 RFM Analysis")

today = df["orderdate"].max()

rfm = df.groupby("customername").agg({
    "orderdate": lambda x: (today - x.max()).days,
    "ordernumber": "count",
    "sales": "sum"
}).reset_index()

rfm.columns = ["customer", "recency", "frequency", "monetary"]

rfm["R"] = pd.qcut(rfm["recency"], 4, labels=[4,3,2,1])
rfm["F"] = pd.qcut(rfm["frequency"], 4, labels=[1,2,3,4])
rfm["M"] = pd.qcut(rfm["monetary"], 4, labels=[1,2,3,4])

rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)

st.dataframe(rfm)

fig6 = px.scatter(
    rfm,
    x="recency",
    y="monetary",
    size="frequency",
    color="RFM_Score"
)

st.plotly_chart(fig6, use_container_width=True)

# 🔥 🔹 ML Prediction
st.subheader("📈 Sales Prediction (ML)")

df_ml = df.sort_values("orderdate").copy()
df_ml["date_ordinal"] = df_ml["orderdate"].map(pd.Timestamp.toordinal)

X = df_ml[["date_ordinal"]]
y = df_ml["sales"]

model = LinearRegression()
model.fit(X, y)

future_days = st.slider("Select Days to Predict", 5, 30, 10)

last_date = df_ml["orderdate"].max()
future_dates = pd.date_range(last_date, periods=future_days)

future_ordinal = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1,1)
predictions = model.predict(future_ordinal)

pred_df = pd.DataFrame({
    "date": future_dates,
    "predicted_sales": predictions
})

fig_pred = px.line(pred_df, x="date", y="predicted_sales", title="Future Sales Prediction")

st.plotly_chart(fig_pred, use_container_width=True)
