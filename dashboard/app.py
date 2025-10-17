import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime

# ----------------------------------
# 🧠 Database Connection
# ----------------------------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="fraudshield",
        user="admin",
        password="admin123"
    )

# ----------------------------------
# ⚙️ Streamlit Setup
# ----------------------------------
st.set_page_config(page_title="FraudShield Dashboard", layout="wide")
st.title("🚨 FraudShield Real-Time Dashboard")

st.sidebar.header("⚙️ Settings")

# ----------------------------------
# 🧭 Refresh Handling
# ----------------------------------
if "last_refreshed" not in st.session_state:
    st.session_state["last_refreshed"] = None
if "data" not in st.session_state:
    st.session_state["data"] = None

# Manual refresh
if st.sidebar.button("🔄 Refresh Data"):
    st.session_state["data"] = None
    st.session_state["last_refreshed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.toast("✅ Data refresh triggered! Rebuilding dashboard...")

# Display last refreshed time
if st.session_state["last_refreshed"]:
    st.sidebar.caption(f"🕒 Last refreshed: {st.session_state['last_refreshed']}")
else:
    st.sidebar.caption("🕒 No refresh yet (first load).")

# ----------------------------------
# 🗂️ Load Data (Cached)
# ----------------------------------
@st.cache_data
def load_data():
    with get_connection() as conn:
        query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 300;"
        df = pd.read_sql(query, conn)  # type: ignore
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# Load from session or cache
if st.session_state["data"] is None:
    st.session_state["data"] = load_data()

df = st.session_state["data"]

if df.empty:
    st.warning("No transactions found in database.")
    st.stop()

# ----------------------------------
# 🔍 Sidebar Filters
# ----------------------------------
st.sidebar.subheader("Filters")
status_filter = st.sidebar.multiselect("Status", df["status"].unique(), default=df["status"].unique())
location_filter = st.sidebar.multiselect("Location", df["location"].unique(), default=df["location"].unique())
card_filter = st.sidebar.multiselect("Card Type", df["card_type"].unique(), default=df["card_type"].unique())

df = df[
    (df["status"].isin(status_filter)) &
    (df["location"].isin(location_filter)) &
    (df["card_type"].isin(card_filter))
]

# ----------------------------------
# KPI Metrics
# ----------------------------------
col1, col2, col3, col4 = st.columns(4)
total_txn = len(df)
suspicious_txn = df["is_suspicious"].sum()
normal_txn = total_txn - suspicious_txn
suspicious_pct = round((suspicious_txn / total_txn) * 100, 2) if total_txn > 0 else 0
avg_amount = round(df["amount"].mean(), 2) if total_txn > 0 else 0

col1.metric("Total Transactions", total_txn)
col2.metric("Suspicious Transactions", suspicious_txn)
col3.metric("Suspicious %", f"{suspicious_pct}%")
col4.metric("Avg Amount ($)", avg_amount)
st.markdown("---")

# ====================================================
# Lazy Loading Sections
# ====================================================

# --- Section 1: General Insights ---
with st.expander("📊 General Transaction Insights", expanded=True):
    c1, c2, c3 = st.columns(3)
    fig1 = px.pie(
        names=["Suspicious", "Normal"],
        values=[suspicious_txn, normal_txn],
        color=["Suspicious", "Normal"],
        color_discrete_map={"Suspicious": "red", "Normal": "green"},
        title="Suspicious vs Normal Transactions"
    )
    c1.plotly_chart(fig1, use_container_width=True)

    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["status", "count"]
    fig2 = px.bar(status_count, x="status", y="count", color="status", title="Transaction Status Breakdown")
    c2.plotly_chart(fig2, use_container_width=True)

    avg_amount_status = df.groupby("status")["amount"].mean().reset_index()
    fig3 = px.bar(avg_amount_status, x="status", y="amount", color="status", title="Average Amount by Status")
    c3.plotly_chart(fig3, use_container_width=True)

# --- Section 2: Transaction Trends ---
with st.expander("📈 Transaction Trends"):
    c4, c5 = st.columns(2)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Group by month
    df_time = (
        df.groupby(pd.Grouper(key="timestamp", freq="M"))
        .size()
        .reset_index(name="count")
    )
    df_amount_time = (
        df.groupby(pd.Grouper(key="timestamp", freq="M"))["amount"]
        .mean()
        .reset_index()
    )

    # Format month labels
    df_time["month_label"] = df_time["timestamp"].dt.strftime("%b %Y")  # Jan 2025, Feb 2025, etc.
    df_amount_time["month_label"] = df_amount_time["timestamp"].dt.strftime("%b %Y")
    x_col = "month_label"
    x_title = "Month"

    # --- Charts ---
    fig4 = px.line(
        df_time,
        x=x_col,
        y="count",
        title="Transaction Volume Over Time (Monthly)",
        labels={x_col: x_title, "count": "Number of Transactions"}
    )
    fig4.update_xaxes(tickangle=45)

    fig5 = px.line(
        df_amount_time,
        x=x_col,
        y="amount",
        title="Average Transaction Amount (Monthly)",
        labels={x_col: x_title, "amount": "Average Amount ($)"}
    )
    fig5.update_xaxes(tickangle=45)

    c4.plotly_chart(fig4, use_container_width=True)
    c5.plotly_chart(fig5, use_container_width=True)


# --- Section 3: Location Insights ---
with st.expander("🌍 Location Insights"):
    c6, c7 = st.columns(2)
    top_locations = df["location"].value_counts().nlargest(10).index
    df_top = df[df["location"].isin(top_locations)]

    fig6 = px.histogram(df_top, x="location", color="is_suspicious", title="Top 10 Locations (Suspicious Highlighted)")
    c6.plotly_chart(fig6, use_container_width=True)

    fig7 = px.box(df_top, x="location", y="amount", color="is_suspicious", title="Amount Distribution by Top 10 Locations")
    c7.plotly_chart(fig7, use_container_width=True)

# --- Section 4: Suspicious Customers ---
with st.expander("🔥 Top Suspicious Customers"):
    if "customer_id" in df.columns and "customer_name" in df.columns:
        suspicious_leaderboard = (
            df[df["is_suspicious"] == True]
            .groupby(["customer_id", "customer_name"])
            .agg(
                suspicious_count=("is_suspicious", "sum"),
                total_amount=("amount", "sum"),
                last_seen=("timestamp", "max")
            )
            .reset_index()
            .sort_values("total_amount", ascending=False)
            .head(10)
        )

        fig8 = px.bar(
            suspicious_leaderboard,
            x="customer_name",  # use names for the x-axis
            y="suspicious_count",
            color="total_amount",
            title="Top 10 Suspicious Customers",
            color_continuous_scale="Reds",
            hover_data=["customer_id", "total_amount", "last_seen"]
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.dataframe(suspicious_leaderboard, use_container_width=True)
    else:
        st.info("⚠️ 'customer_id' or 'customer_name' column missing — cannot generate leaderboard.")

# --- Section 5: Fraud Heatmap ---
with st.expander("🕒 Fraud Activity Heatmap"):
    df["month"] = df["timestamp"].dt.strftime("%b %Y")  # Jan 2025, Feb 2025, etc.
    
    heatmap = df[df["is_suspicious"]].groupby("month").size().reset_index(name="count").sort_values("count", ascending=False)

    fig9 = px.bar(
        heatmap,
        x="month",
        y="count",
        title="Suspicious Activity by Month",
        labels={"month": "Month", "count": "Number of Suspicious Transactions"},
        color="count",
        color_continuous_scale="Reds"
    )
    fig9.update_xaxes(tickangle=45)
    st.plotly_chart(fig9, use_container_width=True)

# --- Section 6: Latest Transactions ---
with st.expander("🚨 Latest Transactions"):
    recent_suspicious = (
        df[df["is_suspicious"] == True]
        .sort_values("timestamp", ascending=False)
        .head(10)[["timestamp", "customer_id", "amount", "location"]]
    )
    st.write("### 🚨 Latest Suspicious Transactions")
    st.dataframe(recent_suspicious, use_container_width=True)

    st.write("### 📋 Recent Transactions (Top 10)")
    df_preview = df.head(10).copy()
    df_preview["is_suspicious"] = df_preview["is_suspicious"].astype(bool)
    st.dataframe(df_preview, use_container_width=True)
