import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("📊 Retail Sales Dashboard (SQL + RFM Analysis)")

# 🔹 MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sumo$%23",
        database="retail_db"
    )

# 🔹 Load Data
@st.cache_data
def load_data():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM sales_data", conn)
        conn.close()
    except:
        df = pd.read_csv("data/data.csv")  # fallback

    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df["orderdate"] = pd.to_datetime(df["orderdate"])
    df["month"] = df["orderdate"].dt.strftime("%b")

    return df

df = load_data()

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
